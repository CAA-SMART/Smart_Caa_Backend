from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.urls import re_path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from .views import SecureMediaView, SecureStaticView, debug_media_files, test_media_file

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('smart_caa.urls')),
    path('', include('authentication.urls')),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # Debug endpoints (apenas para desenvolvimento e teste)
    path('debug/media-files/', debug_media_files, name='debug-media-files'),
    path('debug/test-media/<path:path>', test_media_file, name='test-media-file'),
]

# Servir arquivos de mídia e estáticos
if settings.DEBUG:
    # Desenvolvimento: usar static() helper
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    # Produção: usar views seguras customizadas
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', SecureMediaView.as_view(), name='secure-media'),
        re_path(r'^static/(?P<path>.*)$', SecureStaticView.as_view(), name='secure-static'),
    ]
