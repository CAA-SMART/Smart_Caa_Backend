from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from ..models import Pictogram, EverydayCategory


class PictogramSerializer(serializers.ModelSerializer):
    """
    Serializer para Pictogram
    """
    created_by_username = serializers.CharField(
        source='created_by.username', 
        read_only=True,
        help_text="Nome do usuário que criou o pictograma"
    )
    
    category_name = serializers.CharField(
        source='category.name',
        read_only=True,
        help_text="Nome da categoria do pictograma"
    )
    
    # URLs completas para os arquivos
    image_url = serializers.SerializerMethodField(
        help_text="URL completa da imagem do pictograma"
    )
    
    audio_url = serializers.SerializerMethodField(
        help_text="URL completa do áudio do pictograma"
    )
    
    class Meta:
        model = Pictogram
        fields = [
            'id',
            'name',
            'description',
            'category',
            'category_name',
            'image',
            'image_url',
            'audio',
            'audio_url',
            'is_active',
            'created_by',
            'created_by_username',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']
        extra_kwargs = {
            'name': {
                'help_text': 'Nome do pictograma'
            },
            'description': {
                'help_text': 'Descrição adicional do pictograma'
            },
            'category': {
                'help_text': 'ID da categoria do cotidiano'
            },
            'image': {
                'help_text': 'Arquivo de imagem do pictograma'
            },
            'audio': {
                'help_text': 'Arquivo de áudio do pictograma (opcional)'
            },
            'is_active': {
                'help_text': 'Indica se o pictograma está ativo'
            },
            'id': {
                'help_text': 'ID único do pictograma'
            },
            'created_at': {
                'help_text': 'Data e hora de criação do pictograma'
            },
            'updated_at': {
                'help_text': 'Data e hora da última atualização'
            }
        }
    
    @extend_schema_field(serializers.CharField)
    def get_image_url(self, obj):
        """Retorna a URL completa da imagem"""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
    
    @extend_schema_field(serializers.CharField)
    def get_audio_url(self, obj):
        """Retorna a URL completa do áudio"""
        if obj.audio:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.audio.url)
            return obj.audio.url
        return None
    
    def create(self, validated_data):
        # O created_by será definido na view
        return super().create(validated_data)
    
    def validate_category(self, value):
        """Valida se a categoria está ativa"""
        if not value.is_active:
            raise serializers.ValidationError(
                "Não é possível criar pictograma em uma categoria inativa."
            )
        return value


class PictogramListSerializer(PictogramSerializer):
    """
    Serializer simplificado para listagem de pictogramas
    Remove campos de arquivo para otimizar performance
    """
    class Meta(PictogramSerializer.Meta):
        fields = [
            'id',
            'name',
            'description',
            'category',
            'category_name',
            'image_url',
            'audio_url',
            'is_active',
            'created_by_username',
            'created_at',
            'updated_at'
        ]
