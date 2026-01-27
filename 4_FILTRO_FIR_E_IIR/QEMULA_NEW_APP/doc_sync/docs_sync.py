"""
Sistema de sincronização automática entre documentos .docx e help_tab.py

Este script:
1. Extrai conteúdo dos documentos .docx na pasta docs/
2. Atualiza automaticamente o help_tab.py
3. Monitora mudanças nos documentos para sincronização automática
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path
from docx import Document
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import re


class DocxContentExtractor:
    """Extrai conteúdo estruturado de documentos .docx"""
    
    def __init__(self, docs_path):
        self.docs_path = Path(docs_path)
        
    def extract_document_content(self, docx_path):
        """Extrai conteúdo de um documento .docx"""
        try:
            doc = Document(docx_path)
            content = {
                'title': '',
                'sections': [],
                'full_text': '',
                'metadata': {
                    'file': str(docx_path),
                    'last_modified': os.path.getmtime(docx_path),
                    'extracted_at': datetime.now().isoformat()
                }
            }
            
            # Extrair texto completo e estrutura
            full_text_parts = []
            current_section = None
            
            for paragraph in doc.paragraphs:
                text = paragraph.text.strip()
                if not text:
                    continue
                    
                full_text_parts.append(text)
                
                # Detectar títulos e seções baseado no estilo
                style_name = paragraph.style.name.lower() if paragraph.style else ''
                
                # Se é um título (primeiro parágrafo não vazio ou estilo de heading)
                if not content['title'] and text:
                    content['title'] = text
                elif 'heading' in style_name or self._is_likely_heading(text):
                    # Novo section
                    if current_section:
                        content['sections'].append(current_section)
                    current_section = {
                        'title': text,
                        'content': [],
                        'style': style_name
                    }
                elif current_section:
                    current_section['content'].append(text)
                else:
                    # Texto antes de qualquer seção
                    if not content['sections']:
                        content['sections'].append({
                            'title': 'Introduction',
                            'content': [text],
                            'style': 'normal'
                        })
                    else:
                        content['sections'][0]['content'].append(text)
            
            # Adicionar última seção
            if current_section:
                content['sections'].append(current_section)
            
            content['full_text'] = '\n\n'.join(full_text_parts)
            
            return content
            
        except Exception as e:
            print(f"Erro ao extrair conteúdo de {docx_path}: {e}")
            return None
    
    def _is_likely_heading(self, text):
        """Detecta se um texto é provavelmente um título"""
        text_lower = text.lower().strip()
        
        # Ignorar textos muito longos para serem títulos
        if len(text) > 200:
            return False
            
        # Ignorar textos sobre tabelas
        table_keywords = ['table of', 'tabela de', 'signature', 'assinatura']
        if any(keyword in text_lower for keyword in table_keywords):
            return False
            
        # Heurísticas para detectar títulos
        if len(text) < 100 and (
            text.isupper() or 
            text.endswith(':') or
            re.match(r'^\d+\.?\s+[A-Z]', text) or  # Numerados
            all(word[0].isupper() for word in text.split() if word.isalpha() and len(word) > 2)  # Title Case
        ):
            return True
        return False
    
    def extract_all_documents(self):
        """Extrai conteúdo de todos os documentos .docx"""
        documents = {}
        
        for docx_file in self.docs_path.glob('*.docx'):
            if not docx_file.name.startswith('~'):  # Ignorar arquivos temporários
                print(f"Extraindo conteúdo de: {docx_file.name}")
                content = self.extract_document_content(docx_file)
                if content:
                    documents[docx_file.stem] = content
        
        return documents


class HelpTabUpdater:
    """Atualiza o help_tab.py com conteúdo dos documentos"""
    
    def __init__(self, help_tab_path):
        self.help_tab_path = Path(help_tab_path)
        self.backup_path = self.help_tab_path.with_suffix('.py.backup')
        
    def create_backup(self):
        """Cria backup do arquivo atual"""
        if self.help_tab_path.exists():
            import shutil
            shutil.copy2(self.help_tab_path, self.backup_path)
            print(f"Backup criado: {self.backup_path}")
    
    def convert_documents_to_help_items(self, documents):
        """Converte documentos extraídos em itens de ajuda"""
        help_items = []
        
        for doc_name, doc_content in documents.items():
            # Processar cada documento
            if doc_name.lower() == 'official_requirements':
                help_items.extend(self._process_requirements_doc(doc_content))
            elif doc_name.lower() == 'qemula_user_manual':
                help_items.extend(self._process_user_manual(doc_content))
            else:
                # Documento genérico
                help_items.append(self._process_generic_doc(doc_name, doc_content))
        
        return help_items
    
    def _process_requirements_doc(self, doc_content):
        """Processa documento de requisitos"""
        items = []
        
        # Filtros para ignorar seções indesejadas
        ignored_titles = {
            'table of signatures',
            'tabela de assinaturas',
            'signatures', 
            'assinaturas',
            'table of contents',
            'índice',
            'sumário'
        }
        
        ignored_content_keywords = [
            'table of signatures',
            'tabela de assinaturas',
            'signature table',
            'table of contents',
            'sumário',
            'índice'
        ]
        
        # Filtrar seções válidas
        valid_sections = []
        seen_titles = set()
        
        for section in doc_content['sections']:
            section_title = section['title'].lower().strip()
            section_content = '\n'.join(section['content']).lower()
            
            # Ignorar seções vazias
            if len(section['content']) == 0:
                continue
                
            # Ignorar títulos indesejados
            if section_title in ignored_titles:
                continue
                
            # Ignorar seções com conteúdo sobre tabelas/índices
            if any(keyword in section_content for keyword in ignored_content_keywords):
                continue
                
            # Ignorar seções muito pequenas (menos de 30 caracteres)
            if len(section_content) < 30:
                continue
                
            # Evitar duplicatas - renomear se necessário
            if section_title in seen_titles:
                original_title = section['title']
                counter = 2
                while f"{section_title} ({counter})" in seen_titles:
                    counter += 1
                section_title = f"{section_title} ({counter})"
                section['title'] = f"{original_title} ({counter})"
            
            seen_titles.add(section_title)
            valid_sections.append(section)
        
        # Se temos seções válidas, criar itens de ajuda
        if valid_sections:
            # Agrupar seções relacionadas se necessário
            for section in valid_sections:
                section_text = '\n\n'.join(section['content'])
                items.append((section['title'], f"""
{section_text}

