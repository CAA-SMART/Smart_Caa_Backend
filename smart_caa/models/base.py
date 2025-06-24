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
    
    class Meta:
        abstract = True
        ordering = ['-created_at']
