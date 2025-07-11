# Configuração de Arquivos de Mídia

Este documento explica como configurar corretamente o serviço de arquivos de mídia no Smart CAA Backend.

## � Problema Identificado - PythonAnywhere

### Situação Atual
- **Desenvolvimento**: ✅ Funciona (`http://localhost:8000/media/...`)
- **Produção**: ❌ Não funciona (`https://janioalexandre.pythonanywhere.com/media/...`)

### Causa
O PythonAnywhere não serve arquivos de mídia automaticamente quando `DEBUG = False`.

### Solução Implementada

1. **Views Customizadas** (`app/views.py`):
   - `SecureMediaView`: Serve arquivos de mídia com segurança
   - `SecureStaticView`: Serve arquivos estáticos
   - Views de debug para teste

2. **URLs Configuradas** (`app/urls.py`):
   ```python
   # Produção - serve via Django
   re_path(r'^media/(?P<path>.*)$', SecureMediaView.as_view(), name='secure-media'),
   ```

3. **Configurações** (`app/settings.py`):
   - Detecção automática do PythonAnywhere
   - Headers de cache apropriados
   - Configurações de segurança

## � Como Testar

### 1. Endpoints de Debug

```bash
# Listar todos os arquivos de mídia
https://janioalexandre.pythonanywhere.com/debug/media-files/

# Testar arquivo específico
https://janioalexandre.pythonanywhere.com/debug/test-media/pictograms/images/Ajuda.png
```

### 2. Teste Direto

```bash
# Arquivo que não funciona atualmente
https://janioalexandre.pythonanywhere.com/media/pictograms/images/Ajuda.png

# Deveria funcionar após o deploy
curl -I https://janioalexandre.pythonanywhere.com/media/pictograms/images/Ajuda.png
```

### 3. Script de Teste

Execute o script de teste:
```bash
python test_media_serving.py
```

## 📋 Checklist para Deploy

### No PythonAnywhere:

1. **Fazer upload dos arquivos**:
   - `app/views.py` (views customizadas)
   - `app/urls.py` (URLs atualizadas)
   - `app/settings.py` (configurações)

2. **Verificar estrutura de arquivos**:
   ```
   /home/janioalexandre/Smart-Caa-Backend/
   ├── media/
   │   └── pictograms/
   │       ├── images/
   │       │   ├── Ajuda.png
   │       │   ├── dor.jpeg
   │       │   └── comer.jpeg
   │       └── audio/
   │           ├── comer.m4a
   │           └── dor.m4a
   ```

3. **Recarregar a aplicação**:
   - Ir ao Dashboard do PythonAnywhere
   - Clicar em "Reload" na aplicação web

4. **Testar os endpoints**:
   - `/debug/media-files/` (lista arquivos)
   - `/media/pictograms/images/Ajuda.png` (arquivo específico)

## 📄 URLs de Exemplo

### Desenvolvimento
```
http://localhost:8000/media/pictograms/images/Ajuda.png
http://localhost:8000/media/pictograms/images/dor.jpeg
http://localhost:8000/media/pictograms/audio/comer.m4a
```

### Produção (após correção)
```
https://janioalexandre.pythonanywhere.com/media/pictograms/images/Ajuda.png
https://janioalexandre.pythonanywhere.com/media/pictograms/images/dor.jpeg
https://janioalexandre.pythonanywhere.com/media/pictograms/audio/comer.m4a
```

## � Troubleshooting

### 1. Se ainda não funcionar após deploy

**Verificar logs do erro**:
```python
# No dashboard do PythonAnywhere, ver "Error log"
# Procurar por erros relacionados a arquivos de mídia
```

**Verificar permissões**:
```bash
# No console do PythonAnywhere
ls -la media/pictograms/images/
# Devem ter permissão de leitura
```

### 2. Verificar configurações

**Verificar se DEBUG está correto**:
```python
# Em settings.py
DEBUG = False  # Para produção
```

**Verificar caminhos**:
```python
# Testar no console do PythonAnywhere
import os
from django.conf import settings
print("MEDIA_ROOT:", settings.MEDIA_ROOT)
print("Arquivo existe:", os.path.exists(os.path.join(settings.MEDIA_ROOT, "pictograms/images/Ajuda.png")))
```

### 3. Alternativa: Configuração via Static Files

Se a solução atual não funcionar, configure como arquivo estático:

```python
# settings.py
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'media'),
]
```

## � Próximos Passos

1. **Deploy imediato**: Fazer upload dos arquivos alterados
2. **Teste**: Verificar se os arquivos são servidos corretamente
3. **Otimização**: Considerar CDN para melhor performance
4. **Monitoramento**: Configurar logs para acompanhar acessos

## 📝 Comandos Úteis

```bash
# Verificar estrutura de arquivos
find media/ -type f -name "*.png" -o -name "*.jpeg" -o -name "*.m4a"

# Testar URL específica
curl -I https://janioalexandre.pythonanywhere.com/media/pictograms/images/Ajuda.png

# Ver logs de erro
tail -f logs/django.log
```
