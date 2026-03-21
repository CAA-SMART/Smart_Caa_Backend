from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from smtplib import SMTPException
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import ForgotPasswordSerializer, ResetPasswordSerializer


@extend_schema(tags=['Authentication'])
class ForgotPasswordView(APIView):
    permission_classes = (AllowAny,)

    @extend_schema(
        summary='Solicitar redefinicao de senha',
        description='Recebe um e-mail e envia instrucoes para redefinicao de senha.',
        request=ForgotPasswordSerializer,
        responses={200: {'description': 'Solicitacao processada com sucesso'}}
    )
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        user_model = get_user_model()
        user = user_model.objects.filter(email__iexact=email, is_active=True).first()

        # Resposta uniforme para evitar enumeracao de contas.
        success_response = {
            'detail': 'Se o e-mail estiver cadastrado, voce recebera instrucoes para redefinir sua senha.'
        }

        if not user:
            return Response(success_response, status=status.HTTP_200_OK)

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_url = f"{settings.FRONTEND_RESET_PASSWORD_URL}?uid={uid}&token={token}"

        context = {
            'user': user,
            'reset_url': reset_url,
            'app_name': 'Smart CAA',
        }

        subject = render_to_string('authentication/emails/password_reset_subject.txt', context).strip()
        message = render_to_string('authentication/emails/password_reset_body.txt', context)

        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
        except SMTPException:
            # Em homologacao/desenvolvimento, evita quebrar o endpoint por falha externa de SMTP.
            return Response(
                {'detail': 'Nao foi possivel enviar o e-mail no momento. Tente novamente mais tarde.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except Exception:
            return Response(
                {'detail': 'Falha inesperada ao processar a solicitacao.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(success_response, status=status.HTTP_200_OK)


@extend_schema(tags=['Authentication'])
class ResetPasswordView(APIView):
    permission_classes = (AllowAny,)

    @extend_schema(
        summary='Confirmar redefinicao de senha',
        description='Valida token de recuperacao e define a nova senha.',
        request=ResetPasswordSerializer,
        responses={200: {'description': 'Senha alterada com sucesso'}, 400: {'description': 'Dados invalidos'}}
    )
    def post(self, request):
        user_model = get_user_model()
        serializer = ResetPasswordSerializer(
            data=request.data,
            context={'user_model': user_model},
        )
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']

        if not default_token_generator.check_token(user, token):
            return Response({'detail': 'Token invalido ou expirado.'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save(update_fields=['password'])

        return Response({'detail': 'Senha redefinida com sucesso.'}, status=status.HTTP_200_OK)
