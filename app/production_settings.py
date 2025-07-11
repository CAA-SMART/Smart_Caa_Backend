# Configurações específicas para produção

# Configurações de arquivos estáticos e mídia para produção
STATIC_FILE_SETTINGS = {
    'CACHE_CONTROL_MAX_AGE': 31536000,  # 1 ano
    'MEDIA_CACHE_CONTROL_MAX_AGE': 3600,  # 1 hora
    'ENABLE_COMPRESSION': True,
    'ENABLE_ETAGS': True,
}

# Configurações de segurança para arquivos
SECURE_FILE_SETTINGS = {
    'MAX_FILE_SIZE': 10 * 1024 * 1024,  # 10MB
    'ALLOWED_IMAGE_EXTENSIONS': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'],
    'ALLOWED_AUDIO_EXTENSIONS': ['.mp3', '.wav', '.m4a', '.ogg'],
    'ALLOWED_DOCUMENT_EXTENSIONS': ['.pdf'],
    'SCAN_UPLOADS': True,  # Escanear uploads em busca de malware (se disponível)
}

# Headers de segurança para arquivos
SECURE_HEADERS = {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Referrer-Policy': 'strict-origin-when-cross-origin',
}

# Configurações de CDN (para futuro uso)
CDN_SETTINGS = {
    'ENABLED': False,
    'BASE_URL': '',
    'CACHE_CONTROL': 'public, max-age=31536000',
}

# Configurações de backup de arquivos
BACKUP_SETTINGS = {
    'ENABLED': True,
    'BACKUP_MEDIA_FILES': True,
    'RETENTION_DAYS': 30,
}
