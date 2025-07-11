from rest_framework import serializers
from django.contrib.auth.models import User
from ..models import Person


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer para o perfil do usuário logado
    Retorna dados do User + dados da Person associada
    """
    # Dados do usuário
    username = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    date_joined = serializers.DateTimeField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    
    # Dados da pessoa associada
    person_id = serializers.IntegerField(source='person.id', read_only=True)
    person_name = serializers.CharField(source='person.name', read_only=True)
    person_cpf = serializers.CharField(source='person.cpf', read_only=True)
    person_email = serializers.EmailField(source='person.email', read_only=True)
    person_phone = serializers.CharField(source='person.phone', read_only=True)
    person_profession = serializers.CharField(source='person.profession', read_only=True)
    person_cid = serializers.CharField(source='person.cid', read_only=True)
    
    # Tipos de pessoa
    is_patient = serializers.BooleanField(source='person.is_patient', read_only=True)
    is_caregiver = serializers.BooleanField(source='person.is_caregiver', read_only=True)
    
    # Endereço
    postal_code = serializers.CharField(source='person.postal_code', read_only=True)
    state = serializers.CharField(source='person.state', read_only=True)
    city = serializers.CharField(source='person.city', read_only=True)
    district = serializers.CharField(source='person.district', read_only=True)
    street = serializers.CharField(source='person.street', read_only=True)
    number = serializers.CharField(source='person.number', read_only=True)
    complement = serializers.CharField(source='person.complement', read_only=True)
    
    # Informações específicas do paciente (se aplicável)
    colors = serializers.CharField(source='person.colors', read_only=True)
    sounds = serializers.CharField(source='person.sounds', read_only=True)
    smells = serializers.CharField(source='person.smells', read_only=True)
    hobbies = serializers.CharField(source='person.hobbies', read_only=True)
    
    class Meta:
        model = User
        fields = [
            # Dados do usuário
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'date_joined',
            'is_active',
            
            # Dados da pessoa
            'person_id',
            'person_name',
            'person_cpf',
            'person_email',
            'person_phone',
            'person_profession',
            'person_cid',
            
            # Tipos
            'is_patient',
            'is_caregiver',
            
            # Endereço
            'postal_code',
            'state',
            'city',
            'district',
            'street',
            'number',
            'complement',
            
            # Específicos do paciente
            'colors',
            'sounds',
            'smells',
            'hobbies',
        ]
    
    def to_representation(self, instance):
        """Customiza a representação para tratar casos onde não há pessoa associada"""
        data = super().to_representation(instance)
        
        # Se não há pessoa associada, remove campos relacionados à pessoa
        if not hasattr(instance, 'person') or instance.person is None:
            person_fields = [
                'person_id', 'person_name', 'person_cpf', 'person_email', 
                'person_phone', 'person_profession', 'person_cid',
                'is_patient', 'is_caregiver',
                'postal_code', 'state', 'city', 'district', 'street', 'number', 'complement',
                'colors', 'sounds', 'smells', 'hobbies'
            ]
            for field in person_fields:
                data[field] = None
                
        return data


class MyPersonSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado que retorna apenas os dados da Person do usuário logado
    """
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Person
        fields = [
            'id',
            'user_id',
            'username',
            'name',
            'cpf',
            'email',
            'phone',
            'profession',
            'cid',
            'postal_code',
            'state',
            'city',
            'district',
            'street',
            'number',
            'complement',
            'is_patient',
            'is_caregiver',
            'colors',
            'sounds',
            'smells',
            'hobbies',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
