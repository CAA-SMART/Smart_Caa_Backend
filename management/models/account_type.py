from smart_caa.models.base import BaseModel
from django.db import models


class AccountType(BaseModel):
    name = models.CharField(
        max_length=100,
        verbose_name="Nome",
        help_text="Nome do tipo de conta"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Descrição",
        help_text="Descrição do tipo de conta"
    )

    class Meta:
        verbose_name = "Tipo de Conta"
        verbose_name_plural = "Tipos de Conta"
        ordering = ["name"]

    def __str__(self):
        return self.name
