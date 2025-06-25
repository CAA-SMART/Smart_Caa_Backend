from rest_framework import generics
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema
from ..models import Person
from ..serializers import CaregiverSerializer


@extend_schema(tags=['Caregiver'])
class CaregiverCreateListView(generics.ListCreateAPIView):
    serializer_class = CaregiverSerializer
    permission_classes = [AllowAny]  # Remove autenticação para testes
    
    def get_queryset(self):
        """Retorna apenas pessoas que são cuidadores"""
        return Person.objects.filter(is_caregiver=True)
    
    @extend_schema(
        summary='Listar Cuidadores',
        description='Utilizado para listar todos os cuidadores cadastrados no sistema'
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary='Cadastrar Cuidador',
        description='Utilizado para cadastrar um novo cuidador. Se o CPF já existir, a pessoa será marcada também como cuidador.'
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        # Comentado temporariamente para testes sem autenticação
        # serializer.save(created_by=self.request.user)
        serializer.save()


@extend_schema(tags=['Caregiver'])
class CaregiverRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CaregiverSerializer
    permission_classes = [AllowAny]  # Remove autenticação para testes
    
    def get_queryset(self):
        """Retorna apenas pessoas que são cuidadores"""
        return Person.objects.filter(is_caregiver=True)
    
    @extend_schema(
        summary='Obter Cuidador',
        description='Utilizado para obter os dados de um cuidador específico'
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary='Atualizar Cuidador',
        description='Utilizado para atualizar completamente os dados de um cuidador'
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @extend_schema(
        summary='Atualizar Parcialmente Cuidador',
        description='Utilizado para atualizar parcialmente os dados de um cuidador'
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    @extend_schema(
        summary='Deletar Cuidador',
        description='Utilizado para deletar um cuidador do sistema'
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