Last Updated: {datetime.fromisoformat(doc_content['metadata']['extracted_at']).strftime('%Y-%m-%d %H:%M')}
Source: {Path(doc_content['metadata']['file']).name}
                """.strip()))
        else:
            # Fallback: usar texto completo se não há seções válidas
            requirements_text = self._format_sections_text(doc_content['sections'])
            items.append(("System Requirements", f"""
{doc_content['title']}

{requirements_text}

Last Updated: {datetime.fromisoformat(doc_content['metadata']['extracted_at']).strftime('%Y-%m-%d %H:%M')}
Source: {Path(doc_content['metadata']['file']).name}
            """.strip()))
        
        return items
    
    def _process_user_manual(self, doc_content):
        """Processa manual do usuário"""
        items = []
        
        # Filtros para ignorar seções indesejadas
        ignored_titles = {
            'table of signatures',
            'tabela de assinaturas', 
            'signatures',
            'assinaturas'
        }
        
        ignored_content_keywords = [
            'table of signatures',
            'tabela de assinaturas',
            'signature table',
            'tabela de',
            'table of'
        ]
        
        seen_titles = set()  # Para evitar duplicatas
        
        # Dividir em seções lógicas baseadas no conteúdo
        for section in doc_content['sections']:
            section_title = section['title'].lower().strip()
            section_content = '\n'.join(section['content']).lower()
            
            # Ignorar seções vazias
            if len(section['content']) == 0:
                continue
                
            # Ignorar títulos indesejados
            if section_title in ignored_titles:
                continue
                
            # Ignorar seções com conteúdo sobre tabelas
            if any(keyword in section_content for keyword in ignored_content_keywords):
                continue
                
            # Ignorar seções muito pequenas (menos de 50 caracteres)
            if len(section_content) < 50:
                continue
                
            # Verificar se o conteúdo principal é só sobre tabela
            content_lines = [line.strip() for line in section['content'] if line.strip()]
            if len(content_lines) <= 2 and any('table' in line.lower() or 'tabela' in line.lower() for line in content_lines):
                continue
                
            # Evitar duplicatas de títulos
            if section_title in seen_titles:
                # Se já existe, adicionar um sufixo
                original_title = section['title']
                counter = 2
                while f"{section_title} ({counter})" in seen_titles:
                    counter += 1
                section_title = f"{section_title} ({counter})"
                section['title'] = f"{original_title} ({counter})"
            
            seen_titles.add(section_title)
            
            section_text = '\n\n'.join(section['content'])
            items.append((section['title'], f"""
{section_text}

