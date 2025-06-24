from django.db import models
from .base import BaseModel
from .everyday_category import EverydayCategory


class Pictogram(BaseModel):
    
    name = models.CharField(
        max_length=100,
        verbose_name="Nome do pictograma",
        help_text="Nome descritivo do pictograma"
    )
    
    category = models.ForeignKey(
        EverydayCategory,
        on_delete=models.CASCADE,
        related_name='pictograms',
        verbose_name="Categoria",
        help_text="Categoria do cotidiano à qual o pictograma pertence"
    )
    
    image = models.ImageField(
        upload_to='pictograms/images/',
        verbose_name="Imagem do pictograma",
        help_text="Arquivo de imagem do pictograma (PNG, JPG, etc.)"
    )
    
    audio = models.FileField(
        upload_to='pictograms/audio/',
        blank=True,
        null=True,
        verbose_name="Áudio do pictograma",
        help_text="Arquivo de áudio com a pronúncia do pictograma (MP3, WAV, etc.)"
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Descrição",
        help_text="Descrição adicional do pictograma"
    )
    
    class Meta:
        verbose_name = "Pictograma"
        verbose_name_plural = "Pictogramas"
        ordering = ['name']
        unique_together = ['name', 'category']  # Nome único por categoria
    
    def __str__(self):
        return f"{self.name} ({self.category.name})"
