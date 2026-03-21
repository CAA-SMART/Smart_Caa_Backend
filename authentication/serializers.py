from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ChangePasswordSerializer(serializers.Serializer):
    username = serializers.CharField()
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        username = attrs.get('username')
        current_password = attrs.get('current_password')
        new_password = attrs.get('new_password')

        UserModel = self.context['user_model']
        user = UserModel.objects.filter(username=username, is_active=True).first()
        if not user:
            raise serializers.ValidationError({'username': 'Usuario nao encontrado.'})

        if not user.check_password(current_password):
            raise serializers.ValidationError({'current_password': 'Senha atual invalida.'})

        if current_password == new_password:
            raise serializers.ValidationError({'new_password': 'A nova senha deve ser diferente da senha atual.'})

        validate_password(new_password, user=user)

        attrs['user'] = user
        return attrs