Last Updated: {datetime.fromisoformat(doc_content['metadata']['extracted_at']).strftime('%Y-%m-%d %H:%M')}
Source: {Path(doc_content['metadata']['file']).name}
            """.strip()))
        
        return items
    
    def _process_generic_doc(self, doc_name, doc_content):
        """Processa documento genérico"""
        content_text = self._format_sections_text(doc_content['sections'])
        
        return (doc_name.replace('_', ' ').title(), f"""
{doc_content['title']}

{content_text}

Last Updated: {datetime.fromisoformat(doc_content['metadata']['extracted_at']).strftime('%Y-%m-%d %H:%M')}
Source: {Path(doc_content['metadata']['file']).name}
        """.strip())
    
    def _format_sections_text(self, sections):
        """Formata seções em texto"""
        formatted_sections = []
        
        for section in sections:
            if section['title'] and section['content']:
                section_text = f"{section['title']}:\n" + '\n'.join(section['content'])
                formatted_sections.append(section_text)
            elif section['content']:
                formatted_sections.append('\n'.join(section['content']))
        
        return '\n\n'.join(formatted_sections)
    
    def update_help_tab(self, documents):
        """Atualiza o arquivo help_tab.py"""
        try:
            # Criar backup
            self.create_backup()
            
            # Converter documentos em itens de ajuda
            new_help_items = self.convert_documents_to_help_items(documents)
            
            # Ler arquivo atual
            with open(self.help_tab_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Encontrar início e fim da lista help_items
            start_pattern = 'help_items = ['
            end_pattern = '        ]'
            
            start_pos = content.find(start_pattern)
            if start_pos == -1:
                raise ValueError("Não foi possível encontrar 'help_items = [' no arquivo")
            
            # Procurar o final da lista (após o start_pos)
            temp_content = content[start_pos:]
            bracket_count = 0
            end_pos = start_pos
            
            for i, char in enumerate(temp_content):
                if char == '[':
                    bracket_count += 1
                elif char == ']':
                    bracket_count -= 1
                    if bracket_count == 0:
                        end_pos = start_pos + i + 1
                        break
            
            if bracket_count != 0:
                raise ValueError("Não foi possível encontrar o final da lista help_items")
            
            # Gerar nova lista de itens
            items_code = self._generate_help_items_code(new_help_items)
            
            # Construir novo conteúdo
            new_list = f'help_items = [\n{items_code}\n        ]'
            new_content = content[:start_pos] + new_list + content[end_pos:]
            
            # Adicionar header com informações de sincronização se não existir
            if 'Auto-generated content from .docx documents' not in new_content:
                sync_info = f'''"""
Auto-generated content from .docx documents
Last sync: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Documents processed: {', '.join(documents.keys())}
"""

'''
                
                # Inserir após os imports
                import_end = new_content.find('class AccordionItem')
                if import_end != -1:
                    new_content = new_content[:import_end] + sync_info + new_content[import_end:]
            else:
                # Atualizar informações existentes
                sync_pattern = r'"""[\s\S]*?Auto-generated content from \.docx documents[\s\S]*?Documents processed:.*?\n"""'
                sync_info = f'''"""
Auto-generated content from .docx documents
Last sync: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Documents processed: {', '.join(documents.keys())}
"""'''
                new_content = re.sub(sync_pattern, sync_info, new_content)
            
            # Salvar arquivo atualizado
            with open(self.help_tab_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"help_tab.py atualizado com {len(new_help_items)} itens de ajuda")
            return True
            
        except Exception as e:
            print(f"Erro ao atualizar help_tab.py: {e}")
            import traceback
            traceback.print_exc()
            # Restaurar backup se houve erro
            if self.backup_path.exists():
                import shutil
                shutil.copy2(self.backup_path, self.help_tab_path)
                print("Backup restaurado devido ao erro")
            return False
    
    def _generate_help_items_code(self, help_items):
        """Gera código Python para os itens de ajuda"""
        items_code = []
        
        for title, content in help_items:
            # Escapar aspas triplas no conteúdo
            content_escaped = content.replace('"""', '\\"\\"\\"')
            
            item_code = f'''            ("{title}", """
{content_escaped}
            """)'''
            
            items_code.append(item_code)
        
        return ',\n\n'.join(items_code)


