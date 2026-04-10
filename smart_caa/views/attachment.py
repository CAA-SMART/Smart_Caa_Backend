from rest_framework import generics
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, OpenApiResponse, extend_schema

from ..models.attachment import Attachment
from ..serializers import AttachmentSerializer

@extend_schema(tags=['Attachment'])
class AttachmentCreateListView(generics.ListCreateAPIView):
    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser)

    @extend_schema(
        summary='Listar Anexos',
        description='Lista todos os anexos, com filtro opcional por paciente e por histórico.',
        parameters=[
            OpenApiParameter(
                name='patient',
                type=int,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Filtrar anexos por paciente (ID)'
            ),
            OpenApiParameter(
                name='history_id',
                type=int,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Filtrar anexos por histórico (ID). Parâmetro recomendado.'
            ),
            OpenApiParameter(
                name='history',
                type=int,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Filtrar anexos por histórico (ID). Alias legado de `history_id`.'
            )
        ],
        responses={200: AttachmentSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary='Criar Anexo',
        description=(
            'Cria um novo anexo para um paciente via `multipart/form-data`. '
            'O campo `history` é opcional e deve receber o ID de um histórico do mesmo paciente, quando informado.'
        ),
        request=AttachmentSerializer,
        responses={
            201: AttachmentSerializer,
            400: OpenApiResponse(description='Dados inválidos')
        },
        examples=[
            OpenApiExample(
                'Criar anexo com histórico',
                summary='Exemplo com vínculo ao histórico',
                value={
                    'name': 'Relatório Terapêutico',
                    'patient': 1,
                    'history': 10,
                    'file': '<arquivo binário>'
                },
                request_only=True,
            ),
            OpenApiExample(
                'Criar anexo sem histórico',
                summary='Exemplo sem vínculo ao histórico',
                value={
                    'name': 'Receita Médica',
                    'patient': 1,
                    'file': '<arquivo binário>'
                },
                request_only=True,
            ),
        ]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        patient_id = self.request.query_params.get('patient')
        history_id = (
            self.request.query_params.get('history_id')
            or self.request.query_params.get('history')
        )

        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        if history_id:
            queryset = queryset.filter(history_id=history_id)

        return queryset

@extend_schema(tags=['Attachment'])
class AttachmentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser)

    @extend_schema(
        summary='Obter Anexo',
        description='Utilizado para obter um anexo específico.',
        responses={200: AttachmentSerializer}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary='Atualizar Anexo',
        description='Atualiza completamente um anexo. O campo `history` continua opcional.',
        request=AttachmentSerializer,
        responses={
            200: AttachmentSerializer,
            400: OpenApiResponse(description='Dados inválidos')
        }
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        summary='Atualizar Parcialmente Anexo',
        description='Atualiza parcialmente um anexo. Você pode enviar `history` com um ID válido ou `null`.',
        request=AttachmentSerializer,
        responses={
            200: AttachmentSerializer,
            400: OpenApiResponse(description='Dados inválidos')
        }
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    @extend_schema(
        summary='Excluir Anexo',
        description='Exclui um anexo pelo ID',
        responses={204: OpenApiResponse(description='Anexo excluído com sucesso')}
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
