from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('authentication/token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('authentication/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('authentication/verify/', TokenObtainPairView.as_view(), name='token_verify'),
    path('authentication/logout/', TokenObtainPairView.as_view(), name='token_logout'),
]
