from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, extend_schema
from drf_spectacular.types import OpenApiTypes
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import History, Person
from ..serializers import HistorySerializer


@extend_schema(tags=['History'])
class HistoryCreateListView(generics.ListCreateAPIView):
    serializer_class = HistorySerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = History.objects.filter(is_active=True)

        patient_id = self.request.query_params.get('patient_id')
        caregiver_id = self.request.query_params.get('caregiver_id')

        if patient_id:
            get_object_or_404(Person, id=patient_id, is_patient=True)
            queryset = queryset.filter(patient_id=patient_id)

        if caregiver_id:
            get_object_or_404(Person, id=caregiver_id, is_caregiver=True)
            queryset = queryset.filter(caregiver_id=caregiver_id)

        return queryset

    @extend_schema(
        summary='Listar Históricos',
        description='Lista históricos ativos. Permite filtros por patient_id e caregiver_id via query parameters.',
        parameters=[
            OpenApiParameter(
                name='patient_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Filtra históricos pelo ID do paciente.'
            ),
            OpenApiParameter(
                name='caregiver_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Filtra históricos pelo ID do cuidador.'
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary='Criar Histórico',
        description='Cria um novo histórico para paciente e cuidador.'
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


@extend_schema(tags=['History'])
class HistoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = HistorySerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return History.objects.filter(is_active=True)

    @extend_schema(
        summary='Obter Histórico',
        description='Retorna os detalhes de um histórico específico.'
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary='Atualizar Histórico',
        description='Atualiza completamente um histórico específico.'
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        summary='Atualizar Parcialmente Histórico',
        description='Atualiza parcialmente um histórico específico.'
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        summary='Deletar Histórico',
        description='Remove um histórico do sistema (soft delete).'
    )
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
