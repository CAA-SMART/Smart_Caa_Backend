from django.db import models
from .base import BaseModel
from .person import Person


class Anamnesis(BaseModel):
    """
    Modelo para armazenar informações de anamnese de pacientes
    """
    
    # Relacionamentos
    patient = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name="anamneses",
        verbose_name="Paciente",
        help_text="Paciente para quem a anamnese foi criada",
        limit_choices_to={'is_patient': True}
    )
    
    caregiver = models.ForeignKey(
        Person,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_anamneses",
        verbose_name="Cuidador",
        help_text="Cuidador que cadastrou a anamnese",
        limit_choices_to={'is_caregiver': True}
    )

    # Seção 1 - Dados pessoais e diagnóstico
    main_diagnosis = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Diagnóstico Principal",
        help_text="Diagnóstico principal do paciente"
    )

    associated_conditions = models.TextField(
        blank=True,
        null=True,
        verbose_name="Comorbidades / Diagnósticos Secundários",
        help_text="Comorbidades ou diagnósticos secundários relacionados ao paciente"
    )

    responsible_contact = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Contato do Responsável",
        help_text="Telefone, e-mail ou outro contato do responsável/cuidador"
    )

    reference_professional = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Profissional de Referência",
        help_text="Profissional que acompanha o paciente, como fonoaudiólogo ou terapeuta"
    )
    
    # Seção 3 - Habilidades cognitivas
    cognitive_level = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Nível Cognitivo",
        help_text="Nível cognitivo estimado do paciente"
    )

    auditory_comprehension = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name="Compreensão Auditiva",
        help_text="O quanto o paciente compreende comandos, palavras ou frases"
    )

    memory_profile = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name="Memória",
        help_text="Perfil de memória visual e/ou auditiva do paciente"
    )

    attention_duration = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Atenção / Concentração",
        help_text="Tempo ou nível de atenção/concentração do paciente"
    )

    learning_pace = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Capacidade de Aprendizado",
        help_text="Velocidade ou facilidade de aprendizado do paciente"
    )

    language_style = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Linguagem Literal ou Figurada",
        help_text="Forma predominante de compreensão da linguagem pelo paciente"
    )
    
    # Seção 4 - Comunicação atual
    functional_speech = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Possui Fala Funcional",
        help_text="Ex.: não, sim parcial ou sim completa"
    )

    speech_intelligibility = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Inteligibilidade de Fala",
        help_text="Nível de inteligibilidade da fala do paciente"
    )

    uses_gestures = models.BooleanField(
        blank=True,
        null=True,
        verbose_name="Usa Gestos",
        help_text="Indica se o paciente utiliza gestos naturais para se comunicar"
    )

    uses_signs = models.BooleanField(
        blank=True,
        null=True,
        verbose_name="Usa Sinais",
        help_text="Indica se o paciente utiliza Libras ou outro sistema de sinais"
    )

    uses_images_or_symbols = models.BooleanField(
        blank=True,
        null=True,
        verbose_name="Usa Imagens ou Símbolos",
        help_text="Indica se já utiliza comunicação por imagens, figuras ou símbolos"
    )

    preferred_symbol_systems = models.TextField(
        blank=True,
        null=True,
        verbose_name="Sistemas de Símbolos Preferidos",
        help_text="Ex.: PCS, Bliss, Arasaac, fotografias, desenhos"
    )

    symbol_comprehension = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Compreensão de Símbolos",
        help_text="Nível de compreensão dos símbolos apresentados"
    )

    communication_priorities = models.TextField(
        blank=True,
        null=True,
        verbose_name="Necessidades Comunicativas Principais",
        help_text="Principais necessidades comunicativas do paciente"
    )


    class Meta:
        verbose_name = "Anamnese"
        verbose_name_plural = "Anamneses"
        ordering = ['-created_at']
        unique_together = ['patient', 'caregiver']  # Um cuidador pode ter apenas uma anamnese por paciente

    def __str__(self):
        return f"Anamnese de {self.patient.name} por {self.caregiver.name if self.caregiver else 'Não informado'}"

    def clean(self):
        """Validações customizadas"""
        super().clean()
        
        # Valida se o paciente é realmente um paciente
        if self.patient and not self.patient.is_patient:
            from django.core.exceptions import ValidationError
            raise ValidationError({
                'patient': 'A pessoa selecionada deve ser marcada como paciente.'
            })
        
        # Valida se o cuidador é realmente um cuidador
        if self.caregiver and not self.caregiver.is_caregiver:
            from django.core.exceptions import ValidationError
            raise ValidationError({
                'caregiver': 'A pessoa selecionada deve ser marcada como cuidador.'
            })

    def save(self, *args, **kwargs):
        """Override do save para executar validações"""
        self.full_clean()
        super().save(*args, **kwargs)
