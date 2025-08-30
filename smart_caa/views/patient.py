from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiParameter
from ..models import Person, PatientCaregiverRelationship, PatientPictogram, Pictogram
from ..serializers import (
    PatientSerializer, 
    CaregiverForPatientSerializer,
    PatientCaregiverRelationshipSerializer,
    PatientPictogramSerializer,
    PatientPictogramCreateSerializer,
    PatientPictogramBatchCreateSerializer,
    PictogramForPatientSerializer
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


@extend_schema(tags=['Patient'])
class PatientPictogramsListView(generics.ListAPIView):
    """
    View para listar todos os pictogramas de um paciente específico
    """
    serializer_class = PatientPictogramSerializer
    permission_classes = (IsAuthenticated,)
    
    def get_queryset(self):
        patient_id = self.kwargs['patient_id']
        return PatientPictogram.objects.filter(
            patient_id=patient_id,
            is_active=True
        ).select_related('pictogram', 'pictogram__category', 'created_by')
    
    @extend_schema(
        summary='Listar Pictogramas do Paciente',
        description='Utilizado para listar todos os pictogramas vinculados a um paciente específico'
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@extend_schema(tags=['Patient'])
class PatientPictogramCreateView(APIView):
    """
    View para vincular um ou múltiplos pictogramas a um paciente
    """
    permission_classes = (IsAuthenticated,)
    
    @extend_schema(
        summary='Vincular Pictograma(s) ao Paciente',
        description='Utilizado para criar vínculo(s) entre um paciente e pictograma(s). Para múltiplos pictogramas, envie um array no campo "pictograms".',
        request={
            'application/json': {
                'oneOf': [
                    {
                        'type': 'object',
                        'properties': {
                            'pictogram': {'type': 'integer', 'description': 'ID do pictograma (para vínculo único)'}
                        },
                        'required': ['pictogram']
                    },
                    {
                        'type': 'object', 
                        'properties': {
                            'pictograms': {
                                'type': 'array',
                                'items': {'type': 'integer'},
                                'description': 'Array de IDs dos pictogramas (para múltiplos vínculos)'
                            }
                        },
                        'required': ['pictograms']
                    }
                ]
            }
        },
        responses={
            201: PatientPictogramSerializer(many=True),
            400: "Dados inválidos"
        }
    )
    def post(self, request, *args, **kwargs):
        patient_id = self.kwargs['patient_id']
        
        # Verifica se é criação em lote ou única
        if 'pictograms' in request.data:
            # Criação em lote
            serializer = PatientPictogramBatchCreateSerializer(
                data=request.data, 
                context={'request': request, 'patient_id': patient_id}
            )
            
            if serializer.is_valid():
                created_links = serializer.save()
                
                # Retorna os objetos criados
                response_serializer = PatientPictogramSerializer(
                    created_links, 
                    many=True, 
                    context={'request': request}
                )
                
                return Response(
                    {
                        'message': f'{len(created_links)} pictogramas vinculados com sucesso.',
                        'data': response_serializer.data
                    },
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    serializer.errors, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            # Criação única (comportamento original)
            data = request.data.copy()
            data['patient'] = patient_id
            
            serializer = PatientPictogramCreateSerializer(
                data=data, 
                context={'request': request}
            )
            
            if serializer.is_valid():
                patient_pictogram = serializer.save(created_by=request.user)
                
                response_serializer = PatientPictogramSerializer(
                    patient_pictogram, 
                    context={'request': request}
                )
                
                return Response(
                    {
                        'message': 'Pictograma vinculado com sucesso.',
                        'data': response_serializer.data
                    },
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    serializer.errors, 
                    status=status.HTTP_400_BAD_REQUEST
                )


@extend_schema(tags=['Patient'])
class PatientPictogramDestroyView(generics.DestroyAPIView):
    """
    View para desvincular um pictograma de um paciente (inativar)
    """
    serializer_class = PatientPictogramSerializer
    permission_classes = (IsAuthenticated,)
    
    def get_queryset(self):
        patient_id = self.kwargs['patient_id']
        return PatientPictogram.objects.filter(
            patient_id=patient_id,
            is_active=True
        )
    
    @extend_schema(
        summary='Desvincular Pictograma do Paciente',
        description='Utilizado para desvincular um pictograma de um paciente (marca como inativo)'
    )
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Ao invés de deletar, marca como inativo
        instance.is_active = False
        instance.inactivated_by = request.user
        instance.inactivated_at = timezone.now()
        instance.save()
        
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=['Patient'])
class PatientAvailablePictogramsView(generics.ListAPIView):
    """
    View para listar pictogramas disponíveis para vincular ao paciente
    """
    serializer_class = PictogramForPatientSerializer
    permission_classes = (IsAuthenticated,)
    
    def get_queryset(self):
        patient_id = self.kwargs['patient_id']
        
        # Pictogramas já vinculados e ativos ao paciente
        linked_pictograms = PatientPictogram.objects.filter(
            patient_id=patient_id,
            is_active=True
        ).values_list('pictogram_id', flat=True)
        
        # Retorna pictogramas ativos que não estão vinculados ao paciente
        return Pictogram.objects.filter(
            is_active=True
        ).exclude(
            id__in=linked_pictograms
        ).select_related('category')
    
    @extend_schema(
        summary='Listar Pictogramas Disponíveis',
        description='Utilizado para listar pictogramas disponíveis para vincular ao paciente'
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
