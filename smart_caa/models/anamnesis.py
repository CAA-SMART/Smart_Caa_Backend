from django.db import models
from .base import BaseModel
from .person import Person


class Anamnesis(BaseModel):
    """
    Modelo para armazenar informações de anamnese de pacientes
    """
    
    # Relacionamentos
    patient = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name="anamneses",
        verbose_name="Paciente",
        help_text="Paciente para quem a anamnese foi criada",
        limit_choices_to={'is_patient': True}
    )
    
    caregiver = models.ForeignKey(
        Person,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_anamneses",
        verbose_name="Cuidador",
        help_text="Cuidador que cadastrou a anamnese",
        limit_choices_to={'is_caregiver': True}
    )

    # Health History / Histórico de saúde
    main_diagnosis = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Diagnóstico Principal",
        help_text="Diagnóstico médico principal do paciente"
    )
    
    associated_conditions = models.TextField(
        blank=True,
        null=True,
        verbose_name="Condições Associadas",
        help_text="Outras condições médicas ou comorbidades"
    )
    
    allergies = models.TextField(
        blank=True,
        null=True,
        verbose_name="Alergias",
        help_text="Alergias conhecidas do paciente"
    )
    
    medications = models.TextField(
        blank=True,
        null=True,
        verbose_name="Medicações",
        help_text="Medicamentos em uso atual"
    )

    # Communication / Comunicação
    communication_methods = models.TextField(
        blank=True,
        null=True,
        verbose_name="Formas de Comunicação",
        help_text="Métodos de comunicação utilizados pelo paciente"
    )
    
    spoken_words = models.TextField(
        blank=True,
        null=True,
        verbose_name="Palavras Faladas",
        help_text="Palavras que o paciente consegue falar ou entender"
    )
    
    preferred_pictograms = models.TextField(
        blank=True,
        null=True,
        verbose_name="Pictogramas Preferidos",
        help_text="Pictogramas ou símbolos que o paciente prefere ou reconhece melhor"
    )

    # Feeding / Alimentação
    dietary_restrictions = models.TextField(
        blank=True,
        null=True,
        verbose_name="Restrições Alimentares",
        help_text="Alimentos que devem ser evitados ou restrições específicas"
    )
    
    food_preferences = models.TextField(
        blank=True,
        null=True,
        verbose_name="Preferências Alimentares",
        help_text="Alimentos favoritos ou preferências do paciente"
    )
    
    feeding_difficulties = models.TextField(
        blank=True,
        null=True,
        verbose_name="Dificuldades na Alimentação",
        help_text="Problemas ou dificuldades relacionadas à alimentação"
    )

    # Behavioral Aspects / Aspectos comportamentais
    needs_expression = models.TextField(
        blank=True,
        null=True,
        verbose_name="Expressão de Necessidades",
        help_text="Como o paciente expressa suas necessidades e desejos"
    )
    
    frustration_reactions = models.TextField(
        blank=True,
        null=True,
        verbose_name="Reações à Frustração",
        help_text="Como o paciente reage quando frustrado ou irritado"
    )

    # General Observations / Observações gerais
    general_observations = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observações Gerais",
        help_text="Observações adicionais importantes sobre o paciente"
    )

    class Meta:
        verbose_name = "Anamnese"
        verbose_name_plural = "Anamneses"
        ordering = ['-created_at']
        unique_together = ['patient', 'caregiver']  # Um cuidador pode ter apenas uma anamnese por paciente

    def __str__(self):
        return f"Anamnese de {self.patient.name} por {self.caregiver.name if self.caregiver else 'Não informado'}"

    def clean(self):
        """Validações customizadas"""
        super().clean()
        
        # Valida se o paciente é realmente um paciente
        if self.patient and not self.patient.is_patient:
            from django.core.exceptions import ValidationError
            raise ValidationError({
                'patient': 'A pessoa selecionada deve ser marcada como paciente.'
            })
        
        # Valida se o cuidador é realmente um cuidador
        if self.caregiver and not self.caregiver.is_caregiver:
            from django.core.exceptions import ValidationError
            raise ValidationError({
                'caregiver': 'A pessoa selecionada deve ser marcada como cuidador.'
            })

    def save(self, *args, **kwargs):
        """Override do save para executar validações"""
        self.full_clean()
        super().save(*args, **kwargs)
