from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter
from ..models.attachment import Attachment
from ..serializers import AttachmentSerializer

@extend_schema(tags=['Attachment'])
class AttachmentCreateListView(generics.ListCreateAPIView):
    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        summary='Listar Anexos',
        description='Lista todos os anexos, com filtro por paciente',
        parameters=[
            OpenApiParameter(
                name='patient',
                type=int,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Filtrar anexos por paciente (ID)'
            )
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary='Criar Anexo',
        description='Cria um novo anexo para um paciente'
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        patient_id = self.request.query_params.get('patient')
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        return queryset

@extend_schema(tags=['Attachment'])
class AttachmentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        summary='Obter Anexo',
        description='Utilizado para obter um anexo específico'
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary='Atualizar Anexo',
        description='Utilizado para atualizar completamente um anexo'
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        summary='Atualizar Parcialmente Anexo',
        description='Utilizado para atualizar parcialmente um anexo'
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    @extend_schema(
        summary='Excluir Anexo',
        description='Exclui um anexo pelo ID'
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
