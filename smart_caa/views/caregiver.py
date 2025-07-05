from rest_framework import generics
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema
from ..models import Person, PatientCaregiverRelationship
from ..serializers import CaregiverSerializer, PatientForCaregiverSerializer


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


@extend_schema(tags=['Caregiver'])
class CaregiverPatientsListView(generics.ListAPIView):
    """
    View para listar todos os pacientes de um cuidador específico
    """
    serializer_class = PatientForCaregiverSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        caregiver_id = self.kwargs['caregiver_id']
        return PatientCaregiverRelationship.objects.filter(
            caregiver_id=caregiver_id,
            is_active=True
        ).select_related('patient', 'caregiver')
    
    @extend_schema(
        summary='Listar Pacientes do Cuidador',
        description='Utilizado para listar todos os pacientes vinculados a um cuidador específico'
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
