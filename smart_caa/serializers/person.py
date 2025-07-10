from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from ..models import Person


def validate_cpf(cpf):
    """
    Valida CPF brasileiro verificando formato e dígitos verificadores
    """
    # Remove caracteres não numéricos
    cpf_numbers = ''.join(filter(str.isdigit, cpf))
    
    # Verifica se tem 11 dígitos
    if len(cpf_numbers) != 11:
        raise serializers.ValidationError("CPF deve conter exatamente 11 dígitos")
    
    # Verifica se não é uma sequência de números iguais (ex: 111.111.111-11)
    if cpf_numbers == cpf_numbers[0] * 11:
        raise serializers.ValidationError("CPF não pode ser uma sequência de números iguais")
    
    # Calcula o primeiro dígito verificador
    soma = 0
    for i in range(9):
        soma += int(cpf_numbers[i]) * (10 - i)
    
    primeiro_digito = 11 - (soma % 11)
    if primeiro_digito >= 10:
        primeiro_digito = 0
    
    # Verifica o primeiro dígito
    if int(cpf_numbers[9]) != primeiro_digito:
        raise serializers.ValidationError("CPF inválido - primeiro dígito verificador incorreto")
    
    # Calcula o segundo dígito verificador
    soma = 0
    for i in range(10):
        soma += int(cpf_numbers[i]) * (11 - i)
    
    segundo_digito = 11 - (soma % 11)
    if segundo_digito >= 10:
        segundo_digito = 0
    
    # Verifica o segundo dígito
    if int(cpf_numbers[10]) != segundo_digito:
        raise serializers.ValidationError("CPF inválido - segundo dígito verificador incorreto")
    
    return cpf_numbers  # Retorna apenas os números para padronização


def format_cpf(cpf_numbers):
    """
    Formata CPF adicionando pontos e hífen
    """
    return f"{cpf_numbers[:3]}.{cpf_numbers[3:6]}.{cpf_numbers[6:9]}-{cpf_numbers[9:]}"


def create_user_for_person(cpf, email, name, password):
    """
    Função utilitária para criar usuário para uma pessoa
    """
    # Remove caracteres não numéricos do CPF para usar como username
    username = ''.join(filter(str.isdigit, cpf))
    
    # Verifica se já existe usuário com esse username (CPF)
    if User.objects.filter(username=username).exists():
        raise serializers.ValidationError({
            'cpf': 'Já existe um usuário cadastrado com este CPF.'
        })
    
    # Verifica se já existe usuário com esse email
    if User.objects.filter(email=email).exists():
        raise serializers.ValidationError({
            'email': 'Já existe um usuário cadastrado com este e-mail.'
        })
    
    # Cria o usuário
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=name.split()[0] if name.split() else '',
        last_name=' '.join(name.split()[1:]) if len(name.split()) > 1 else ''
    )
    
    return user


class PersonSerializer(serializers.ModelSerializer):
    """
    Serializer completo para Person (usado para consultas gerais)
    Inclui todos os campos disponíveis da pessoa
    """
    person_types = serializers.SerializerMethodField(
        help_text="Tipos da pessoa (Paciente, Cuidador ou ambos)"
    )
    
    created_by_username = serializers.CharField(
        source='created_by.username', 
        read_only=True,
        help_text="Nome do usuário que criou o registro"
    )
    
    user_id = serializers.IntegerField(
        source='user.id',
        read_only=True,
        allow_null=True,
        help_text="ID do usuário associado a esta pessoa"
    )
    
    username = serializers.CharField(
        source='user.username',
        read_only=True,
        allow_null=True,
        help_text="Nome de usuário associado a esta pessoa"
    )
    
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
            'cid',
            'profession',
            'postal_code',
            'state',
            'city',
            'district',
            'street',
            'number',
            'complement',
            'is_patient',
            'is_caregiver',
            'person_types',
            'colors',
            'sounds',
            'smells',
            'hobbies',
            'is_active',
            'created_by',
            'created_by_username',
            'created_at',
            'updated_at',
            'inactivated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at', 'inactivated_at', 'user_id', 'username']
    
    @extend_schema_field(serializers.ListField(child=serializers.CharField()))
    def get_person_types(self, obj):
        """Retorna lista com os tipos da pessoa"""
        types = []
        if obj.is_patient:
            types.append("Paciente")
        if obj.is_caregiver:
            types.append("Cuidador")
        return types


