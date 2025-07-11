from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiParameter
from ..models import Person, PatientCaregiverRelationship
from ..serializers import (
    PatientSerializer, 
    CaregiverForPatientSerializer,
    PatientCaregiverRelationshipSerializer
)


@extend_schema(tags=['Patient'])
class PatientCreateListView(generics.ListCreateAPIView):
    serializer_class = PatientSerializer
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.request.method == 'POST':
            # Cadastro de paciente é aberto (não precisa estar logado)
            permission_classes = [AllowAny]
        else:
            # Listagem de pacientes requer autenticação
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """Retorna apenas pessoas que são pacientes"""
        queryset = Person.objects.filter(is_patient=True)
        
        # Filtro por CPF se fornecido
        cpf = self.request.query_params.get('cpf', None)
        if cpf:
            # Remove formatação do CPF para busca flexível
            cpf_cleaned = ''.join(filter(str.isdigit, cpf))
            queryset = queryset.filter(cpf=cpf_cleaned)
        
        return queryset
    
    @extend_schema(
        summary='Listar Pacientes',
        description='Utilizado para listar todos os pacientes cadastrados no sistema. Opcionalmente pode filtrar por CPF usando o parâmetro ?cpf=12345678901. **Requer autenticação.**',
        parameters=[
            OpenApiParameter(
                name='cpf',
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description='CPF do paciente para filtrar (apenas números, sem formatação)'
            )
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary='Cadastrar Paciente',
        description='Utilizado para cadastrar um novo paciente. Se o CPF já existir, a pessoa será marcada também como paciente. Este endpoint não requer autenticação.'
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


@extend_schema(tags=['Patient'])
class PatientRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PatientSerializer
    permission_classes = (IsAuthenticated,)
    
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


@extend_schema(tags=['Patient'])
class PatientCaregiversListView(generics.ListAPIView):
    """
    View para listar todos os cuidadores de um paciente específico
    """
    serializer_class = CaregiverForPatientSerializer
    permission_classes = (IsAuthenticated,)
    
    def get_queryset(self):
        patient_id = self.kwargs['patient_id']
        return PatientCaregiverRelationship.objects.filter(
            patient_id=patient_id,
            is_active=True
        ).select_related('patient', 'caregiver')
    
    @extend_schema(
        summary='Listar Cuidadores do Paciente',
        description='Utilizado para listar todos os cuidadores vinculados a um paciente específico'
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@extend_schema(tags=['Patient'])
class PatientCaregiverCreateView(generics.CreateAPIView):
    """
    View para vincular um cuidador a um paciente
    """
    serializer_class = PatientCaregiverRelationshipSerializer
    permission_classes = (IsAuthenticated,)
    
    @extend_schema(
        summary='Vincular Cuidador ao Paciente',
        description='Utilizado para criar um vínculo entre um paciente e um cuidador'
    )
    def post(self, request, *args, **kwargs):
        # Adiciona o patient_id da URL aos dados
        patient_id = self.kwargs['patient_id']
        data = request.data.copy()
        data['patient'] = patient_id
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


@extend_schema(tags=['Patient'])
class PatientCaregiverDetailView(generics.RetrieveUpdateAPIView):
    """
    View para gerenciar um relacionamento específico entre paciente e cuidador
    """
    serializer_class = PatientCaregiverRelationshipSerializer
    permission_classes = (IsAuthenticated,)
    
    def get_queryset(self):
        patient_id = self.kwargs['patient_id']
        return PatientCaregiverRelationship.objects.filter(
            patient_id=patient_id
        )
    
    @extend_schema(
        summary='Obter Relacionamento',
        description='Utilizado para obter detalhes de um relacionamento específico'
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary='Atualizar Relacionamento',
        description='Utilizado para atualizar um relacionamento entre paciente e cuidador'
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @extend_schema(
        summary='Atualizar Parcialmente Relacionamento',
        description='Utilizado para atualizar parcialmente um relacionamento'
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
