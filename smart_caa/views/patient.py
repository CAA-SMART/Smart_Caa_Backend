from rest_framework import generics
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema
from ..models import Person
from ..serializers import PatientSerializer


@extend_schema(tags=['Patient'])
class PatientCreateListView(generics.ListCreateAPIView):
    serializer_class = PatientSerializer
    permission_classes = [AllowAny]  # Remove autenticação para testes
    
    def get_queryset(self):
        """Retorna apenas pessoas que são pacientes"""
        return Person.objects.filter(is_patient=True)
    
    @extend_schema(
        summary='Listar Pacientes',
        description='Utilizado para listar todos os pacientes cadastrados no sistema'
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary='Cadastrar Paciente',
        description='Utilizado para cadastrar um novo paciente. Se o CPF já existir, a pessoa será marcada também como paciente.'
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        # Comentado temporariamente para testes sem autenticação
        # serializer.save(created_by=self.request.user)
        serializer.save()


@extend_schema(tags=['Patient'])
class PatientRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PatientSerializer
    permission_classes = [AllowAny]  # Remove autenticação para testes
    
    def get_queryset(self):
        """Retorna apenas pessoas que são pacientes"""
        return Person.objects.filter(is_patient=True)
    
    @extend_schema(
        summary='Obter Paciente',
        description='Utilizado para obter os dados de um paciente específico'
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary='Atualizar Paciente',
        description='Utilizado para atualizar completamente os dados de um paciente'
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @extend_schema(
        summary='Atualizar Parcialmente Paciente',
        description='Utilizado para atualizar parcialmente os dados de um paciente'
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    @extend_schema(
        summary='Deletar Paciente',
        description='Utilizado para deletar um paciente do sistema'
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
