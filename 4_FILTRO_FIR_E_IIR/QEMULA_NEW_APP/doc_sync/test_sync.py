import sys
sys.path.append('c:/Users/felip/Desktop/GitHub/QEMULA_Oficial_Rep/QEMULA_NEW_APP/doc_sync')
from docs_sync import DocxContentExtractor, HelpTabUpdater
from pathlib import Path

base_path = Path('c:/Users/felip/Desktop/GitHub/QEMULA_Oficial_Rep/QEMULA_NEW_APP')
docs_path = base_path / 'docs'
help_tab_path = base_path / 'frontend' / 'help_tab.py'

extractor = DocxContentExtractor(docs_path)
updater = HelpTabUpdater(help_tab_path)

print('Extraindo documentos...')
documents = extractor.extract_all_documents()
print(f'Documentos encontrados: {list(documents.keys())}')

for doc_name, doc_content in documents.items():
    print(f'\n{doc_name}:')
    print(f'  Título: {doc_content["title"]}')
    print(f'  Seções: {len(doc_content["sections"])}')
    for i, section in enumerate(doc_content["sections"][:3]):  # Primeiras 3 seções
        print(f'    {i+1}. {section["title"]} ({len(section["content"])} parágrafos)')

print('\nAtualizando help_tab.py...')
success = updater.update_help_tab(documents)
print(f'Sucesso: {success}')
