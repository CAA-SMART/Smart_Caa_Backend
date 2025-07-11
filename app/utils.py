import os
import mimetypes
from django.conf import settings
from django.core.exceptions import ValidationError


def validate_file_extension(value):
    """
    Valida a extensão do arquivo enviado
    """
    if hasattr(value, 'name'):
        filename = value.name
    else:
        filename = value
    
    ext = os.path.splitext(filename)[1].lower()
    
    # Verificar se a extensão é permitida
    allowed_extensions = getattr(settings, 'ALLOWED_MEDIA_EXTENSIONS', [
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg',
        '.mp3', '.mp4', '.wav', '.m4a', '.pdf', '.doc', '.docx'
    ])
    
    if ext not in allowed_extensions:
        raise ValidationError(
            f'Tipo de arquivo não permitido: {ext}. '
            f'Tipos permitidos: {", ".join(allowed_extensions)}'
        )
    
    return value


def validate_file_size(value):
    """
    Valida o tamanho do arquivo enviado
    """
    if hasattr(value, 'size'):
        file_size = value.size
    else:
        return value
    
    max_size = getattr(settings, 'FILE_UPLOAD_MAX_MEMORY_SIZE', 5 * 1024 * 1024)  # 5MB
    
    if file_size > max_size:
        max_size_mb = max_size / (1024 * 1024)
        raise ValidationError(
            f'Arquivo muito grande: {file_size / (1024 * 1024):.1f}MB. '
            f'Tamanho máximo permitido: {max_size_mb:.1f}MB'
        )
    
    return value


def get_safe_filename(filename):
    """
    Retorna um nome de arquivo seguro, removendo caracteres perigosos
    """
    # Remover caracteres especiais e espaços
    import re
    safe_filename = re.sub(r'[^\w\-_\.]', '_', filename)
    safe_filename = re.sub(r'_+', '_', safe_filename)  # Remover múltiplos underscores
    return safe_filename.lower()


def get_content_type(file_path):
    """
    Retorna o tipo MIME do arquivo
    """
    content_type, _ = mimetypes.guess_type(file_path)
    return content_type or 'application/octet-stream'


def is_image_file(file_path):
    """
    Verifica se o arquivo é uma imagem
    """
    content_type = get_content_type(file_path)
    return content_type.startswith('image/')


def is_audio_file(file_path):
    """
    Verifica se o arquivo é um arquivo de áudio
    """
    content_type = get_content_type(file_path)
    return content_type.startswith('audio/')
