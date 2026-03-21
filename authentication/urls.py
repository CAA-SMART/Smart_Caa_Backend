from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import ForgotPasswordView, ResetPasswordView

urlpatterns = [
    path('authentication/token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('authentication/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('authentication/verify/', TokenObtainPairView.as_view(), name='token_verify'),
    path('authentication/logout/', TokenObtainPairView.as_view(), name='token_logout'),
    path('authentication/forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('authentication/reset-password/', ResetPasswordView.as_view(), name='reset_password'),
]
