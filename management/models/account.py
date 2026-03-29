from smart_caa.models.base import BaseModel
from django.db import models
from .account_type import AccountType
from .payment_period import PaymentPeriod
from .payment_plan import PaymentPlan

class Account(BaseModel):
    name = models.CharField(
        max_length=100,
        verbose_name="Nome da conta",
        help_text="Nome da conta"
    )
    account_type = models.ForeignKey(
        AccountType,
        on_delete=models.PROTECT,
        verbose_name="Tipo de Conta",
        help_text="Tipo de conta associada"
    )
    payment_period = models.ForeignKey(
        PaymentPeriod,
        on_delete=models.PROTECT,
        verbose_name="Período de Pagamento",
        help_text="Período de pagamento da conta"
    )
    payment_plan = models.ForeignKey(
        PaymentPlan,
        on_delete=models.PROTECT,
        verbose_name="Plano de Pagamento",
        help_text="Plano de pagamento da conta"
    )
    due_day = models.PositiveSmallIntegerField(
        verbose_name="Dia do vencimento",
        help_text="Dia do mês para vencimento da cobrança"
    )
    start_date = models.DateField(
        verbose_name="Data de início",
        help_text="Data de início da conta"
    )
    first_due_date = models.DateField(
        verbose_name="Data do 1º vencimento",
        help_text="Data do primeiro vencimento da conta"
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data fim vigência",
        help_text="Data de término da vigência da conta"
    )
    responsible_name = models.CharField(
        max_length=100,
        verbose_name="Nome do responsável",
        help_text="Nome do responsável pela conta"
    )
    responsible_phone = models.CharField(
        max_length=20,
        verbose_name="Celular do responsável",
        help_text="Celular do responsável pela conta"
    )
    responsible_email = models.EmailField(
        verbose_name="E-mail do responsável",
        help_text="E-mail do responsável pela conta"
    )
    auto_renewal = models.BooleanField(
        default=False,
        verbose_name="Renovação automática",
        help_text="Se a conta possui renovação automática"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Descrição",
        help_text="Descrição adicional da conta"
    )

    class Meta:
        verbose_name = "Conta"
        verbose_name_plural = "Contas"
        ordering = ["name"]

    def __str__(self):
        return self.name
