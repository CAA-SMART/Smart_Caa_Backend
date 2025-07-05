from django.db import models
from django.contrib.auth.models import User


class BaseModel(models.Model):

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Criado por",
        help_text="Usuário que criou o registro"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de criação"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Data de atualização"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Ativo",
        help_text="Indica se o registro está ativo no sistema"
    )
    
    inactivated_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data de inativação",
        help_text="Data em que o registro foi inativado"
    )
    
    inactivated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_inactivated",
        verbose_name="Inativado por",
        help_text="Usuário que inativou o registro"
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']
