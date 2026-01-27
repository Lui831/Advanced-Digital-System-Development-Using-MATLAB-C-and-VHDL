"""
QEMULA Document Synchronization Module

Sistema de sincronização automática entre documentos .docx e help_tab.py

Módulos principais:
- docs_sync: Motor de sincronização principal
- qemula_auto_sync: Serviço de monitoramento automático 
- sync_integration: Interface de integração simplificada

Uso básico:
    from doc_sync.sync_integration import sync_help_documentation
    success = sync_help_documentation()
"""

__version__ = "1.0.0"
__author__ = "QEMULA Team"

# Importações principais para facilitar o uso
try:
    from .sync_integration import sync_help_documentation, get_documentation_status
    from .docs_sync import DocxContentExtractor, HelpTabUpdater
    
    __all__ = [
        'sync_help_documentation',
        'get_documentation_status', 
        'DocxContentExtractor',
        'HelpTabUpdater'
    ]
except ImportError:
    # Se as dependências não estiverem disponíveis
    __all__ = []
