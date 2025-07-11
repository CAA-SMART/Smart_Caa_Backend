#!/usr/bin/env python
"""
Script para testar se os arquivos de mídia estão sendo servidos corretamente
no PythonAnywhere.

Para executar:
python test_media_serving.py
"""

import requests
import json

# URLs para teste
BASE_URL = "https://janioalexandre.pythonanywhere.com"
LOCAL_URL = "http://localhost:8000"

def test_media_file(base_url, file_path):
    """
    Testa se um arquivo de mídia específico está sendo servido
    """
    url = f"{base_url}/media/{file_path}"
    
    try:
        response = requests.get(url, timeout=10)
        
        print(f"URL: {url}")
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
        print(f"Content-Length: {response.headers.get('content-length', 'N/A')}")
        
        if response.status_code == 200:
            print("✅ Arquivo encontrado e servido com sucesso!")
        else:
            print("❌ Arquivo não encontrado ou erro no servidor")
            print(f"Resposta: {response.text[:200]}...")
        
        print("-" * 50)
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na requisição: {e}")
        print("-" * 50)


def test_debug_endpoint(base_url):
    """
    Testa o endpoint de debug para listar arquivos
    """
    url = f"{base_url}/debug/media-files/"
    
    try:
        response = requests.get(url, timeout=10)
        
        print(f"Debug URL: {url}")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Media Root: {data.get('media_root', 'N/A')}")
            print(f"✅ Media URL: {data.get('media_url', 'N/A')}")
            print(f"✅ Total Files: {data.get('total_files', 0)}")
            
            files = data.get('files', [])
            if files:
                print("\nArquivos encontrados:")
                for file_info in files[:5]:  # Mostrar apenas os primeiros 5
                    print(f"  - {file_info['filename']} ({file_info['size']} bytes)")
                    print(f"    URL: {file_info['url']}")
                    print(f"    Exists: {file_info['exists']}")
            else:
                print("❌ Nenhum arquivo encontrado")
        else:
            print("❌ Erro no endpoint de debug")
            print(f"Resposta: {response.text[:200]}...")
        
        print("-" * 50)
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na requisição: {e}")
        print("-" * 50)


def test_specific_file(base_url, file_path):
    """
    Testa um arquivo específico usando o endpoint de debug
    """
    url = f"{base_url}/debug/test-media/{file_path}"
    
    try:
        response = requests.get(url, timeout=10)
        
        print(f"Test URL: {url}")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Requested Path: {data.get('requested_path', 'N/A')}")
            print(f"✅ Full Path: {data.get('full_path', 'N/A')}")
            print(f"✅ Exists: {data.get('exists', False)}")
            print(f"✅ Is File: {data.get('is_file', False)}")
            print(f"✅ Size: {data.get('size', 0)} bytes")
            print(f"✅ URL: {data.get('url', 'N/A')}")
        else:
            print("❌ Erro no teste do arquivo")
            print(f"Resposta: {response.text[:200]}...")
        
        print("-" * 50)
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na requisição: {e}")
        print("-" * 50)


def main():
    print("=== TESTE DE ARQUIVOS DE MÍDIA ===")
    print()
    
    # Arquivos para testar
    test_files = [
        "pictograms/images/Ajuda.png",
        "pictograms/images/dor.jpeg",
        "pictograms/images/comer.jpeg",
        "pictograms/audio/comer.m4a",
        "pictograms/audio/dor.m4a",
    ]
    
    # Testar produção (PythonAnywhere)
    print("🚀 TESTANDO PRODUÇÃO (PythonAnywhere)")
    print("=" * 50)
    
    # Testar endpoint de debug
    test_debug_endpoint(BASE_URL)
    
    # Testar arquivos específicos
    for file_path in test_files:
        test_specific_file(BASE_URL, file_path)
        test_media_file(BASE_URL, file_path)
    
    print("\n" + "=" * 50)
    print("RESUMO:")
    print("1. Verifique se os arquivos existem no servidor")
    print("2. Verifique se as URLs estão corretas")
    print("3. Verifique se o DEBUG está configurado corretamente")
    print("4. Verifique os logs do servidor para erros")
    print("=" * 50)


if __name__ == "__main__":
    main()
