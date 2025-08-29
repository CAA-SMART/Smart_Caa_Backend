from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404
from ..models import Anamnesis, Person
from ..serializers import (
    AnamnesisSerializer,
    AnamnesisListSerializer,
    CaregiverAnamnesisSerializer
)


@extend_schema(tags=['Anamnesis'])
class AnamnesisCreateListView(generics.ListCreateAPIView):
    """
    View para listar e criar anamneses
    """
    permission_classes = (IsAuthenticated,)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AnamnesisSerializer
        return AnamnesisListSerializer
    
    def get_queryset(self):
        """Retorna todas as anamneses ativas"""
        return Anamnesis.objects.filter(is_active=True)
    
    @extend_schema(
        summary='Listar Anamneses',
        description='Lista todas as anamneses ativas no sistema. **Requer autenticação.**'
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary='Criar Anamnese',
        description='Cria uma nova anamnese para um paciente. Apenas uma anamnese por paciente/cuidador é permitida. **Requer autenticação.**'
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        """Define o usuário autenticado como criador"""
        serializer.save(created_by=self.request.user)


@extend_schema(tags=['Anamnesis'])
class AnamnesisRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    View para obter, atualizar e deletar uma anamnese específica
    """
    serializer_class = AnamnesisSerializer
    permission_classes = (IsAuthenticated,)
    
    def get_queryset(self):
        """Retorna todas as anamneses ativas"""
        return Anamnesis.objects.filter(is_active=True)
    
    @extend_schema(
        summary='Obter Anamnese',
        description='Retorna os detalhes de uma anamnese específica'
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary='Atualizar Anamnese',
        description='Atualiza completamente uma anamnese específica'
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @extend_schema(
        summary='Atualizar Parcialmente Anamnese',
        description='Atualiza parcialmente uma anamnese específica'
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    @extend_schema(
        summary='Deletar Anamnese',
        description='Remove uma anamnese do sistema (soft delete)'
    )
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=['Anamnesis'])
class CaregiverAnamnesisListView(generics.ListAPIView):
    """
    View para listar anamneses criadas por um cuidador específico
    """
    serializer_class = CaregiverAnamnesisSerializer
    permission_classes = (IsAuthenticated,)
    
    def get_queryset(self):
        caregiver_id = self.kwargs['caregiver_id']
        
        # Verifica se o cuidador existe e é realmente um cuidador
        caregiver = get_object_or_404(Person, id=caregiver_id, is_caregiver=True)
        
        return Anamnesis.objects.filter(
            caregiver=caregiver,
            is_active=True
        ).order_by('-created_at')
    
    @extend_schema(
        summary='Listar Anamneses de um Cuidador',
        description='Lista todas as anamneses criadas por um cuidador específico'
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@extend_schema(tags=['Anamnesis'])
class PatientAnamnesisListView(generics.ListAPIView):
    """
    View para listar anamneses de um paciente específico
    """
    serializer_class = AnamnesisSerializer
    permission_classes = (IsAuthenticated,)
    
    def get_queryset(self):
        patient_id = self.kwargs['patient_id']
        
        # Verifica se o paciente existe e é realmente um paciente
        patient = get_object_or_404(Person, id=patient_id, is_patient=True)
        
        return Anamnesis.objects.filter(
            patient=patient,
            is_active=True
        ).order_by('-created_at')
    
    @extend_schema(
        summary='Listar Anamneses de um Paciente',
        description='Lista todas as anamneses de um paciente específico'
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@extend_schema(tags=['Anamnesis'])
class PatientCaregiverAnamnesisView(generics.RetrieveAPIView):
    """
    View para obter a anamnese específica de um paciente criada por um cuidador
    """
    serializer_class = AnamnesisSerializer
    permission_classes = (IsAuthenticated,)
    
    def get_object(self):
        patient_id = self.kwargs['patient_id']
        caregiver_id = self.kwargs['caregiver_id']
        
        # Verifica se o paciente e cuidador existem
        patient = get_object_or_404(Person, id=patient_id, is_patient=True)
        caregiver = get_object_or_404(Person, id=caregiver_id, is_caregiver=True)
        
        # Busca a anamnese específica
        anamnesis = get_object_or_404(
            Anamnesis,
            patient=patient,
            caregiver=caregiver,
            is_active=True
        )
        
        return anamnesis
    
    @extend_schema(
        summary='Obter Anamnese Específica',
        description='Retorna a anamnese de um paciente específico criada por um cuidador específico'
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@extend_schema(tags=['Anamnesis'])
class CreatePatientAnamnesisView(generics.CreateAPIView):
    """
    View para criar anamnese para um paciente específico
    """
    serializer_class = AnamnesisSerializer
    permission_classes = (IsAuthenticated,)
    
    @extend_schema(
        summary='Criar Anamnese para Paciente',
        description='Cria uma anamnese para um paciente específico. O cuidador deve ser especificado no body da requisição.'
    )
    def post(self, request, *args, **kwargs):
        # Adiciona o patient_id do URL no data
        request.data['patient'] = self.kwargs['patient_id']
        return super().post(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        """Define o usuário autenticado como criador"""
        patient_id = self.kwargs['patient_id']
        patient = get_object_or_404(Person, id=patient_id, is_patient=True)
        
        serializer.save(
            patient=patient,
            created_by=self.request.user
        )


@extend_schema(tags=['Anamnesis'])
class GetAnamnesisView(generics.RetrieveAPIView):
    """
    View para obter anamnese por IDs do paciente e cuidador via query parameters
    """
    serializer_class = AnamnesisSerializer
    permission_classes = (IsAuthenticated,)
    
    def get_object(self):
        patient_id = self.request.query_params.get('patient_id')
        caregiver_id = self.request.query_params.get('caregiver_id')
        
        if not patient_id:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'patient_id': 'Este parâmetro é obrigatório.'})
        
        if not caregiver_id:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'caregiver_id': 'Este parâmetro é obrigatório.'})
        
        # Verifica se o paciente e cuidador existem
        patient = get_object_or_404(Person, id=patient_id, is_patient=True)
        caregiver = get_object_or_404(Person, id=caregiver_id, is_caregiver=True)
        
        # Busca a anamnese específica
        anamnesis = get_object_or_404(
            Anamnesis,
            patient=patient,
            caregiver=caregiver,
            is_active=True
        )
        
        return anamnesis
    
    @extend_schema(
        summary='Obter Anamnese por IDs',
        description='Retorna a anamnese usando IDs do paciente e cuidador como query parameters',
        parameters=[
            {
                'name': 'patient_id',
                'in': 'query',
                'required': True,
                'schema': {'type': 'integer'},
                'description': 'ID do paciente'
            },
            {
                'name': 'caregiver_id', 
                'in': 'query',
                'required': True,
                'schema': {'type': 'integer'},
                'description': 'ID do cuidador'
            }
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
