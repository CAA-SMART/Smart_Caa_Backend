from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from ..models import Person
from ..serializers.person import PersonSerializer


@extend_schema(tags=['Person'])
class GetPersonByUserIdView(APIView):
    """
    View para obter a pessoa associada a um usuário específico pelo ID do usuário
    """
    permission_classes = (AllowAny,)  # Removida autenticação obrigatória
    
    @extend_schema(
        summary='Obter Pessoa por ID do Usuário',
        description='Retorna os dados da pessoa associada ao usuário especificado pelo ID',
        responses={
            200: PersonSerializer,
            404: {'description': 'Usuário não encontrado ou não possui pessoa associada'}
        }
    )
    def get(self, request, user_id):
        """Retorna os dados da pessoa associada ao usuário especificado"""
        # Busca o usuário pelo ID
        user = get_object_or_404(User, id=user_id)
        
        try:
            # Busca a pessoa associada ao usuário
            person = user.person
            serializer = PersonSerializer(person)
            return Response(serializer.data)
        except Person.DoesNotExist:
            return Response(
                {
                    'detail': f'Usuário com ID {user_id} não possui pessoa associada.',
                    'user_id': user.id,
                    'username': user.username
                },
                status=status.HTTP_404_NOT_FOUND
            )


@extend_schema(tags=['Person'])
class GetPersonByCpfView(APIView):
    """
    View para buscar pessoa pelo CPF e ver se tem usuário associado
    """
    permission_classes = (AllowAny,)  # Removida autenticação obrigatória
    
    @extend_schema(
        summary='Buscar Pessoa por CPF',
        description='Busca pessoa pelo CPF e retorna informações sobre usuário associado',
        responses={
            200: PersonSerializer,
            404: {'description': 'Pessoa não encontrada'}
        }
    )
    def get(self, request, cpf):
        """Busca pessoa pelo CPF"""
        # Remove formatação do CPF
        cpf_numbers = ''.join(filter(str.isdigit, cpf))
        
        try:
            # Busca a pessoa pelo CPF de forma exata
            # Primeiro tenta busca exata pelos números (sem formatação)
            person = Person.objects.filter(cpf=cpf_numbers).first()
            
            # Se não encontrar, tenta busca exata com a formatação original
            if not person:
                person = Person.objects.filter(cpf=cpf).first()
            
            if not person:
                return Response(
                    {
                        'detail': f'Pessoa com CPF {cpf} não encontrada.',
                        'cpf_pesquisado': cpf,
                        'cpf_numerico': cpf_numbers,
                        'debug_info': 'Busca exata apenas - sem busca parcial'
                    },
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Verifica se há usuário associado
            user_info = None
            if person.user:
                user_info = {
                    'user_id': person.user.id,
                    'username': person.user.username,
                    'email': person.user.email,
                    'first_name': person.user.first_name,
                    'last_name': person.user.last_name,
                    'is_active': person.user.is_active,
                    'date_joined': person.user.date_joined
                }
            
            serializer = PersonSerializer(person)
            response_data = serializer.data
            response_data['user_info'] = user_info
            
            return Response(response_data)
            
        except Exception as e:
            # Adiciona informações de debug para produção
            all_cpfs = Person.objects.values_list('cpf', flat=True)[:10]  # Primeiros 10 CPFs para debug
            return Response(
                {
                    'detail': f'Erro ao buscar pessoa: {str(e)}',
                    'cpf_pesquisado': cpf,
                    'cpf_numerico': cpf_numbers,
                    'debug_cpfs_existentes': list(all_cpfs),
                    'total_pessoas': Person.objects.count()
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema(tags=['Person'])
class MakeCaregiverView(APIView):
    """
    View para tornar uma pessoa em cuidador
    """
    permission_classes = (IsAuthenticated,)  # Requer autenticação
    
    @extend_schema(
        summary='Tornar Pessoa em Cuidador',
        description='Atualiza uma pessoa existente para se tornar cuidador. Apenas marca o campo is_caregiver como True. **Requer autenticação.**',
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'profession': {
                        'type': 'string',
                        'description': 'Profissão ou ocupação do cuidador (opcional)',
                        'example': 'Enfermeiro'
                    }
                },
                'required': []
            }
        },
        responses={
            200: {
                'description': 'Pessoa atualizada para cuidador com sucesso',
                'content': {
                    'application/json': {
                        'type': 'object',
                        'properties': {
                            'message': {'type': 'string'},
                            'is_caregiver': {'type': 'boolean'},
                            'updated_fields': {'type': 'object'}
                        }
                    }
                }
            },
            400: {'description': 'Pessoa já é cuidador ou dados inválidos'},
            401: {'description': 'Não autenticado'},
            403: {'description': 'Sem permissão'},
            404: {'description': 'Pessoa não encontrada'}
        }
    )
    def patch(self, request, person_id):
        """Torna uma pessoa em cuidador"""
        try:
            # Busca a pessoa pelo ID
            person = get_object_or_404(Person, id=person_id)
            
            # Verifica se a pessoa já é cuidador
            if person.is_caregiver:
                return Response(
                    {
                        'message': 'Esta pessoa já é um cuidador.',
                        'is_caregiver': True
                    },
                    status=status.HTTP_200_OK
                )
            
            # Prepara campos que serão atualizados
            updated_fields = {}
            
            # Atualiza campos opcionais se fornecidos
            profession = request.data.get('profession')
            if profession:
                person.profession = profession
                updated_fields['profession'] = profession
            
            # Marca como cuidador
            person.is_caregiver = True
            updated_fields['is_caregiver'] = True
            person.save()
            
            return Response(
                {
                    'message': 'Pessoa atualizada para cuidador com sucesso.',
                    'is_caregiver': True,
                    'updated_fields': updated_fields
                },
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            return Response(
                {
                    'detail': f'Erro ao atualizar pessoa para cuidador: {str(e)}',
                    'person_id': person_id
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema(tags=['Person'])
class MakePatientView(APIView):
    """
    View para tornar uma pessoa em paciente
    """
    permission_classes = (IsAuthenticated,)  # Requer autenticação
    
    @extend_schema(
        summary='Tornar Pessoa em Paciente',
        description='Atualiza uma pessoa existente para se tornar paciente. Marca o campo is_patient como True e permite atualizar campos específicos do paciente. **Requer autenticação.**',
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'cid': {
                        'type': 'string',
                        'description': 'Classificação Internacional de Doenças (opcional)',
                        'example': 'F84.0'
                    },
                    'colors': {
                        'type': 'string',
                        'description': 'Cores que o paciente gosta ou tem preferência (opcional)',
                        'example': 'Azul, Verde, Amarelo'
                    },
                    'sounds': {
                        'type': 'string',
                        'description': 'Sons, toques ou músicas que o paciente aprecia (opcional)',
                        'example': 'Música clássica, sons da natureza'
                    },
                    'smells': {
                        'type': 'string',
                        'description': 'Cheiros que o paciente gosta ou reconhece (opcional)',
                        'example': 'Lavanda, café, flores'
                    },
                    'hobbies': {
                        'type': 'string',
                        'description': 'Atividades e hobbies do paciente (opcional)',
                        'example': 'Pintura, música, jogos'
                    }
                },
                'required': []
            }
        },
        responses={
            200: {
                'description': 'Pessoa atualizada para paciente com sucesso',
                'content': {
                    'application/json': {
                        'type': 'object',
                        'properties': {
                            'message': {'type': 'string'},
                            'is_patient': {'type': 'boolean'},
                            'updated_fields': {'type': 'object'}
                        }
                    }
                }
            },
            400: {'description': 'Pessoa já é paciente ou dados inválidos'},
            401: {'description': 'Não autenticado'},
            403: {'description': 'Sem permissão'},
            404: {'description': 'Pessoa não encontrada'}
        }
    )
    def patch(self, request, person_id):
        """Torna uma pessoa em paciente"""
        try:
            # Busca a pessoa pelo ID
            person = get_object_or_404(Person, id=person_id)
            
            # Verifica se a pessoa já é paciente
            if person.is_patient:
                return Response(
                    {
                        'message': 'Esta pessoa já é um paciente.',
                        'is_patient': True
                    },
                    status=status.HTTP_200_OK
                )
            
            # Prepara campos que serão atualizados
            updated_fields = {}
            
            # Atualiza campos específicos do paciente se fornecidos
            patient_fields = ['cid', 'colors', 'sounds', 'smells', 'hobbies']
            for field in patient_fields:
                value = request.data.get(field)
                if value:
                    setattr(person, field, value)
                    updated_fields[field] = value
            
            # Marca como paciente
            person.is_patient = True
            updated_fields['is_patient'] = True
            person.save()
            
            return Response(
                {
                    'message': 'Pessoa atualizada para paciente com sucesso.',
                    'is_patient': True,
                    'updated_fields': updated_fields
                },
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            return Response(
                {
                    'detail': f'Erro ao atualizar pessoa para paciente: {str(e)}',
                    'person_id': person_id
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
