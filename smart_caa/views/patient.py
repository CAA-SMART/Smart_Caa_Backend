from rest_framework import generics, serializers, status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError, transaction
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    PolymorphicProxySerializer,
    extend_schema,
    inline_serializer,
)
from ..models import Person, PatientCaregiverRelationship, PatientPictogram, Pictogram
from ..serializers import (
    PatientSerializer, 
    CaregiverForPatientSerializer,
    PatientCaregiverRelationshipSerializer,
    PatientPictogramSerializer,
    PatientPictogramCreateSerializer,
    PatientCustomPictogramCreateSerializer,
    PatientPictogramBatchCreateSerializer,
    PatientPictogramDestroySerializer,
    PictogramForPatientSerializer
)


PATIENT_SWAGGER_EXAMPLE = OpenApiExample(
    'Cadastro de paciente com data de nascimento e gênero',
    summary='Exemplo de payload com os novos campos opcionais do paciente',
    value={
        'name': 'João Silva Teste',
        'cpf': '123.456.789-01',
        'email': 'joao.teste@gmail.com',
        'phone': '(11) 99999-1111',
        'birth_date': '2018-05-10',
        'gender': 'Masculino',
        'password': 'senhaSegura123',
        'cid': 'F84.0',
        'colors': 'Azul, Verde',
        'sounds': 'Música clássica',
        'smells': 'Lavanda',
        'hobbies': 'Pintura, Xadrez'
    },
    request_only=True,
)

PATIENT_PICTOGRAM_SINGLE_REQUEST = inline_serializer(
    name='PatientPictogramSingleRequest',
    fields={
        'pictogram': serializers.IntegerField(help_text='ID do pictograma para operação única')
    },
)

PATIENT_PICTOGRAM_BATCH_REQUEST = inline_serializer(
    name='PatientPictogramBatchRequest',
    fields={
        'pictograms': serializers.ListField(
            child=serializers.IntegerField(),
            help_text='Lista de IDs dos pictogramas para operação em lote'
        )
    },
)

PATIENT_PICTOGRAM_SINGLE_RESPONSE = inline_serializer(
    name='PatientPictogramSingleResponse',
    fields={
        'message': serializers.CharField(),
        'data': PatientPictogramSerializer(),
    },
)

