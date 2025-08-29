from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from ..models import Anamnesis, Person


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
            'allergies',
            'medications',
            'communication_methods',
            'spoken_words',
            'preferred_pictograms',
            'dietary_restrictions',
            'food_preferences',
            'feeding_difficulties',
            'needs_expression',
            'frustration_reactions',
            'general_observations',
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
                'help_text': 'Diagnóstico médico principal do paciente'
            },
            'associated_conditions': {
                'help_text': 'Outras condições médicas ou comorbidades'
            },
            'allergies': {
                'help_text': 'Alergias conhecidas do paciente'
            },
            'medications': {
                'help_text': 'Medicamentos em uso atual'
            },
            'communication_methods': {
                'help_text': 'Métodos de comunicação utilizados pelo paciente'
            },
            'spoken_words': {
                'help_text': 'Palavras que o paciente consegue falar ou entender'
            },
            'preferred_pictograms': {
                'help_text': 'Pictogramas ou símbolos preferidos pelo paciente'
            },
            'dietary_restrictions': {
                'help_text': 'Alimentos que devem ser evitados ou restrições específicas'
            },
            'food_preferences': {
                'help_text': 'Alimentos favoritos ou preferências do paciente'
            },
            'feeding_difficulties': {
                'help_text': 'Problemas ou dificuldades relacionadas à alimentação'
            },
            'needs_expression': {
                'help_text': 'Como o paciente expressa suas necessidades e desejos'
            },
            'frustration_reactions': {
                'help_text': 'Como o paciente reage quando frustrado ou irritado'
            },
            'general_observations': {
                'help_text': 'Observações adicionais importantes sobre o paciente'
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
            'is_active',
            'created_at',
            'updated_at'
        ]
