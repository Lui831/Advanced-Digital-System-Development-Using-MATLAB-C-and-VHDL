import sys
import os
from pathlib import Path

# Configurar paths
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))
os.chdir(str(current_dir))

from docs_sync import DocxContentExtractor, HelpTabUpdater

print('🔍 Testando filtros melhorados...')
base_path = Path('..').resolve()
docs_path = base_path / 'docs'
help_tab_path = base_path / 'frontend' / 'help_tab.py'

extractor = DocxContentExtractor(docs_path)
documents = extractor.extract_all_documents()

for doc_name, doc_content in documents.items():
    print(f'\n📄 {doc_name}:')
    print(f'  Seções totais: {len(doc_content["sections"])}')
    
    updater = HelpTabUpdater(help_tab_path)
    if doc_name.lower() == 'qemula_user_manual':
        items = updater._process_user_manual(doc_content)
    elif doc_name.lower() == 'official_requirements':
        items = updater._process_requirements_doc(doc_content)
    else:
        items = [updater._process_generic_doc(doc_name, doc_content)]
    
    print(f'  Seções filtradas: {len(items)}')
    for i, (title, content) in enumerate(items[:5]):  # Mostrar só as primeiras 5
        print(f'    {i+1}. {title}')

print('\n🔄 Executando sincronização com filtros...')
updater = HelpTabUpdater(help_tab_path)
success = updater.update_help_tab(documents)
print(f'✅ Sincronização {"bem-sucedida" if success else "falhada"}')
