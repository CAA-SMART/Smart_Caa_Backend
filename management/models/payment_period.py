from smart_caa.models.base import BaseModel
from django.db import models

class PaymentPeriod(BaseModel):
    name = models.CharField(
        max_length=100,
        verbose_name="Nome",
        help_text="Nome do período de pagamento"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Descrição",
        help_text="Descrição do período de pagamento"
    )

    class Meta:
        verbose_name = "Período de Pagamento"
        verbose_name_plural = "Períodos de Pagamento"
        ordering = ["name"]

    def __str__(self):
        return self.name