class PatientSerializer(serializers.ModelSerializer):
    """
    Serializer para Paciente
    """
    created_by_username = serializers.CharField(
        source='created_by.username', 
        read_only=True,
        help_text="Nome do usuário que criou o paciente"
    )
    
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text="Senha para o usuário do sistema (mínimo 8 caracteres)",
        min_length=8
    )
    
    class Meta:
        model = Person
        fields = [
            'id',
            'name',
            'cpf',
            'email',
            'phone',
            'cid',
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
            'password',
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
            'cid': {
                'help_text': 'Classificação Internacional de Doenças (formato: A00-B99, C00-D48)'
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
        # Remove a senha dos dados validados para não tentar salvar no modelo Person
        password = validated_data.pop('password')
        cpf = validated_data.get('cpf')
        email = validated_data.get('email')
        name = validated_data.get('name')
        
        # Remove formatação do CPF para busca
        cpf_numbers = ''.join(filter(str.isdigit, cpf))
        
        # Verifica se pessoa já existe com esse CPF (busca por números apenas)
        try:
            # Busca flexível por CPF (com ou sem formatação)
            person = Person.objects.filter(
                cpf__regex=r'[^0-9]*' + ''.join(f'[^0-9]*{d}' for d in cpf_numbers) + '[^0-9]*'
            ).first()
            
            if person:
                # Se a pessoa já tem um usuário associado, retorna erro
                if person.user:
                    raise serializers.ValidationError({
                        'cpf': 'Esta pessoa já possui um usuário associado.'
                    })
                
                # Valida consistência dos dados básicos
                self._validate_existing_person(person, validated_data)
                
                # Cria o usuário usando a função utilitária
                user = create_user_for_person(cpf, email, name, password)
                
                # Atualiza dados da pessoa
                for field, value in validated_data.items():
                    setattr(person, field, value)
                    
                # Marca como paciente e associa o usuário
                person.is_patient = True
                person.user = user
                person.save()
                
                return person
            else:
                # Pessoa não existe, cria nova
                raise Person.DoesNotExist()
            
        except Person.DoesNotExist:
            # Cria o usuário usando a função utilitária
            user = create_user_for_person(cpf, email, name, password)
            
            # Cria nova pessoa como paciente
            validated_data['is_patient'] = True
            validated_data['user'] = user
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
        """Validação completa de CPF"""
        # Usa a função de validação de CPF
        cpf_numbers = validate_cpf(value)
        
        # Retorna o CPF formatado
        return format_cpf(cpf_numbers)

    def validate_password(self, value):
        """Validação de senha usando validadores do Django"""
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)
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
    
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text="Senha para o usuário do sistema (mínimo 8 caracteres)",
        min_length=8
    )
    
    class Meta:
        model = Person
        fields = [
            'id',
            'name',
            'cpf',
            'email',
            'phone',
            'profession',
            'postal_code',
            'state',
            'city',
            'district',
            'street',
            'number',
            'complement',
            'password',
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
            'profession': {
                'help_text': 'Profissão ou ocupação do cuidador'
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
        # Remove a senha dos dados validados para não tentar salvar no modelo Person
        password = validated_data.pop('password')
        cpf = validated_data.get('cpf')
        email = validated_data.get('email')
        name = validated_data.get('name')
        
        # Remove formatação do CPF para busca
        cpf_numbers = ''.join(filter(str.isdigit, cpf))
        
        # Verifica se pessoa já existe com esse CPF (busca por números apenas)
        try:
            # Busca flexível por CPF (com ou sem formatação)
            person = Person.objects.filter(
                cpf__regex=r'[^0-9]*' + ''.join(f'[^0-9]*{d}' for d in cpf_numbers) + '[^0-9]*'
            ).first()
            
            if person:
                # Se a pessoa já tem um usuário associado, retorna erro
                if person.user:
                    raise serializers.ValidationError({
                        'cpf': 'Esta pessoa já possui um usuário associado.'
                    })
                
                # Valida consistência dos dados básicos
                self._validate_existing_person(person, validated_data)
                
                # Cria o usuário usando a função utilitária
                user = create_user_for_person(cpf, email, name, password)
                
                # Atualiza dados da pessoa (preserva campos específicos do paciente)
                for field, value in validated_data.items():
                    setattr(person, field, value)
                    
                # Marca como cuidador e associa o usuário
                person.is_caregiver = True
                person.user = user
                person.save()
                
                return person
            else:
                # Pessoa não existe, cria nova
                raise Person.DoesNotExist()
            
        except Person.DoesNotExist:
            # Cria o usuário usando a função utilitária
            user = create_user_for_person(cpf, email, name, password)
            
            # Cria nova pessoa como cuidador
            validated_data['is_caregiver'] = True
            validated_data['user'] = user
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
        """Validação completa de CPF"""
        # Usa a função de validação de CPF
        cpf_numbers = validate_cpf(value)
        
        # Retorna o CPF formatado
        return format_cpf(cpf_numbers)

    def validate_password(self, value):
        """Validação de senha usando validadores do Django"""
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)
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
