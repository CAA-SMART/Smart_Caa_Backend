from rest_framework import serializers
from ..models import PatientCaregiverRelationship, Person


class PatientCaregiverRelationshipSerializer(serializers.ModelSerializer):
    """
    Serializer para Relacionamento Paciente-Cuidador
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
    
    relationship_type_display = serializers.CharField(
        source='get_relationship_type_display',
        read_only=True,
        help_text="Descrição do tipo de relacionamento"
    )
    
    created_by_username = serializers.CharField(
        source='created_by.username',
        read_only=True,
        help_text="Nome do usuário que criou o relacionamento"
    )
    
    class Meta:
        model = PatientCaregiverRelationship
        fields = [
            'id',
            'patient',
            'patient_name',
            'caregiver',
            'caregiver_name',
            'relationship_type',
            'relationship_type_display',
            'start_date',
            'notes',
            'is_active',
            'created_by',
            'created_by_username',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']
        extra_kwargs = {
            'patient': {
                'help_text': 'ID do paciente'
            },
            'caregiver': {
                'help_text': 'ID do cuidador'
            },
            'relationship_type': {
                'help_text': 'Tipo de relacionamento (FAMILY, PROFESSIONAL, FRIEND, VOLUNTEER, OTHER)'
            },
            'start_date': {
                'help_text': 'Data de início do relacionamento'
            },
            'notes': {
                'help_text': 'Observações sobre o relacionamento'
            },
            'is_active': {
                'help_text': 'Indica se o relacionamento está ativo'
            }
        }
    
    def validate(self, data):
        """Validações customizadas"""
        patient = data.get('patient')
        caregiver = data.get('caregiver')
        is_active = data.get('is_active', True)
        
        # Verifica se o paciente é realmente um paciente
        if patient and not patient.is_patient:
            raise serializers.ValidationError({
                'patient': 'A pessoa selecionada deve estar marcada como paciente.'
            })
        
        # Verifica se o cuidador é realmente um cuidador
        if caregiver and not caregiver.is_caregiver:
            raise serializers.ValidationError({
                'caregiver': 'A pessoa selecionada deve estar marcada como cuidador.'
            })
        
        # Verifica se não é a mesma pessoa
        if patient and caregiver and patient.id == caregiver.id:
            raise serializers.ValidationError(
                'Uma pessoa não pode ser paciente e cuidador de si mesma.'
            )
        
        # Verifica se não existe outro vínculo ativo entre as mesmas pessoas
        if patient and caregiver and is_active:
            existing_active = PatientCaregiverRelationship.objects.filter(
                patient=patient,
                caregiver=caregiver,
                is_active=True,
                inactivated_at__isnull=True
            )
            
            # Se estamos editando um registro existente, excluir o próprio registro da verificação
            if self.instance:
                existing_active = existing_active.exclude(pk=self.instance.pk)
            
            if existing_active.exists():
                existing_relationship = existing_active.first()
                raise serializers.ValidationError(
                    f'Já existe um vínculo ativo entre {patient.name} e {caregiver.name} '
                    f'({existing_relationship.get_relationship_type_display()}) desde {existing_relationship.start_date}. '
                    f'Inative o vínculo anterior antes de criar um novo.'
                )
        
        return data


class PatientCaregiverListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listagem de relacionamentos
    """
    patient_name = serializers.CharField(
        source='patient.name',
        read_only=True
    )
    
    caregiver_name = serializers.CharField(
        source='caregiver.name',
        read_only=True
    )
    
    relationship_type_display = serializers.CharField(
        source='get_relationship_type_display',
        read_only=True
    )
    
    class Meta:
        model = PatientCaregiverRelationship
        fields = [
            'id',
            'patient',
            'patient_name',
            'caregiver',
            'caregiver_name',
            'relationship_type',
            'relationship_type_display',
            'start_date',
            'is_active'
        ]


class CaregiverForPatientSerializer(serializers.ModelSerializer):
    """
    Serializer para mostrar cuidadores de um paciente
    """
    caregiver_id = serializers.IntegerField(source='caregiver.id')
    caregiver_name = serializers.CharField(source='caregiver.name')
    caregiver_email = serializers.EmailField(source='caregiver.email')
    caregiver_phone = serializers.CharField(source='caregiver.phone')
    relationship_type_display = serializers.CharField(source='get_relationship_type_display')
    
    class Meta:
        model = PatientCaregiverRelationship
        fields = [
            'id',
            'caregiver_id',
            'caregiver_name',
            'caregiver_email',
            'caregiver_phone',
            'relationship_type',
            'relationship_type_display',
            'start_date',
            'notes',
            'is_active'
        ]


class PatientForCaregiverSerializer(serializers.ModelSerializer):
    """
    Serializer para mostrar pacientes de um cuidador
    """
    patient_id = serializers.IntegerField(source='patient.id')
    patient_name = serializers.CharField(source='patient.name')
    patient_email = serializers.EmailField(source='patient.email')
    patient_phone = serializers.CharField(source='patient.phone')
    relationship_type_display = serializers.CharField(source='get_relationship_type_display')
    
    class Meta:
        model = PatientCaregiverRelationship
        fields = [
            'id',
            'patient_id',
            'patient_name',
            'patient_email',
            'patient_phone',
            'relationship_type',
            'relationship_type_display',
            'start_date',
            'notes',
            'is_active'
        ]
