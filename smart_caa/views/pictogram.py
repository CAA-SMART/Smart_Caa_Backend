from rest_framework import generics
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema
from ..models import Pictogram
from ..serializers import PictogramSerializer


@extend_schema(tags=['Pictogram'])
class PictogramCreateListView(generics.ListCreateAPIView):
    queryset = Pictogram.objects.all()
    serializer_class = PictogramSerializer
    permission_classes = [AllowAny]  # Remove autenticação para testes
    
    @extend_schema(
        summary='Listar Pictogramas',
        description='Utilizado para listar todos os pictogramas'
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary='Criar Pictograma',
        description='Utilizado para criar um novo pictograma'
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        # Comentado temporariamente para testes sem autenticação
        # serializer.save(created_by=self.request.user)
        serializer.save()
    
    def get_queryset(self):
        """Otimiza as consultas incluindo a categoria relacionada"""
        return Pictogram.objects.select_related('category', 'created_by')


@extend_schema(tags=['Pictogram'])
class PictogramRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Pictogram.objects.all()
    serializer_class = PictogramSerializer
    permission_classes = [AllowAny]  # Remove autenticação para testes
    
    @extend_schema(
        summary='Obter Pictograma',
        description='Utilizado para obter um pictograma específico'
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary='Atualizar Pictograma',
        description='Utilizado para atualizar completamente um pictograma'
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @extend_schema(
        summary='Atualizar Parcialmente Pictograma',
        description='Utilizado para atualizar parcialmente um pictograma'
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    @extend_schema(
        summary='Deletar Pictograma',
        description='Utilizado para deletar um pictograma'
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
    
    def get_queryset(self):
        """Otimiza as consultas incluindo a categoria relacionada"""
        return Pictogram.objects.select_related('category', 'created_by')
