"""
Chalice Offline Mode
Local model inference without internet dependency
"""
from .ollama_provider import OllamaProvider, get_ollama_provider
from .lmstudio_provider import LMStudioProvider, get_lmstudio_provider

__all__ = [
    'OllamaProvider',
    'get_ollama_provider',
    'LMStudioProvider',
    'get_lmstudio_provider'
]
