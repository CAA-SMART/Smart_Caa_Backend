import os
import mimetypes
from django.http import Http404, HttpResponse, FileResponse, JsonResponse
from django.conf import settings
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control
from django.views.decorators.http import last_modified
from django.views.decorators.vary import vary_on_headers
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


@method_decorator(csrf_exempt, name='dispatch')
class SecureMediaView(View):
    """
    View para servir arquivos de mídia com controle de segurança
    Otimizada para PythonAnywhere
    """
    
    @method_decorator(cache_control(max_age=3600, public=True))
    @method_decorator(vary_on_headers('User-Agent'))
    def get(self, request, path):
        """
        Serve arquivos de mídia com validação de segurança
        """
        try:
            # Validar se o arquivo está dentro do diretório de mídia
            media_root = settings.MEDIA_ROOT
            file_path = os.path.join(media_root, path)
            
            # Normalizar o caminho para evitar problemas de traversal
            file_path = os.path.abspath(file_path)
            media_root = os.path.abspath(media_root)
            
            # Verificar se o arquivo existe
            if not os.path.exists(file_path):
                raise Http404(f"Arquivo não encontrado: {path}")
            
            # Verificar se o caminho não sai do diretório de mídia (segurança)
            if not file_path.startswith(media_root):
                raise Http404("Acesso negado")
            
            # Verificar se é um arquivo (não diretório)
            if not os.path.isfile(file_path):
                raise Http404("Arquivo não encontrado")
            
            # Determinar o tipo MIME
            content_type, _ = mimetypes.guess_type(file_path)
            if not content_type:
                # Tipos MIME específicos para arquivos comuns
                ext = os.path.splitext(file_path)[1].lower()
                content_type_map = {
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg',
                    '.png': 'image/png',
                    '.gif': 'image/gif',
                    '.bmp': 'image/bmp',
                    '.webp': 'image/webp',
                    '.svg': 'image/svg+xml',
                    '.mp3': 'audio/mpeg',
                    '.wav': 'audio/wav',
                    '.m4a': 'audio/mp4',
                    '.ogg': 'audio/ogg',
                }
                content_type = content_type_map.get(ext, 'application/octet-stream')
            
            # Ler o arquivo e retornar resposta
            with open(file_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type=content_type)
                response['Content-Length'] = os.path.getsize(file_path)
                response['Cache-Control'] = 'public, max-age=3600'
                response['X-Content-Type-Options'] = 'nosniff'
                
                # Headers específicos para imagens
                if content_type.startswith('image/'):
                    response['X-Frame-Options'] = 'SAMEORIGIN'
                
                return response
                
        except Exception as e:
            # Log do erro para debug
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Erro ao servir arquivo de mídia {path}: {str(e)}")
            raise Http404(f"Erro ao acessar o arquivo: {path}")


@method_decorator(csrf_exempt, name='dispatch')
class SecureStaticView(View):
    """
    View para servir arquivos estáticos com controle de segurança
    Otimizada para PythonAnywhere
    """
    
    @method_decorator(cache_control(max_age=86400, public=True))
    @method_decorator(vary_on_headers('User-Agent'))
    def get(self, request, path):
        """
        Serve arquivos estáticos com validação de segurança
        """
        try:
            # Validar se o arquivo está dentro do diretório estático
            static_root = settings.STATIC_ROOT
            file_path = os.path.join(static_root, path)
            
            # Normalizar o caminho
            file_path = os.path.abspath(file_path)
            static_root = os.path.abspath(static_root)
            
            # Verificar se o arquivo existe
            if not os.path.exists(file_path):
                raise Http404(f"Arquivo não encontrado: {path}")
            
            # Verificar se o caminho não sai do diretório estático (segurança)
            if not file_path.startswith(static_root):
                raise Http404("Acesso negado")
            
            # Verificar se é um arquivo (não diretório)
            if not os.path.isfile(file_path):
                raise Http404("Arquivo não encontrado")
            
            # Determinar o tipo MIME
            content_type, _ = mimetypes.guess_type(file_path)
            if not content_type:
                content_type = 'application/octet-stream'
            
            # Ler o arquivo e retornar resposta
            with open(file_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type=content_type)
                response['Content-Length'] = os.path.getsize(file_path)
                response['Cache-Control'] = 'public, max-age=86400'
                response['X-Content-Type-Options'] = 'nosniff'
                return response
                
        except Exception as e:
            # Log do erro para debug
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Erro ao servir arquivo estático {path}: {str(e)}")
            raise Http404(f"Erro ao acessar o arquivo: {path}")


@csrf_exempt
def debug_media_files(request):
    """
    View de debug para listar arquivos de mídia disponíveis
    """
    import os
    from django.conf import settings
    
    if not settings.DEBUG and not request.user.is_superuser:
        return JsonResponse({'error': 'Acesso negado'}, status=403)
    
    media_root = settings.MEDIA_ROOT
    files = []
    
    try:
        for root, dirs, filenames in os.walk(media_root):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                rel_path = os.path.relpath(file_path, media_root)
                url = settings.MEDIA_URL + rel_path.replace('\\', '/')
                
                files.append({
                    'filename': filename,
                    'path': rel_path.replace('\\', '/'),
                    'url': url,
                    'full_path': file_path,
                    'exists': os.path.exists(file_path),
                    'size': os.path.getsize(file_path) if os.path.exists(file_path) else 0
                })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({
        'media_root': media_root,
        'media_url': settings.MEDIA_URL,
        'files': files,
        'total_files': len(files)
    })


@csrf_exempt
def test_media_file(request, path):
    """
    View de teste para verificar se um arquivo específico existe
    """
    import os
    from django.conf import settings
    
    media_root = settings.MEDIA_ROOT
    file_path = os.path.join(media_root, path)
    
    return JsonResponse({
        'requested_path': path,
        'media_root': media_root,
        'full_path': file_path,
        'exists': os.path.exists(file_path),
        'is_file': os.path.isfile(file_path) if os.path.exists(file_path) else False,
        'size': os.path.getsize(file_path) if os.path.exists(file_path) else 0,
        'url': settings.MEDIA_URL + path
    })
