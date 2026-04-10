from rest_framework import serializers

from ..models.attachment import Attachment


class AttachmentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    def get_file_url(self, obj) -> str:
        request = self.context.get('request')
        if request is not None:
            return request.build_absolute_uri(obj.file.url)
        return obj.file.url

    def validate(self, attrs):
        patient = attrs.get('patient', getattr(self.instance, 'patient', None))
        history = attrs.get('history', getattr(self.instance, 'history', None))

        if history is not None and patient is not None and history.patient_id != patient.id:
            raise serializers.ValidationError({
                'history': 'O histórico informado deve pertencer ao mesmo paciente do anexo.'
            })

        return attrs

    class Meta:
        model = Attachment
        fields = ['id', 'name', 'file', 'file_url', 'patient', 'history', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'history': {
                'help_text': 'ID do histórico relacionado ao anexo (opcional)',
                'required': False,
                'allow_null': True,
            }
        }
