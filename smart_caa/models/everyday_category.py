from django.db import models
from .base import BaseModel


class EverydayCategory(BaseModel):

    name = models.CharField(
        max_length=100,
        verbose_name="Nome da categoria",
        help_text="Nome da categoria do cotidiano",
        unique=True
    )
    
    class Meta:
        verbose_name = "Categoria do Cotidiano"
        verbose_name_plural = "Categorias do Cotidiano"
        ordering = ['name']
    
    def __str__(self):
        return self.name
