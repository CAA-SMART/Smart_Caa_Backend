from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from ..models import EverydayCategory


class EverydayCategorySerializer(serializers.ModelSerializer):
    """
    Serializer para Categoria do Cotidiano
    """
    created_by_username = serializers.CharField(
        source='created_by.username', 
        read_only=True,
        help_text="Nome do usuário que criou a categoria"
    )
    
    class Meta:
        model = EverydayCategory
        fields = [
            'id',
            'name',
            'is_active',
            'created_by',
            'created_by_username',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']
        extra_kwargs = {
            'name': {
                'help_text': 'Nome da categoria do cotidiano'
            },
            'is_active': {
                'help_text': 'Indica se a categoria está ativa'
            },
            'id': {
                'help_text': 'ID único da categoria'
            },
            'created_at': {
                'help_text': 'Data e hora de criação da categoria'
            },
            'updated_at': {
                'help_text': 'Data e hora da última atualização'
            }
        }
    
    def create(self, validated_data):
        # O created_by será definido na view
        return super().create(validated_data)
