from smart_caa.models.base import BaseModel
from django.db import models

class PaymentPlan(BaseModel):
    name = models.CharField(
        max_length=100,
        verbose_name="Nome",
        help_text="Nome do plano de pagamento"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Descrição",
        help_text="Descrição do plano de pagamento"
    )
    user_limit = models.PositiveIntegerField(
        verbose_name="Quantidade de usuários",
        help_text="Quantidade máxima de usuários permitidos no plano",
        default=0
    )
    custom_pictograms_per_patient = models.PositiveIntegerField(
        verbose_name="Qtd. pictogramas personalizados por paciente",
        help_text="Quantidade máxima de pictogramas personalizados por paciente",
        default=0
    )
    attachments_per_patient = models.PositiveIntegerField(
        verbose_name="Qtd. anexos por paciente",
        help_text="Quantidade máxima de anexos por paciente",
        default=0
    )

    class Meta:
        verbose_name = "Plano de Pagamento"
        verbose_name_plural = "Planos de Pagamento"
        ordering = ["name"]

    def __str__(self):
        return self.name
