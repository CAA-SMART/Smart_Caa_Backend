from rest_framework import serializers
from ..models import Anamnesis


class AnamnesisSerializer(serializers.ModelSerializer):
    """
    Serializer completo para Anamnesis
    """
    
    # Campos read-only para informações do paciente
    patient_name = serializers.CharField(
        source='patient.name',
        read_only=True,
        help_text="Nome do paciente"
    )
    
    patient_cpf = serializers.CharField(
        source='patient.cpf',
        read_only=True,
        help_text="CPF do paciente"
    )
    
    # Campos read-only para informações do cuidador
    caregiver_name = serializers.CharField(
        source='caregiver.name',
        read_only=True,
        help_text="Nome do cuidador"
    )
    
    created_by_username = serializers.CharField(
        source='created_by.username',
        read_only=True,
        help_text="Nome do usuário que criou o registro"
    )

    class Meta:
        model = Anamnesis
        fields = [
            'id',
            'patient',
            'patient_name',
            'patient_cpf',
            'caregiver',
            'caregiver_name',
            'main_diagnosis',
            'associated_conditions',
            'responsible_contact',
            'reference_professional',
            'cognitive_level',
            'auditory_comprehension',
            'memory_profile',
            'attention_duration',
            'learning_pace',
            'language_style',
            'functional_speech',
            'speech_intelligibility',
            'uses_gestures',
            'uses_signs',
            'uses_images_or_symbols',
            'preferred_symbol_systems',
            'symbol_comprehension',
            'communication_priorities',
            'is_active',
            'created_by',
            'created_by_username',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']
        extra_kwargs = {
            'patient': {
                'help_text': 'ID do paciente para quem a anamnese está sendo criada'
            },
            'caregiver': {
                'help_text': 'ID do cuidador que está criando a anamnese'
            },
            'main_diagnosis': {
                'help_text': 'Diagnóstico principal do paciente'
            },
            'associated_conditions': {
                'help_text': 'Comorbidades ou diagnósticos secundários'
            },
            'responsible_contact': {
                'help_text': 'Contato do responsável ou cuidador'
            },
            'reference_professional': {
                'help_text': 'Profissional de referência que acompanha o paciente'
            },
            'cognitive_level': {
                'help_text': 'Nível cognitivo estimado do paciente'
            },
            'attention_duration': {
                'help_text': 'Tempo ou nível de atenção/concentração'
            },
            'memory_profile': {
                'help_text': 'Perfil de memória visual e/ou auditiva'
            },
            'learning_pace': {
                'help_text': 'Velocidade ou facilidade de aprendizado'
            },
            'language_style': {
                'help_text': 'Se a compreensão é mais literal, figurada ou ambas'
            },
            'functional_speech': {
                'help_text': 'Se possui fala funcional: não, parcial ou completa'
            },
            'speech_intelligibility': {
                'help_text': 'Nível de inteligibilidade da fala'
            },
            'auditory_comprehension': {
                'help_text': 'Compreensão auditiva de palavras, frases ou comandos'
            },
            'uses_gestures': {
                'help_text': 'Indica se o paciente utiliza gestos naturais'
            },
            'uses_signs': {
                'help_text': 'Indica se o paciente utiliza sinais/Libras'
            },
            'uses_images_or_symbols': {
                'help_text': 'Indica se o paciente utiliza imagens, figuras ou símbolos'
            },
            'preferred_symbol_systems': {
                'help_text': 'Sistemas de símbolos preferidos, como Arasaac ou fotografias'
            },
            'symbol_comprehension': {
                'help_text': 'Nível de compreensão dos símbolos apresentados'
            },
            'communication_priorities': {
                'help_text': 'Principais necessidades comunicativas do paciente'
            }
        }

    def validate_patient(self, value):
        """Valida se a pessoa é marcada como paciente"""
        if not value.is_patient:
            raise serializers.ValidationError(
                "A pessoa selecionada deve ser marcada como paciente."
            )
        return value

    def validate_caregiver(self, value):
        """Valida se a pessoa é marcada como cuidador"""
        if value and not value.is_caregiver:
            raise serializers.ValidationError(
                "A pessoa selecionada deve ser marcada como cuidador."
            )
        return value

    def validate(self, data):
        """Validações adicionais"""
        patient = data.get('patient')
        caregiver = data.get('caregiver')
        
        # Verifica se já existe uma anamnese para este paciente por este cuidador
        if patient and caregiver:
            # Se é uma criação (não tem self.instance)
            if not self.instance:
                existing = Anamnesis.objects.filter(
                    patient=patient,
                    caregiver=caregiver
                ).exists()
                
                if existing:
                    raise serializers.ValidationError({
                        'non_field_errors': [
                            'Já existe uma anamnese deste paciente criada por este cuidador. '
                            'Apenas uma anamnese por paciente/cuidador é permitida.'
                        ]
                    })
            
            # Se é uma atualização, verifica se não está mudando para uma combinação que já existe
            else:
                existing = Anamnesis.objects.filter(
                    patient=patient,
                    caregiver=caregiver
                ).exclude(id=self.instance.id).exists()
                
                if existing:
                    raise serializers.ValidationError({
                        'non_field_errors': [
                            'Já existe uma anamnese deste paciente criada por este cuidador.'
                        ]
                    })
        
        return data


class AnamnesisListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listagem de anamneses
    """
    
    patient_name = serializers.CharField(
        source='patient.name',
        read_only=True,
        help_text="Nome do paciente"
    )
    
    caregiver_name = serializers.CharField(
        source='caregiver.name',
        read_only=True,
        help_text="Nome do cuidador"
    )

    class Meta:
        model = Anamnesis
        fields = [
            'id',
            'patient',
            'patient_name',
            'caregiver',
            'caregiver_name',
            'main_diagnosis',
            'cognitive_level',
            'functional_speech',
            'is_active',
            'created_at',
            'updated_at'
        ]


class CaregiverAnamnesisSerializer(serializers.ModelSerializer):
    """
    Serializer para anamneses de um cuidador específico
    """
    
    patient_name = serializers.CharField(
        source='patient.name',
        read_only=True,
        help_text="Nome do paciente"
    )
    
    patient_cpf = serializers.CharField(
        source='patient.cpf',
        read_only=True,
        help_text="CPF do paciente"
    )

    class Meta:
        model = Anamnesis
        fields = [
            'id',
            'patient',
            'patient_name',
            'patient_cpf',
            'main_diagnosis',
            'associated_conditions',
            'cognitive_level',
            'functional_speech',
            'is_active',
            'created_at',
            'updated_at'
        ]
