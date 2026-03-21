from django.urls import path
from .views import (
    AuthenticationTokenObtainPairView,
    AuthenticationTokenRefreshView,
    ChangePasswordView,
    ForgotPasswordView,
)

urlpatterns = [
    path('authentication/token', AuthenticationTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('authentication/refresh/', AuthenticationTokenRefreshView.as_view(), name='token_refresh'),
    path('authentication/verify/', AuthenticationTokenObtainPairView.as_view(), name='token_verify'),
    path('authentication/logout/', AuthenticationTokenObtainPairView.as_view(), name='token_logout'),
    path('authentication/forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('authentication/change-password/', ChangePasswordView.as_view(), name='change_password'),
]
