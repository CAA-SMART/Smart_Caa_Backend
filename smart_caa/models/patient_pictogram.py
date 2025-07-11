from django.db import models
from .base import BaseModel


class PatientPictogram(BaseModel):
    """
    Modelo para relacionar pacientes com pictogramas.
    Permite que cada paciente tenha seus próprios pictogramas personalizados.
    """
    
    patient = models.ForeignKey(
        'Person',
        on_delete=models.CASCADE,
        related_name='patient_pictograms',
        limit_choices_to={'is_patient': True},
        verbose_name="Paciente",
        help_text="Paciente ao qual o pictograma será vinculado"
    )
    
    pictogram = models.ForeignKey(
        'Pictogram',
        on_delete=models.CASCADE,
        related_name='patient_pictograms',
        verbose_name="Pictograma",
        help_text="Pictograma vinculado ao paciente"
    )
    
    class Meta:
        verbose_name = "Pictograma do Paciente"
        verbose_name_plural = "Pictogramas dos Pacientes"
        ordering = ['patient__name', 'pictogram__name', '-created_at']
        indexes = [
            models.Index(fields=['patient', 'is_active']),
            models.Index(fields=['pictogram', 'is_active']),
            models.Index(fields=['patient', 'pictogram', 'is_active']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['patient', 'pictogram'],
                condition=models.Q(is_active=True),
                name='unique_active_patient_pictogram',
                violation_error_message='Este pictograma já está ativo para este paciente.'
            )
        ]
    
    def __str__(self):
        status = "Ativo" if self.is_active else "Inativo"
        return f"{self.patient.name} - {self.pictogram.name} ({status})"
    
    def save(self, *args, **kwargs):
        """
        Sobrescreve o save para garantir que apenas pacientes possam ter pictogramas
        """
        if not self.patient.is_patient:
            raise ValueError("Apenas pacientes podem ter pictogramas vinculados")
        super().save(*args, **kwargs)
