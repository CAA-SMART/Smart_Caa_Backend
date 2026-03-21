from django.contrib.auth.password_validation import validate_password
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        uid = attrs.get('uid')
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')

        if new_password != confirm_password:
            raise serializers.ValidationError({'confirm_password': 'As senhas nao conferem.'})

        try:
            user_id = urlsafe_base64_decode(uid).decode()
        except Exception as exc:
            raise serializers.ValidationError({'uid': 'UID invalido.'}) from exc

        UserModel = self.context['user_model']
        user = UserModel.objects.filter(pk=user_id).first()
        if not user:
            raise serializers.ValidationError({'uid': 'Usuario nao encontrado.'})

        validate_password(new_password, user=user)

        attrs['user'] = user
        return attrs
