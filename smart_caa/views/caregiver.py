from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_spectacular.utils import extend_schema
from ..models import Person, PatientCaregiverRelationship
from ..serializers import CaregiverSerializer, PatientForCaregiverSerializer


@extend_schema(tags=['Caregiver'])
class CaregiverCreateListView(generics.ListCreateAPIView):
    serializer_class = CaregiverSerializer
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'create' or self.request.method == 'POST':
            # Cadastro de cuidador é aberto (não precisa estar logado)
            permission_classes = [AllowAny]
        else:
            # Listagem de cuidadores requer autenticação
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """Retorna apenas pessoas que são cuidadores"""
        return Person.objects.filter(is_caregiver=True)
    
    @extend_schema(
        summary='Listar Cuidadores',
        description='Utilizado para listar todos os cuidadores cadastrados no sistema. **Requer autenticação.**'
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary='Cadastrar Cuidador',
        description='Utilizado para cadastrar um novo cuidador. Se o CPF já existir, a pessoa será marcada também como cuidador. Este endpoint não requer autenticação.'
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        # Se o usuário estiver autenticado, usar como created_by
        if self.request.user.is_authenticated:
            serializer.save(created_by=self.request.user)
        else:
            # Se não estiver autenticado, salvar sem created_by
            serializer.save()


@extend_schema(tags=['Caregiver'])
class CaregiverRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CaregiverSerializer
    permission_classes = (IsAuthenticated,)
    
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
    permission_classes = (IsAuthenticated,)
    
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
