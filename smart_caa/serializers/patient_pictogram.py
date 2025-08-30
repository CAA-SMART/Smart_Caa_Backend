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


class PatientPictogramBatchCreateSerializer(serializers.Serializer):
    """
    Serializer para criar múltiplas vinculações de pictogramas ao paciente
    """
    pictograms = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="Lista de IDs dos pictogramas a serem vinculados",
        allow_empty=False
    )
    
    def validate_pictograms(self, value):
        """
        Valida se os IDs dos pictogramas são válidos
        """
        from ..models import Pictogram
        
        # Verifica duplicatas
        if len(value) != len(set(value)):
            raise serializers.ValidationError(
                "A lista contém pictogramas duplicados."
            )
        
        # Verifica se todos os pictogramas existem e estão ativos
        existing_pictograms = Pictogram.objects.filter(
            id__in=value, 
            is_active=True
        )
        
        existing_ids = list(existing_pictograms.values_list('id', flat=True))
        invalid_ids = [pid for pid in value if pid not in existing_ids]
        
        if invalid_ids:
            raise serializers.ValidationError(
                f"Os seguintes IDs de pictogramas são inválidos ou inativos: {invalid_ids}"
            )
        
        return existing_pictograms
    
    def validate(self, attrs):
        """
        Valida se os pictogramas não estão já ativos para o paciente
        """
        # O patient será passado no contexto da view
        patient_id = self.context.get('patient_id')
        if not patient_id:
            raise serializers.ValidationError("ID do paciente não fornecido.")
        
        from ..models import Person
        try:
            patient = Person.objects.get(id=patient_id, is_patient=True, is_active=True)
        except Person.DoesNotExist:
            raise serializers.ValidationError("Paciente não encontrado.")
        
        pictograms = attrs.get('pictograms')
        
        # Verifica se algum pictograma já está ativo para o paciente
        existing_pictograms = PatientPictogram.objects.filter(
            patient=patient,
            pictogram__in=pictograms,
            is_active=True
        ).values_list('pictogram__name', flat=True)
        
        if existing_pictograms:
            existing_names = list(existing_pictograms)
            raise serializers.ValidationError(
                f"Os seguintes pictogramas já estão ativos para este paciente: {', '.join(existing_names)}"
            )
        
        attrs['patient'] = patient
        return attrs
    
    def create(self, validated_data):
        """
        Cria múltiplas vinculações de pictogramas ao paciente
        """
        patient = validated_data['patient']
        pictograms = validated_data['pictograms']
        created_by = None
        
        if 'request' in self.context:
            created_by = self.context['request'].user
        
        created_links = []
        for pictogram in pictograms:
            link = PatientPictogram.objects.create(
                patient=patient,
                pictogram=pictogram,
                created_by=created_by
            )
            created_links.append(link)
        
        return created_links


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
