from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from ..models import Person


class PatientSerializer(serializers.ModelSerializer):
    """
    Serializer para Paciente
    """
    created_by_username = serializers.CharField(
        source='created_by.username', 
        read_only=True,
        help_text="Nome do usuário que criou o paciente"
    )
    
    class Meta:
        model = Person
        fields = [
            'id',
            'name',
            'cpf',
            'email',
            'phone',
            'postal_code',
            'state',
            'city',
            'district',
            'street',
            'number',
            'complement',
            'colors',
            'sounds',
            'smells',
            'hobbies',
            'is_active',
            'created_by',
            'created_by_username',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']
        extra_kwargs = {
            'name': {
                'help_text': 'Nome completo do paciente'
            },
            'cpf': {
                'help_text': 'CPF do paciente (formato: 000.000.000-00)'
            },
            'email': {
                'help_text': 'E-mail do paciente'
            },
            'phone': {
                'help_text': 'Telefone de contato do paciente'
            },
            'postal_code': {
                'help_text': 'CEP do endereço'
            },
            'state': {
                'help_text': 'Estado (UF)'
            },
            'city': {
                'help_text': 'Cidade'
            },
            'district': {
                'help_text': 'Bairro'
            },
            'street': {
                'help_text': 'Logradouro (rua, avenida, etc.)'
            },
            'number': {
                'help_text': 'Número da residência'
            },
            'complement': {
                'help_text': 'Complemento do endereço'
            },
            'colors': {
                'help_text': 'Cores que o paciente gosta ou tem preferência'
            },
            'sounds': {
                'help_text': 'Sons, toques ou músicas que o paciente aprecia'
            },
            'smells': {
                'help_text': 'Cheiros que o paciente gosta ou reconhece'
            },
            'hobbies': {
                'help_text': 'Atividades e hobbies do paciente'
            },
            'is_active': {
                'help_text': 'Indica se o paciente está ativo no sistema'
            }
        }
    
    def create(self, validated_data):
        cpf = validated_data.get('cpf')
        
        # Verifica se pessoa já existe com esse CPF
        try:
            person = Person.objects.get(cpf=cpf)
            
            # Valida consistência dos dados básicos
            self._validate_existing_person(person, validated_data)
            
            # Atualiza dados da pessoa
            for field, value in validated_data.items():
                setattr(person, field, value)
                
            # Marca como paciente
            person.is_patient = True
            person.save()
            
            return person
            
        except Person.DoesNotExist:
            # Cria nova pessoa como paciente
            validated_data['is_patient'] = True
            return super().create(validated_data)
    
    def _validate_existing_person(self, person, validated_data):
        """Valida se dados básicos são consistentes com pessoa existente"""
        inconsistencies = []
        
        if person.name != validated_data.get('name'):
            inconsistencies.append(f"Nome atual: '{person.name}', nome fornecido: '{validated_data.get('name')}'")
            
        if person.email != validated_data.get('email'):
            inconsistencies.append(f"E-mail atual: '{person.email}', e-mail fornecido: '{validated_data.get('email')}'")
            
        if inconsistencies:
            raise serializers.ValidationError({
                'cpf': f"CPF já cadastrado com dados diferentes: {'; '.join(inconsistencies)}"
            })
    
    def validate_cpf(self, value):
        """Validação básica de CPF"""
        # Remove caracteres não numéricos
        cpf_numbers = ''.join(filter(str.isdigit, value))
        
        if len(cpf_numbers) != 11:
            raise serializers.ValidationError("CPF deve conter 11 dígitos")
            
        return value


class CaregiverSerializer(serializers.ModelSerializer):
    """
    Serializer para Cuidador
    """
    created_by_username = serializers.CharField(
        source='created_by.username', 
        read_only=True,
        help_text="Nome do usuário que criou o cuidador"
    )
    
    class Meta:
        model = Person
        fields = [
            'id',
            'name',
            'cpf',
            'email',
            'phone',
            'postal_code',
            'state',
            'city',
            'district',
            'street',
            'number',
            'complement',
            'is_active',
            'created_by',
            'created_by_username',
            'created_at',
            'updated_at'
        ]  # Não inclui campos específicos do paciente
        read_only_fields = ['created_by', 'created_at', 'updated_at']
        extra_kwargs = {
            'name': {
                'help_text': 'Nome completo do cuidador'
            },
            'cpf': {
                'help_text': 'CPF do cuidador (formato: 000.000.000-00)'
            },
            'email': {
                'help_text': 'E-mail do cuidador'
            },
            'phone': {
                'help_text': 'Telefone de contato do cuidador'
            },
            'postal_code': {
                'help_text': 'CEP do endereço'
            },
            'state': {
                'help_text': 'Estado (UF)'
            },
            'city': {
                'help_text': 'Cidade'
            },
            'district': {
                'help_text': 'Bairro'
            },
            'street': {
                'help_text': 'Logradouro (rua, avenida, etc.)'
            },
            'number': {
                'help_text': 'Número da residência'
            },
            'complement': {
                'help_text': 'Complemento do endereço'
            },
            'is_active': {
                'help_text': 'Indica se o cuidador está ativo no sistema'
            }
        }
    
    def create(self, validated_data):
        cpf = validated_data.get('cpf')
        
        # Verifica se pessoa já existe com esse CPF
        try:
            person = Person.objects.get(cpf=cpf)
            
            # Valida consistência dos dados básicos
            self._validate_existing_person(person, validated_data)
            
            # Atualiza dados da pessoa (preserva campos específicos do paciente)
            for field, value in validated_data.items():
                setattr(person, field, value)
                
            # Marca como cuidador
            person.is_caregiver = True
            person.save()
            
            return person
            
        except Person.DoesNotExist:
            # Cria nova pessoa como cuidador
            validated_data['is_caregiver'] = True
            return super().create(validated_data)
    
    def _validate_existing_person(self, person, validated_data):
        """Valida se dados básicos são consistentes com pessoa existente"""
        inconsistencies = []
        
        if person.name != validated_data.get('name'):
            inconsistencies.append(f"Nome atual: '{person.name}', nome fornecido: '{validated_data.get('name')}'")
            
        if person.email != validated_data.get('email'):
            inconsistencies.append(f"E-mail atual: '{person.email}', e-mail fornecido: '{validated_data.get('email')}'")
            
        if inconsistencies:
            raise serializers.ValidationError({
                'cpf': f"CPF já cadastrado com dados diferentes: {'; '.join(inconsistencies)}"
            })
    
    def validate_cpf(self, value):
        """Validação básica de CPF"""
        # Remove caracteres não numéricos
        cpf_numbers = ''.join(filter(str.isdigit, value))
        
        if len(cpf_numbers) != 11:
            raise serializers.ValidationError("CPF deve conter 11 dígitos")
            
        return value


class PersonListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listagem geral de pessoas
    """
    person_types = serializers.SerializerMethodField(
        help_text="Tipos da pessoa (Paciente, Cuidador ou ambos)"
    )
    
    created_by_username = serializers.CharField(
        source='created_by.username', 
        read_only=True,
        help_text="Nome do usuário que criou o registro"
    )
    
    class Meta:
        model = Person
        fields = [
            'id',
            'name',
            'cpf',
            'email',
            'phone',
            'person_types',
            'is_active',
            'created_by_username',
            'created_at',
            'updated_at'
        ]
    
    @extend_schema_field(serializers.ListField(child=serializers.CharField()))
    def get_person_types(self, obj):
        """Retorna lista com os tipos da pessoa"""
        types = []
        if obj.is_patient:
            types.append("Paciente")
        if obj.is_caregiver:
            types.append("Cuidador")
        return types
