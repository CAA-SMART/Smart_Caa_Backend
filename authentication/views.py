from zoneinfo import ZoneInfo

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from smtplib import SMTPException
from django.template.loader import render_to_string
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import ChangePasswordSerializer, ForgotPasswordSerializer


@extend_schema(tags=['Authentication'])
class AuthenticationTokenObtainPairView(TokenObtainPairView):
    pass


@extend_schema(tags=['Authentication'])
class AuthenticationTokenRefreshView(TokenRefreshView):
    pass


@extend_schema(tags=['Authentication'])
class ForgotPasswordView(APIView):
    permission_classes = (AllowAny,)

    @extend_schema(
        summary='Solicitar redefinicao de senha',
        description='Recebe um e-mail e, se cadastrado, gera e envia uma nova senha temporaria.',
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
            'detail': 'Se o e-mail estiver cadastrado no sistema, voce recebera uma nova senha.'
        }

        if not user:
            return Response(success_response, status=status.HTTP_200_OK)

        # Gera senha temporaria com hora e minuto atuais no fuso de Sao Paulo.
        now_sp = timezone.now().astimezone(ZoneInfo('America/Sao_Paulo'))
        generated_password = f"smart{now_sp.strftime('%H%M')}"

        context = {
            'user': user,
            'generated_password': generated_password,
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

        user.set_password(generated_password)
        user.save(update_fields=['password'])

        return Response(success_response, status=status.HTTP_200_OK)


@extend_schema(tags=['Authentication'])
class ChangePasswordView(APIView):
    permission_classes = (AllowAny,)

    @extend_schema(
        summary='Alterar senha',
        description='Recebe usuario, senha atual e nova senha. Se validos, altera a senha.',
        request=ChangePasswordSerializer,
        responses={200: {'description': 'Senha alterada com sucesso'}, 400: {'description': 'Dados invalidos'}}
    )
    def post(self, request):
        user_model = get_user_model()
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'user_model': user_model},
        )
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        new_password = serializer.validated_data['new_password']

        user.set_password(new_password)
        user.save(update_fields=['password'])

        return Response({'detail': 'Senha alterada com sucesso.'}, status=status.HTTP_200_OK)
