from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from ..models import Person
from ..serializers.person import PersonSerializer


@extend_schema(tags=['User Profile'])
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
