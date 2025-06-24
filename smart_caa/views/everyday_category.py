from rest_framework import generics
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema
from ..models import EverydayCategory
from ..serializers import EverydayCategorySerializer


@extend_schema(tags=['EverydayCategory'])
class EverydayCategoryCreateListView(generics.ListCreateAPIView):
    queryset = EverydayCategory.objects.all()
    serializer_class = EverydayCategorySerializer
    permission_classes = [AllowAny]  # Remove autenticação para testes
    
    @extend_schema(
        summary='Listar Categorias do Cotidiano',
        description='Utilizado para listar todas as categorias do cotidiano'
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary='Criar Categoria do Cotidiano',
        description='Utilizado para criar uma nova categoria do cotidiano'
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        # Comentado temporariamente para testes sem autenticação
        # serializer.save(created_by=self.request.user)
        serializer.save()


@extend_schema(tags=['EverydayCategory'])
class EverydayCategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = EverydayCategory.objects.all()
    serializer_class = EverydayCategorySerializer
    permission_classes = [AllowAny]  # Remove autenticação para testes
    
    @extend_schema(
        summary='Obter Categoria do Cotidiano',
        description='Utilizado para obter uma categoria do cotidiano específica'
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary='Atualizar Categoria do Cotidiano',
        description='Utilizado para atualizar completamente uma categoria do cotidiano'
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @extend_schema(
        summary='Atualizar Parcialmente Categoria do Cotidiano',
        description='Utilizado para atualizar parcialmente uma categoria do cotidiano'
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    @extend_schema(
        summary='Deletar Categoria do Cotidiano',
        description='Utilizado para deletar uma categoria do cotidiano'
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
