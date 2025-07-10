from rest_framework import status
from rest_framework.permissions import IsAuthenticated
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
    permission_classes = (IsAuthenticated,)
    
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
    permission_classes = (IsAuthenticated,)
    
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
            # Busca a pessoa pelo CPF (com ou sem formatação)
            person = Person.objects.filter(cpf__contains=cpf_numbers).first()
            
            if not person:
                return Response(
                    {'detail': f'Pessoa com CPF {cpf} não encontrada.'},
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
            return Response(
                {
                    'detail': f'Erro ao buscar pessoa: {str(e)}',
                    'cpf_pesquisado': cpf,
                    'cpf_numerico': cpf_numbers
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
