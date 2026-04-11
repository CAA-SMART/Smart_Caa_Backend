from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from django.shortcuts import get_object_or_404
from ..models import Anamnesis, Person
from ..serializers import (
    AnamnesisSerializer,
    AnamnesisListSerializer,
    CaregiverAnamnesisSerializer
)


ANAMNESIS_SWAGGER_EXAMPLE = OpenApiExample(
    'Ficha de anamnese - ordem por seções 1, 3 e 4',
    summary='Exemplo de payload da anamnese na mesma ordem do documento',
    value={
        'patient': 1,
        'caregiver': 2,
        'main_diagnosis': 'TEA',
        'associated_conditions': 'TDAH',
        'responsible_contact': 'Maria Silva - (11) 99999-0000',
        'reference_professional': 'Dra. Ana - Fonoaudióloga',
        'cognitive_level': 'Moderado',
        'auditory_comprehension': 'Compreende frases simples',
        'memory_profile': 'Melhor memória visual',
        'attention_duration': '10-15 minutos',
        'learning_pace': 'Normal',
        'language_style': 'Literal',
        'functional_speech': 'Sim, parcial',
        'speech_intelligibility': 'Pouco inteligível',
        'uses_gestures': True,
        'uses_signs': False,
        'uses_images_or_symbols': True,
        'preferred_symbol_systems': 'Arasaac, Fotografias',
        'symbol_comprehension': 'Muitos',
        'communication_priorities': 'Expressar necessidades, socializar'
    },
    request_only=True,
)


@extend_schema(tags=['Anamnesis'])
class AnamnesisCreateListView(generics.ListCreateAPIView):
    """
    View para listar e criar anamneses
    """
    serializer_class = AnamnesisSerializer
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
        description='Lista todas as anamneses ativas no sistema, seguindo a ordem das seções 1 (dados pessoais e diagnóstico), 3 (habilidades cognitivas) e 4 (comunicação atual). **Requer autenticação.**',
        responses={200: AnamnesisListSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary='Criar Anamnese',
        description='Cria uma nova anamnese para um paciente usando a ficha reestruturada com as seções 1 (dados pessoais e diagnóstico), 3 (habilidades cognitivas) e 4 (comunicação atual). Apenas uma anamnese por paciente/cuidador é permitida. **Requer autenticação.**',
        request=AnamnesisSerializer,
        responses={201: AnamnesisSerializer},
        examples=[ANAMNESIS_SWAGGER_EXAMPLE]
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
        description='Retorna os detalhes completos da anamnese na ordem das seções 1, 3 e 4 do documento.',
        responses={200: AnamnesisSerializer}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary='Atualizar Anamnese',
        description='Atualiza completamente uma anamnese específica preservando a ordem das seções 1, 3 e 4.',
        request=AnamnesisSerializer,
        responses={200: AnamnesisSerializer},
        examples=[ANAMNESIS_SWAGGER_EXAMPLE]
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @extend_schema(
        summary='Atualizar Parcialmente Anamnese',
        description='Atualiza parcialmente os campos da anamnese seguindo a ordem das seções 1, 3 e 4.',
        request=AnamnesisSerializer,
        responses={200: AnamnesisSerializer},
        examples=[ANAMNESIS_SWAGGER_EXAMPLE]
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
        description='Lista as anamneses criadas por um cuidador específico com os dados principais da ficha atualizada.',
        responses={200: CaregiverAnamnesisSerializer(many=True)}
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
        description='Lista todas as anamneses de um paciente específico com os campos completos na ordem das seções 1, 3 e 4.',
        responses={200: AnamnesisSerializer(many=True)}
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
        description='Retorna a anamnese de um paciente específico criada por um cuidador específico, incluindo os campos na ordem das seções 1, 3 e 4.',
        responses={200: AnamnesisSerializer}
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
        description='Cria uma anamnese para um paciente específico com a ficha reestruturada na ordem das seções 1, 3 e 4. O cuidador deve ser especificado no body da requisição.',
        request=AnamnesisSerializer,
        responses={201: AnamnesisSerializer},
        examples=[ANAMNESIS_SWAGGER_EXAMPLE]
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
        description='Retorna a anamnese usando IDs do paciente e cuidador como query parameters, incluindo os campos na ordem das seções 1, 3 e 4.',
        responses={200: AnamnesisSerializer},
        parameters=[
            OpenApiParameter(
                name='patient_id',
                type=int,
                location=OpenApiParameter.QUERY,
                required=True,
                description='ID do paciente'
            ),
            OpenApiParameter(
                name='caregiver_id',
                type=int,
                location=OpenApiParameter.QUERY,
                required=True,
                description='ID do cuidador'
            )
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
