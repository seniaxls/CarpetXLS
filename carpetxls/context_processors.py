# carpetxls/context_processors.py

import os

def dadata_token(request):
    """Добавляет DADATA_TOKEN в контекст шаблона"""
    return {
        'DADATA_TOKEN': os.getenv('DADATA_TOKEN')
    }