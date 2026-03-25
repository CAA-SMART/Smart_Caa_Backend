from django.db import models

from .base import BaseModel
from .person import Person


class History(BaseModel):
    caregiver = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name='caregiver_histories',
        limit_choices_to={'is_caregiver': True},
        verbose_name="Cuidador",
        help_text="Pessoa que é cuidador no histórico"
    )

    patient = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name='patient_histories',
        limit_choices_to={'is_patient': True},
        verbose_name="Paciente",
        help_text="Pessoa que é paciente no histórico"
    )

    description = models.TextField(
        verbose_name="Descrição",
        help_text="Descrição do histórico"
    )

    class Meta:
        verbose_name = "Histórico"
        verbose_name_plural = "Históricos"
        ordering = ['-created_at', 'patient__name', 'caregiver__name']

    def __str__(self):
        return f"{self.patient.name} - {self.caregiver.name}"