PATIENT_PICTOGRAM_BATCH_RESPONSE = inline_serializer(
    name='PatientPictogramBatchResponse',
    fields={
        'message': serializers.CharField(),
        'data': PatientPictogramSerializer(many=True),
    },
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
        responses={200: PatientSerializer(many=True)},
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
        description='Utilizado para cadastrar um novo paciente. Os campos `birth_date` e `gender` são opcionais. Se o CPF já existir, a pessoa será marcada também como paciente. Este endpoint não requer autenticação.',
        request=PatientSerializer,
        responses={201: PatientSerializer},
        examples=[PATIENT_SWAGGER_EXAMPLE]
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
        description='Utilizado para obter os dados de um paciente específico',
        responses={200: PatientSerializer}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary='Atualizar Paciente',
        description='Utilizado para atualizar completamente os dados de um paciente',
        request=PatientSerializer,
        responses={200: PatientSerializer},
        examples=[PATIENT_SWAGGER_EXAMPLE]
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @extend_schema(
        summary='Atualizar Parcialmente Paciente',
        description='Utilizado para atualizar parcialmente os dados de um paciente',
        request=PatientSerializer,
        responses={200: PatientSerializer},
        examples=[PATIENT_SWAGGER_EXAMPLE]
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
    pagination_class = None
    
    def get_queryset(self):
        patient_id = self.kwargs['patient_id']
        queryset = PatientPictogram.objects.filter(
            patient_id=patient_id,
            is_active=True
        ).select_related('pictogram', 'pictogram__category', 'created_by')

        private = self.request.query_params.get('private')
        if private is not None:
            if private.lower() in ['true', '1']:
                queryset = queryset.filter(pictogram__private=True)
            elif private.lower() in ['false', '0']:
                queryset = queryset.filter(pictogram__private=False)

        return queryset
    
    @extend_schema(
        summary='Listar Pictogramas do Paciente',
        description='Utilizado para listar todos os pictogramas vinculados a um paciente específico. Opcionalmente pode filtrar por pictogramas privados usando `?private=true` ou `?private=false`.',
        parameters=[
            OpenApiParameter(
                name='private',
                type=bool,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Filtrar apenas pictogramas privados (`true`) ou públicos (`false`) do paciente.'
            )
        ]
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
        description='Cria um ou múltiplos vínculos entre um paciente e pictogramas. Se já existir vínculo inativo, ele será reativado automaticamente. **Exemplo:** `{ "pictogram": 1 }` ou `{ "pictograms": [1, 2, 3] }`.',
        request=PolymorphicProxySerializer(
            component_name='PatientPictogramCreateRequest',
            serializers=[
                PATIENT_PICTOGRAM_SINGLE_REQUEST,
                PATIENT_PICTOGRAM_BATCH_REQUEST,
            ],
            resource_type_field_name=None,
        ),
        responses={
            201: OpenApiResponse(
                response=PolymorphicProxySerializer(
                    component_name='PatientPictogramCreateResponse',
                    serializers=[
                        PATIENT_PICTOGRAM_SINGLE_RESPONSE,
                        PATIENT_PICTOGRAM_BATCH_RESPONSE,
                    ],
                    resource_type_field_name=None,
                ),
                description='Pictograma(s) vinculado(s) com sucesso.'
            ),
            400: OpenApiResponse(description='Dados inválidos')
        },
        examples=[
            OpenApiExample(
                'Vínculo único',
                summary='Payload para vincular um pictograma',
                value={'pictogram': 1},
                request_only=True,
            ),
            OpenApiExample(
                'Vínculo em lote',
                summary='Payload para vincular vários pictogramas',
                value={'pictograms': [1, 2, 3]},
                request_only=True,
            ),
            OpenApiExample(
                'Resposta vínculo único',
                value={
                    'message': 'Pictograma vinculado com sucesso.',
                    'data': {
                        'id': 10,
                        'pictogram': 1,
                        'pictogram_name': 'Água',
                        'pictogram_category': 'Rotina',
                        'pictogram_image_url': 'http://localhost:8000/media/pictograms/images/agua.png',
                        'pictogram_audio_url': None,
                        'pictogram_description': 'Beber água',
                        'is_active': True,
                        'created_at': '2026-04-11T10:00:00Z',
                        'created_by': 1,
                        'created_by_username': 'tester'
                    }
                },
                response_only=True,
                status_codes=['201'],
            ),
            OpenApiExample(
                'Resposta vínculo em lote',
                value={
                    'message': '3 pictogramas vinculados com sucesso.',
                    'data': [
                        {
                            'id': 10,
                            'pictogram': 1,
                            'pictogram_name': 'Água',
                            'pictogram_category': 'Rotina',
                            'pictogram_image_url': 'http://localhost:8000/media/pictograms/images/agua.png',
                            'pictogram_audio_url': None,
                            'pictogram_description': 'Beber água',
                            'is_active': True,
                            'created_at': '2026-04-11T10:00:00Z',
                            'created_by': 1,
                            'created_by_username': 'tester'
                        }
                    ]
                },
                response_only=True,
                status_codes=['201'],
            ),
        ]
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
class PatientCustomPictogramCreateView(APIView):
    """
    View para criar um pictograma personalizado privado e vinculá-lo
    ao paciente em uma única transação.
    """
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        summary='Adicionar Pictograma Personalizado',
        description='Cria um pictograma privado e já o vincula ao paciente em uma única operação. Se qualquer etapa falhar, nada é salvo.',
        request=PatientCustomPictogramCreateSerializer,
        responses={
            201: OpenApiResponse(
                response=PATIENT_PICTOGRAM_SINGLE_RESPONSE,
                description='Pictograma personalizado criado e vinculado com sucesso.'
            ),
            400: OpenApiResponse(description='Dados inválidos')
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = PatientCustomPictogramCreateSerializer(
            data=request.data,
            context={'request': request, 'patient_id': self.kwargs['patient_id']}
        )
        serializer.is_valid(raise_exception=True)

        try:
            with transaction.atomic():
                patient_pictogram = serializer.save()
        except (ValueError, DjangoValidationError, IntegrityError) as exc:
            return Response(
                {
                    'detail': 'Não foi possível adicionar o pictograma personalizado.',
                    'error': str(exc)
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception:
            return Response(
                {
                    'detail': 'Ocorreu um erro ao salvar o pictograma personalizado. Nenhum dado foi persistido.'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        response_serializer = PatientPictogramSerializer(
            patient_pictogram,
            context={'request': request}
        )

        return Response(
            {
                'message': 'Pictograma personalizado adicionado com sucesso.',
                'data': response_serializer.data
            },
            status=status.HTTP_201_CREATED
        )


@extend_schema(tags=['Patient'])
class PatientPictogramDestroyView(APIView):
    """
    View para desvincular um ou múltiplos pictogramas de um paciente,
    marcando os vínculos como inativos.
    """
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        summary='Desvincular Pictograma(s) do Paciente',
        description='Inativa um ou múltiplos vínculos entre um paciente e pictogramas. Os registros não são apagados da tabela. **Exemplo:** `{ "pictogram": 1 }` ou `{ "pictograms": [1, 2, 3] }`.',
        request=PolymorphicProxySerializer(
            component_name='PatientPictogramDestroyRequest',
            serializers=[
                PATIENT_PICTOGRAM_SINGLE_REQUEST,
                PATIENT_PICTOGRAM_BATCH_REQUEST,
            ],
            resource_type_field_name=None,
        ),
        responses={
            200: OpenApiResponse(
                response=PolymorphicProxySerializer(
                    component_name='PatientPictogramDestroyResponse',
                    serializers=[
                        PATIENT_PICTOGRAM_SINGLE_RESPONSE,
                        PATIENT_PICTOGRAM_BATCH_RESPONSE,
                    ],
                    resource_type_field_name=None,
                ),
                description='Pictograma(s) desvinculado(s) com sucesso.'
            ),
            400: OpenApiResponse(description='Dados inválidos')
        },
        examples=[
            OpenApiExample(
                'Desvinculação única',
                summary='Payload para desvincular um pictograma',
                value={'pictogram': 1},
                request_only=True,
            ),
            OpenApiExample(
                'Desvinculação em lote',
                summary='Payload para desvincular vários pictogramas',
                value={'pictograms': [1, 2, 3]},
                request_only=True,
            ),
            OpenApiExample(
                'Resposta desvinculação única',
                value={
                    'message': 'Pictograma desvinculado com sucesso.',
                    'data': {
                        'id': 10,
                        'pictogram': 1,
                        'pictogram_name': 'Água',
                        'pictogram_category': 'Rotina',
                        'pictogram_image_url': 'http://localhost:8000/media/pictograms/images/agua.png',
                        'pictogram_audio_url': None,
                        'pictogram_description': 'Beber água',
                        'is_active': False,
                        'created_at': '2026-04-11T10:00:00Z',
                        'created_by': 1,
                        'created_by_username': 'tester'
                    }
                },
                response_only=True,
                status_codes=['200'],
            ),
            OpenApiExample(
                'Resposta desvinculação em lote',
                value={
                    'message': '3 pictogramas desvinculados com sucesso.',
                    'data': [
                        {
                            'id': 10,
                            'pictogram': 1,
                            'pictogram_name': 'Água',
                            'pictogram_category': 'Rotina',
                            'pictogram_image_url': 'http://localhost:8000/media/pictograms/images/agua.png',
                            'pictogram_audio_url': None,
                            'pictogram_description': 'Beber água',
                            'is_active': False,
                            'created_at': '2026-04-11T10:00:00Z',
                            'created_by': 1,
                            'created_by_username': 'tester'
                        }
                    ]
                },
                response_only=True,
                status_codes=['200'],
            ),
        ]
    )
    def post(self, request, *args, **kwargs):
        patient_id = self.kwargs['patient_id']

        if 'pictograms' in request.data:
            serializer = PatientPictogramDestroySerializer(
                data=request.data,
                context={'request': request, 'patient_id': patient_id}
            )

            if serializer.is_valid():
                with transaction.atomic():
                    inactivated_links = serializer.save()

                response_serializer = PatientPictogramSerializer(
                    inactivated_links,
                    many=True,
                    context={'request': request}
                )

                return Response(
                    {
                        'message': f'{len(inactivated_links)} pictogramas desvinculados com sucesso.',
                        'data': response_serializer.data
                    },
                    status=status.HTTP_200_OK
                )

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if 'pictogram' in request.data:
            serializer = PatientPictogramDestroySerializer(
                data={'pictograms': [request.data.get('pictogram')]},
                context={'request': request, 'patient_id': patient_id}
            )

            if serializer.is_valid():
                with transaction.atomic():
                    inactivated_links = serializer.save()

                response_serializer = PatientPictogramSerializer(
                    inactivated_links[0],
                    context={'request': request}
                )

                return Response(
                    {
                        'message': 'Pictograma desvinculado com sucesso.',
                        'data': response_serializer.data
                    },
                    status=status.HTTP_200_OK
                )

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {'detail': 'Envie `pictogram` para desvinculação única ou `pictograms` para múltiplas desvinculações.'},
            status=status.HTTP_400_BAD_REQUEST
        )


@extend_schema(tags=['Patient'])
class PatientAvailablePictogramsView(generics.ListAPIView):
    """
    View para listar pictogramas disponíveis para vincular ao paciente
    """
    serializer_class = PictogramForPatientSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = None
    
    def get_queryset(self):
        patient_id = self.kwargs['patient_id']
        
        # Pictogramas já vinculados e ativos ao paciente
        linked_pictograms = PatientPictogram.objects.filter(
            patient_id=patient_id,
            is_active=True
        ).values_list('pictogram_id', flat=True)
        
        # Retorna apenas pictogramas públicos ativos que ainda não estão vinculados ao paciente
        return Pictogram.objects.filter(
            is_active=True,
            private=False,
        ).exclude(
            id__in=linked_pictograms
        ).select_related('category')
    
    @extend_schema(
        summary='Listar Pictogramas Disponíveis',
        description='Utilizado para listar pictogramas disponíveis para vincular ao paciente'
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