class DocumentWatcher(FileSystemEventHandler):
    """Monitora mudanças nos documentos .docx"""
    
    def __init__(self, docs_path, help_tab_path):
        self.docs_path = Path(docs_path)
        self.help_tab_path = help_tab_path
        self.extractor = DocxContentExtractor(docs_path)
        self.updater = HelpTabUpdater(help_tab_path)
        self.last_sync = {}
        self.sync_callback = None  # Callback para notificar sincronização
        
    def on_modified(self, event):
        if event.is_directory:
            return
            
        file_path = Path(event.src_path)
        
        # Verificar se é arquivo .docx e não é temporário
        if file_path.suffix.lower() == '.docx' and not file_path.name.startswith('~'):
            # Evitar múltiplos eventos para o mesmo arquivo
            current_time = time.time()
            if file_path in self.last_sync:
                if current_time - self.last_sync[file_path] < 2:  # 2 segundos de cooldown
                    return
            
            self.last_sync[file_path] = current_time
            
            print(f"\nDocumento modificado: {file_path.name}")
            success = self.sync_documents()
            
            # Chamar callback se definido
            if self.sync_callback:
                message = f"Documento {file_path.name} {'sincronizado' if success else 'falhou na sincronização'}"
                self.sync_callback(success, message)
    
    def sync_documents(self):
        """Sincroniza documentos com help_tab"""
        print("Iniciando sincronização...")
        
        try:
            # Extrair conteúdo dos documentos
            documents = self.extractor.extract_all_documents()
            
            if documents:
                # Atualizar help_tab
                success = self.updater.update_help_tab(documents)
                if success:
                    print("✅ Sincronização concluída com sucesso!")
                    return True
                else:
                    print("❌ Erro na sincronização")
                    return False
            else:
                print("❌ Nenhum documento encontrado para sincronizar")
                return False
                
        except Exception as e:
            print(f"❌ Erro durante sincronização: {e}")
            return False


def main():
    """Função principal"""
    # Configurar caminhos (ajustado para nova estrutura de pastas)
    base_path = Path(__file__).parent.parent  # Subir um nível da pasta doc_sync
    docs_path = base_path / 'docs'
    help_tab_path = base_path / 'frontend' / 'help_tab.py'
    
    if not docs_path.exists():
        print(f"❌ Pasta de documentos não encontrada: {docs_path}")
        return
    
    if not help_tab_path.exists():
        print(f"❌ Arquivo help_tab.py não encontrado: {help_tab_path}")
        return
    
    # Criar instâncias
    extractor = DocxContentExtractor(docs_path)
    updater = HelpTabUpdater(help_tab_path)
    watcher = DocumentWatcher(docs_path, help_tab_path)
    
    # Sincronização inicial
    print("🔄 Executando sincronização inicial...")
    documents = extractor.extract_all_documents()
    
    if documents:
        success = updater.update_help_tab(documents)
        if success:
            print("✅ Sincronização inicial concluída!")
        else:
            print("❌ Erro na sincronização inicial")
            return
    else:
        print("⚠️ Nenhum documento .docx encontrado para sincronização")
    
    # Modo interativo
    print("\n" + "="*60)
    print("🔍 QEMULA - Sincronização de Documentos")
    print("="*60)
    print("1. Monitoramento automático ativo")
    print("2. Digite 'sync' para sincronização manual")
    print("3. Digite 'quit' para sair")
    print("="*60)
    
    # Configurar monitoramento
    observer = Observer()
    observer.schedule(watcher, str(docs_path), recursive=False)
    observer.start()
    
    try:
        while True:
            command = input("\n> ").strip().lower()
            
            if command == 'quit':
                break
            elif command == 'sync':
                watcher.sync_documents()
            elif command == 'help':
                print("\nComandos disponíveis:")
                print("  sync  - Forçar sincronização manual")
                print("  quit  - Sair do programa")
                print("  help  - Mostrar esta ajuda")
            elif command:
                print("Comando não reconhecido. Digite 'help' para ajuda.")
            
    except KeyboardInterrupt:
        print("\n\n👋 Encerrando monitoramento...")
    finally:
        observer.stop()
        observer.join()
        print("✅ Monitoramento encerrado")


if __name__ == "__main__":
    main()
