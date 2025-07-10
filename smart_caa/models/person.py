from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .base import BaseModel


class Person(BaseModel):
    
    # Relacionamento com usuário do sistema
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name="Usuário do Sistema",
        help_text="Usuário associado a esta pessoa para login no sistema",
        related_name='person'
    )
    
    # Dados básicos (obrigatórios)
    name = models.CharField(        max_length=200,
        verbose_name="Nome completo",
        help_text="Nome completo da pessoa"
    )
    
    cpf = models.CharField(
        max_length=14,
        unique=True,
        verbose_name="CPF",
        help_text="CPF da pessoa (formato: 000.000.000-00)"
    )
    
    email = models.EmailField(
        unique=True,
        verbose_name="E-mail",
        help_text="Endereço de e-mail da pessoa"
    )
    
    phone = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Contato",
        help_text="Número de telefone ou celular"
    )
    
    cid = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="CID",
        help_text="Classificação Internacional de Doenças (formato: A00-B99, C00-D48)"
    )
    
    # Profissão
    profession = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Profissão",
        help_text="Profissão ou ocupação da pessoa"
    )
    
    # Address data
    postal_code = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name="CEP",
        help_text="Código de Endereçamento Postal (formato: 00000-000)"
    )
    
    state = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        verbose_name="UF",
        help_text="Unidade Federativa (Estado)"
    )
    
    city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Cidade",
        help_text="Nome da cidade"
    )
    
    district = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Bairro",
        help_text="Nome do bairro"
    )
    
    street = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Logradouro",
        help_text="Rua, avenida, travessa, etc."
    )
    
    number = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name="Número",
        help_text="Número da residência/estabelecimento"
    )
    
    complement = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Complemento",
        help_text="Apartamento, bloco, casa, etc."
    )

    # Tipos de pessoa (pode ser ambos)
    is_patient = models.BooleanField(
        default=False,
        verbose_name="É Paciente",
        help_text="Indica se a pessoa é um paciente"
    )
    
    is_caregiver = models.BooleanField(
        default=False,
        verbose_name="É Cuidador",
        help_text="Indica se a pessoa é um cuidador"
    )
    
    # Campos específicos do paciente (só preenchidos se is_patient=True)
    colors = models.TextField(
        blank=True,
        null=True,
        verbose_name="Cores",
        help_text="Cores que o paciente gosta ou tem preferência"
    )
    
    sounds = models.TextField(
        blank=True,
        null=True,
        verbose_name="Toques",
        help_text="Sons, toques ou músicas que o paciente aprecia"
    )
    
    smells = models.TextField(
        blank=True,
        null=True,
        verbose_name="Cheiros",
        help_text="Cheiros que o paciente gosta ou reconhece"
    )
    
    hobbies = models.TextField(
        blank=True,
        null=True,
        verbose_name="Hobbies",
        help_text="Atividades e hobbies do paciente"
    )
    
    class Meta:
        verbose_name = "Pessoa"
        verbose_name_plural = "Pessoas"
        ordering = ['name']
    
    def __str__(self):
        types = []
        if self.is_patient:
            types.append("Paciente")
        if self.is_caregiver:
            types.append("Cuidador")
        
        type_str = " | ".join(types)
        return f"{self.name} ({type_str})"
    
    def clean(self):
        """Validações customizadas"""
        super().clean()
        
        # Valida se pelo menos um tipo foi selecionado
        if not self.is_patient and not self.is_caregiver:
            raise ValidationError(
                "A pessoa deve ser marcada como Paciente, Cuidador ou ambos."
            )
    
    def save(self, *args, **kwargs):
        """Override do save para executar validações"""
        self.full_clean()
        super().save(*args, **kwargs)
