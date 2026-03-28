from rest_framework import serializers
from ..models.attachment import Attachment

class AttachmentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    def get_file_url(self, obj):
        request = self.context.get('request')
        if request is not None:
            return request.build_absolute_uri(obj.file.url)
        return obj.file.url

    class Meta:
        model = Attachment
        fields = ['id', 'name', 'file', 'file_url', 'patient', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
