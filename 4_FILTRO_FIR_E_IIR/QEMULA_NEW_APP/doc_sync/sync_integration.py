"""
Integração do sistema de sincronização de documentos com update_resources.py

Este módulo permite que o update_resources.py execute automaticamente
a sincronização dos documentos .docx com o help_tab.py
"""

import os
import sys
from pathlib import Path

# Adicionar o diretório atual ao path para importar docs_sync
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

try:
    from docs_sync import DocxContentExtractor, HelpTabUpdater
except ImportError as e:
    print(f"Erro ao importar docs_sync: {e}")
    print("Certifique-se de que o arquivo docs_sync.py está no mesmo diretório")
    sys.exit(1)


def sync_help_documentation():
    """
    Função principal para sincronizar documentação
    Retorna True se bem-sucedida, False caso contrário
    """
    try:
        print("🔄 Iniciando sincronização da documentação...")
        
        # Configurar caminhos (ajustado para nova estrutura)
        base_path = Path(__file__).parent.parent  # Subir um nível da pasta doc_sync
        docs_path = base_path / 'docs'
        help_tab_path = base_path / 'frontend' / 'help_tab.py'
        
        # Verificar se os caminhos existem
        if not docs_path.exists():
            print(f"❌ Pasta de documentos não encontrada: {docs_path}")
            return False
            
        if not help_tab_path.exists():
            print(f"❌ Arquivo help_tab.py não encontrado: {help_tab_path}")
            return False
        
        # Extrair conteúdo dos documentos
        extractor = DocxContentExtractor(docs_path)
        documents = extractor.extract_all_documents()
        
        if not documents:
            print("⚠️ Nenhum documento .docx encontrado")
            return False
        
        print(f"📄 Documentos encontrados: {', '.join(documents.keys())}")
        
        # Atualizar help_tab
        updater = HelpTabUpdater(help_tab_path)
        success = updater.update_help_tab(documents)
        
        if success:
            print("✅ Documentação sincronizada com sucesso!")
            return True
        else:
            print("❌ Falha na sincronização da documentação")
            return False
            
    except Exception as e:
        print(f"❌ Erro durante sincronização: {e}")
        return False


def get_documentation_status():
    """
    Retorna informações sobre o status da documentação
    """
    try:
        base_path = Path(__file__).parent.parent  # Ajustado para nova estrutura
        docs_path = base_path / 'docs'
        help_tab_path = base_path / 'frontend' / 'help_tab.py'
        
        status = {
            'docs_path_exists': docs_path.exists(),
            'help_tab_exists': help_tab_path.exists(),
            'docx_files': [],
            'last_help_update': None
        }
        
        # Listar arquivos .docx
        if docs_path.exists():
            docx_files = list(docs_path.glob('*.docx'))
            status['docx_files'] = [
                {
                    'name': f.name,
                    'size': f.stat().st_size,
                    'modified': f.stat().st_mtime
                }
                for f in docx_files if not f.name.startswith('~')
            ]
        
        # Verificar última atualização do help_tab
        if help_tab_path.exists():
            status['last_help_update'] = help_tab_path.stat().st_mtime
        
        return status
        
    except Exception as e:
        print(f"Erro ao obter status da documentação: {e}")
        return None


if __name__ == "__main__":
    """Execução direta do script"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Sincronização de documentação QEMULA')
    parser.add_argument('--sync', action='store_true', help='Executar sincronização')
    parser.add_argument('--status', action='store_true', help='Mostrar status')
    
    args = parser.parse_args()
    
    if args.sync:
        success = sync_help_documentation()
        sys.exit(0 if success else 1)
    elif args.status:
        status = get_documentation_status()
        if status:
            print("📊 Status da Documentação:")
            print(f"  📁 Pasta docs existe: {'✅' if status['docs_path_exists'] else '❌'}")
            print(f"  📄 help_tab.py existe: {'✅' if status['help_tab_exists'] else '❌'}")
            print(f"  📚 Documentos .docx: {len(status['docx_files'])}")
            for doc in status['docx_files']:
                print(f"    - {doc['name']} ({doc['size']} bytes)")
    else:
        print("Use --sync para sincronizar ou --status para ver o status")
