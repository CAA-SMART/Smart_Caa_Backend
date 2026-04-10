from django.db import models
from .base import BaseModel
from .history import History
from .person import Person

class Attachment(BaseModel):
    """
    Model to store patient attachments (documents, images, PDFs)
    """
    name = models.CharField(
        max_length=255,
        verbose_name="Nome do Anexo",
        help_text="Nome descritivo do anexo"
    )
    file = models.FileField(
        upload_to="anexos/",
        verbose_name="Arquivo do Anexo",
        help_text="Arquivo anexado (imagem, PDF, etc.)"
    )
    patient = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name="attachments",
        verbose_name="Paciente",
        help_text="Paciente ao qual o anexo pertence",
        limit_choices_to={'is_patient': True}
    )
    history = models.ForeignKey(
        History,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="attachments",
        verbose_name="Histórico",
        help_text="Histórico ao qual o anexo pode estar vinculado"
    )
    
    class Meta:
        verbose_name = "Anexo"
        verbose_name_plural = "Anexos"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.patient.name}"
