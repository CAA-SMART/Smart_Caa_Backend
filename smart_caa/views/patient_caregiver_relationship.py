from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from ..models import PatientCaregiverRelationship
from ..serializers import PatientCaregiverRelationshipSerializer, PatientCaregiverListSerializer


@extend_schema(tags=['Patient-Caregiver Relationship'])
class PatientCaregiverRelationshipListCreateView(generics.ListCreateAPIView):
    """
    View para listar e criar relacionamentos entre pacientes e cuidadores
    """
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return PatientCaregiverListSerializer
        return PatientCaregiverRelationshipSerializer
    
    def get_queryset(self):
        """Retorna relacionamentos ativos, com filtros opcionais"""
        queryset = PatientCaregiverRelationship.objects.select_related(
            'patient', 'caregiver', 'created_by'
        )
        
        # Filtros opcionais
        patient_id = self.request.query_params.get('patient', None)
        caregiver_id = self.request.query_params.get('caregiver', None)
        relationship_type = self.request.query_params.get('type', None)
        is_active = self.request.query_params.get('active', None)
        
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        if caregiver_id:
            queryset = queryset.filter(caregiver_id=caregiver_id)
        if relationship_type:
            queryset = queryset.filter(relationship_type=relationship_type)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset
    
    @extend_schema(
        summary='Listar Relacionamentos',
        description='Utilizado para listar relacionamentos entre pacientes e cuidadores. '
                   'Suporta filtros: ?patient=ID&caregiver=ID&type=TIPO&active=true/false'
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary='Criar Relacionamento',
        description='Utilizado para criar um novo relacionamento entre paciente e cuidador'
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        # Comentado temporariamente para testes sem autenticação
        # serializer.save(created_by=self.request.user)
        serializer.save()


@extend_schema(tags=['Patient-Caregiver Relationship'])
class PatientCaregiverRelationshipDetailView(generics.RetrieveUpdateAPIView):
    """
    View para obter e atualizar relacionamentos específicos
    """
    serializer_class = PatientCaregiverRelationshipSerializer
    permission_classes = [AllowAny]
    queryset = PatientCaregiverRelationship.objects.select_related(
        'patient', 'caregiver', 'created_by'
    )
    
    @extend_schema(
        summary='Obter Relacionamento',
        description='Utilizado para obter detalhes de um relacionamento específico'
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary='Atualizar Relacionamento',
        description='Utilizado para atualizar completamente um relacionamento'
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @extend_schema(
        summary='Atualizar Parcialmente Relacionamento',
        description='Utilizado para atualizar parcialmente um relacionamento'
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


@extend_schema(tags=['Patient-Caregiver Relationship'])
class PatientCaregiverRelationshipInactivateView(APIView):
    """
    View para inativar um relacionamento específico
    """
    permission_classes = [AllowAny]
    
    @extend_schema(
        summary='Inativar Relacionamento',
        description='Utilizado para inativar um relacionamento entre paciente e cuidador'
    )
    def post(self, request, pk):
        try:
            relationship = PatientCaregiverRelationship.objects.get(pk=pk)
            
            if not relationship.is_active:
                return Response(
                    {'detail': 'Este relacionamento já está inativo.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # relationship.inactivate(user=request.user)  # Descomentado quando tiver autenticação
            relationship.inactivate()
            
            serializer = PatientCaregiverRelationshipSerializer(relationship)
            return Response({
                'detail': 'Relacionamento inativado com sucesso.',
                'relationship': serializer.data
            })
            
        except PatientCaregiverRelationship.DoesNotExist:
            return Response(
                {'detail': 'Relacionamento não encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )
