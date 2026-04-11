from django.utils import timezone
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from ..models import EverydayCategory, PatientPictogram, Person, Pictogram


def _reactivate_or_create_patient_pictogram(patient, pictogram, created_by=None):
    existing_link = PatientPictogram.objects.filter(
        patient=patient,
        pictogram=pictogram,
    ).order_by('-created_at', '-id').first()

    if existing_link is not None:
        if not existing_link.is_active:
            existing_link.is_active = True
            existing_link.inactivated_at = None
            existing_link.inactivated_by = None

            update_fields = ['is_active', 'inactivated_at', 'inactivated_by', 'updated_at']
            if existing_link.created_by_id is None and created_by is not None:
                existing_link.created_by = created_by
                update_fields.append('created_by')

            existing_link.save(update_fields=update_fields)

        return existing_link

    return PatientPictogram.objects.create(
        patient=patient,
        pictogram=pictogram,
        created_by=created_by,
    )


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
        Cria a vinculação do pictograma ao paciente ou reativa um vínculo inativo existente.
        """
        created_by = None
        if 'request' in self.context:
            created_by = self.context['request'].user

        return _reactivate_or_create_patient_pictogram(
            patient=validated_data['patient'],
            pictogram=validated_data['pictogram'],
            created_by=created_by,
        )


class PatientCustomPictogramCreateSerializer(serializers.Serializer):
    """
    Serializer para criar um pictograma personalizado e vinculá-lo ao paciente
    em uma única operação.
    """
    name = serializers.CharField(max_length=100, help_text="Nome do pictograma")
    category = serializers.PrimaryKeyRelatedField(
        queryset=EverydayCategory.objects.filter(is_active=True),
        help_text="ID da categoria do cotidiano"
    )
    image = serializers.ImageField(help_text="Arquivo de imagem do pictograma")
    audio = serializers.FileField(
        required=False,
        allow_null=True,
        help_text="Arquivo de áudio do pictograma (opcional)"
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text="Descrição adicional do pictograma"
    )

    def validate(self, attrs):
        patient_id = self.context.get('patient_id')
        if not patient_id:
            raise serializers.ValidationError("ID do paciente não fornecido.")

        try:
            patient = Person.objects.get(id=patient_id, is_active=True)
        except Person.DoesNotExist:
            raise serializers.ValidationError("Paciente não encontrado.")

        if not patient.is_patient:
            raise serializers.ValidationError("A pessoa informada não é um paciente válido.")

        if Pictogram.objects.filter(
            name=attrs.get('name'),
            category=attrs.get('category'),
            is_active=True
        ).exists():
            raise serializers.ValidationError({
                'name': 'Já existe um pictograma ativo com este nome nesta categoria.'
            })

        attrs['patient'] = patient
        return attrs

    def create(self, validated_data):
        patient = validated_data.pop('patient')
        request = self.context.get('request')
        created_by = request.user if request and request.user.is_authenticated else None

        pictogram = None
        try:
            pictogram = Pictogram.objects.create(
                **validated_data,
                private=True,
                is_default=False,
                created_by=created_by,
            )
            return PatientPictogram.objects.create(
                patient=patient,
                pictogram=pictogram,
                created_by=created_by,
            )
        except Exception:
            if pictogram is not None:
                if pictogram.image:
                    pictogram.image.delete(save=False)
                if pictogram.audio:
                    pictogram.audio.delete(save=False)
            raise


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
        ou reativa vínculos inativos existentes.
        """
        patient = validated_data['patient']
        pictograms = validated_data['pictograms']
        created_by = None

        if 'request' in self.context:
            created_by = self.context['request'].user

        created_links = []
        for pictogram in pictograms:
            link = _reactivate_or_create_patient_pictogram(
                patient=patient,
                pictogram=pictogram,
                created_by=created_by,
            )
            created_links.append(link)

        return created_links


class PatientPictogramDestroySerializer(serializers.Serializer):
    """
    Serializer para desvincular um ou múltiplos pictogramas de um paciente,
    sem remover o histórico da tabela de vinculação.
    """
    pictograms = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="Lista de IDs dos pictogramas a serem desvinculados",
        allow_empty=False
    )

    def validate_pictograms(self, value):
        if len(value) != len(set(value)):
            raise serializers.ValidationError(
                "A lista contém pictogramas duplicados."
            )
        return value

    def validate(self, attrs):
        patient_id = self.context.get('patient_id')
        if not patient_id:
            raise serializers.ValidationError("ID do paciente não fornecido.")

        try:
            patient = Person.objects.get(id=patient_id, is_patient=True, is_active=True)
        except Person.DoesNotExist:
            raise serializers.ValidationError("Paciente não encontrado.")

        pictogram_ids = attrs.get('pictograms', [])
        active_links = list(
            PatientPictogram.objects.filter(
                patient=patient,
                pictogram_id__in=pictogram_ids,
                is_active=True
            ).select_related('pictogram')
        )

        active_ids = {link.pictogram_id for link in active_links}
        missing_ids = [pid for pid in pictogram_ids if pid not in active_ids]

        if missing_ids:
            raise serializers.ValidationError(
                f"Os seguintes pictogramas não estão vinculados ou já estão inativos para este paciente: {missing_ids}"
            )

        attrs['patient'] = patient
        attrs['links'] = active_links
        return attrs

    def create(self, validated_data):
        links = validated_data['links']
        request = self.context.get('request')
        inactivated_by = request.user if request and request.user.is_authenticated else None
        inactivated_at = timezone.now()

        for link in links:
            link.is_active = False
            link.inactivated_by = inactivated_by
            link.inactivated_at = inactivated_at
            link.save(update_fields=['is_active', 'inactivated_by', 'inactivated_at', 'updated_at'])

        return links


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
