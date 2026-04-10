from rest_framework import serializers

from ..models import History


class HistorySerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(
        source='patient.name',
        read_only=True,
        help_text="Nome do paciente"
    )

    attachment_count = serializers.SerializerMethodField(
        help_text="Quantidade de anexos vinculados a este histórico"
    )

    caregiver_name = serializers.CharField(
        source='caregiver.name',
        read_only=True,
        help_text="Nome do cuidador"
    )

    created_by_username = serializers.CharField(
        source='created_by.username',
        read_only=True,
        help_text="Nome do usuário que criou o registro"
    )

    def get_attachment_count(self, obj) -> int:
        return getattr(obj, 'attachment_count', obj.attachments.filter(is_active=True).count())

    class Meta:
        model = History
        fields = [
            'id',
            'patient',
            'patient_name',
            'caregiver',
            'caregiver_name',
            'description',
            'attachment_count',
            'is_active',
            'created_by',
            'created_by_username',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']
        extra_kwargs = {
            'patient': {
                'help_text': 'ID do paciente relacionado ao histórico'
            },
            'caregiver': {
                'help_text': 'ID do cuidador relacionado ao histórico'
            },
            'description': {
                'help_text': 'Descrição textual do histórico'
            }
        }

    def validate_patient(self, value):
        if not value.is_patient:
            raise serializers.ValidationError(
                "A pessoa selecionada deve ser marcada como paciente."
            )
        return value

    def validate_caregiver(self, value):
        if not value.is_caregiver:
            raise serializers.ValidationError(
                "A pessoa selecionada deve ser marcada como cuidador."
            )
        return value
