from smart_caa.models.base import BaseModel
from django.db import models
from .account import Account


class AccountUser(BaseModel):
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name="users",
        verbose_name="Conta",
        help_text="Conta à qual o usuário pertence"
    )
    name = models.CharField(
        max_length=100,
        verbose_name="Nome",
        help_text="Nome do usuário da conta",
        blank=False,
        null=False
    )
    cpf = models.CharField(
        max_length=14,
        verbose_name="CPF",
        help_text="CPF do usuário da conta",
        unique=True,
        blank=False,
        null=False
    )

    class Meta:
        verbose_name = "Usuário da Conta"
        verbose_name_plural = "Usuários da Conta"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.cpf})"
