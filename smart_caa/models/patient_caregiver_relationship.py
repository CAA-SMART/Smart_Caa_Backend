from django.db import models
from django.core.exceptions import ValidationError
from .base import BaseModel
from .person import Person


class PatientCaregiverRelationship(BaseModel):
    """
    Modelo para relacionamento entre Paciente e Cuidador
    """
    
    # Tipos de vínculo
    RELATIONSHIP_TYPES = [
        ('FAMILY', 'Familiar'),
        ('PROFESSIONAL', 'Profissional'),
        ('FRIEND', 'Amigo'),
        ('VOLUNTEER', 'Voluntário'),
        ('OTHER', 'Outros'),
    ]
    
    patient = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name='caregiver_relationships',
        limit_choices_to={'is_patient': True},
        verbose_name="Paciente",
        help_text="Pessoa que é paciente neste relacionamento"
    )
    
    caregiver = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name='patient_relationships',
        limit_choices_to={'is_caregiver': True},
        verbose_name="Cuidador",
        help_text="Pessoa que é cuidador neste relacionamento"
    )
    
    relationship_type = models.CharField(
        max_length=20,
        choices=RELATIONSHIP_TYPES,
        verbose_name="Tipo de Vínculo",
        help_text="Tipo de relacionamento entre paciente e cuidador"
    )
    
    start_date = models.DateField(
        verbose_name="Data de Início",
        help_text="Data de início do vínculo entre paciente e cuidador"
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observações",
        help_text="Observações sobre o relacionamento"
    )
    
    class Meta:
        verbose_name = "Relacionamento Paciente-Cuidador"
        verbose_name_plural = "Relacionamentos Paciente-Cuidador"
        # Removido unique_together para permitir vínculos históricos
        ordering = ['-start_date', 'patient__name', 'caregiver__name']
    
    def __str__(self):
        return f"{self.patient.name} - {self.caregiver.name} ({self.get_relationship_type_display()})"
    
    def clean(self):
        """Validações customizadas"""
        super().clean()
        
        # Valida se o paciente é realmente marcado como paciente
        if self.patient and not self.patient.is_patient:
            raise ValidationError({
                'patient': 'A pessoa selecionada deve estar marcada como paciente.'
            })
        
        # Valida se o cuidador é realmente marcado como cuidador
        if self.caregiver and not self.caregiver.is_caregiver:
            raise ValidationError({
                'caregiver': 'A pessoa selecionada deve estar marcada como cuidador.'
            })
        
        # Valida se não é a mesma pessoa
        if self.patient and self.caregiver and self.patient.id == self.caregiver.id:
            raise ValidationError(
                'Uma pessoa não pode ser paciente e cuidador de si mesma.'
            )
        
        # Valida se não existe outro vínculo ativo entre as mesmas pessoas
        if self.patient and self.caregiver and self.is_active:
            existing_active = PatientCaregiverRelationship.objects.filter(
                patient=self.patient,
                caregiver=self.caregiver,
                is_active=True,
                inactivated_at__isnull=True  # Garante que não foi inativado
            )
            
            # Se estamos editando um registro existente, excluir o próprio registro da verificação
            if self.pk:
                existing_active = existing_active.exclude(pk=self.pk)
            
            if existing_active.exists():
                existing_relationship = existing_active.first()
                raise ValidationError(
                    f'Já existe um vínculo ativo entre {self.patient.name} e {self.caregiver.name} '
                    f'({existing_relationship.get_relationship_type_display()}) desde {existing_relationship.start_date}. '
                    f'Inative o vínculo anterior antes de criar um novo.'
                )
    
    def save(self, *args, **kwargs):
        """Override do save para executar validações"""
        self.full_clean()
        super().save(*args, **kwargs)
    
    def inactivate(self, user=None):
        """
        Inativa o relacionamento de forma controlada
        """
        from django.utils import timezone
        
        self.is_active = False
        self.inactivated_at = timezone.now()
        if user:
            self.inactivated_by = user
        self.save()
