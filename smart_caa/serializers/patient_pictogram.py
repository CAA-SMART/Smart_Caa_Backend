from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from ..models import PatientPictogram, Pictogram


class PatientPictogramSerializer(serializers.ModelSerializer):
    """
    Serializer para PatientPictogram - usado para listar pictogramas do paciente
    """
    pictogram_name = serializers.CharField(source='pictogram.name', read_only=True)
    pictogram_category = serializers.CharField(source='pictogram.category.name', read_only=True)
    pictogram_image_url = serializers.SerializerMethodField()
    pictogram_audio_url = serializers.SerializerMethodField()
    pictogram_description = serializers.CharField(source='pictogram.description', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = PatientPictogram
        fields = [
            'id', 'pictogram', 'pictogram_name', 'pictogram_category',
            'pictogram_image_url', 'pictogram_audio_url', 'pictogram_description',
            'is_active', 'created_at', 'created_by', 'created_by_username'
        ]
        read_only_fields = ['created_by', 'created_at']
    
    @extend_schema_field(serializers.URLField(allow_null=True))
    def get_pictogram_image_url(self, obj):
        """Retorna URL completa da imagem do pictograma"""
        if obj.pictogram.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.pictogram.image.url)
        return None
    
    @extend_schema_field(serializers.URLField(allow_null=True))
    def get_pictogram_audio_url(self, obj):
        """Retorna URL completa do áudio do pictograma"""
        if obj.pictogram.audio:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.pictogram.audio.url)
        return None


class PatientPictogramCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para criar vinculação de pictograma ao paciente
    """
    
    class Meta:
        model = PatientPictogram
        fields = ['patient', 'pictogram']
        
    def validate(self, attrs):
        """
        Valida se o pictograma não está já ativo para o paciente
        """
        patient = attrs.get('patient')
        pictogram = attrs.get('pictogram')
        
        # Verifica se já existe uma vinculação ativa
        if PatientPictogram.objects.filter(
            patient=patient, 
            pictogram=pictogram, 
            is_active=True
        ).exists():
            raise serializers.ValidationError(
                "Este pictograma já está ativo para este paciente."
            )
        
        return attrs
    
    def create(self, validated_data):
        """
        Cria a vinculação do pictograma ao paciente
        """
        # Define o created_by se disponível no contexto
        if 'request' in self.context:
            validated_data['created_by'] = self.context['request'].user
        
        return super().create(validated_data)


class PictogramForPatientSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listar pictogramas disponíveis para vincular ao paciente
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    image_url = serializers.SerializerMethodField()
    audio_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Pictogram
        fields = [
            'id', 'name', 'category_name', 'description', 
            'image_url', 'audio_url', 'is_default'
        ]
    
    @extend_schema_field(serializers.URLField(allow_null=True))
    def get_image_url(self, obj):
        """Retorna URL completa da imagem"""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
        return None
    
    @extend_schema_field(serializers.URLField(allow_null=True))
    def get_audio_url(self, obj):
        """Retorna URL completa do áudio"""
        if obj.audio:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.audio.url)
        return None
