"""
QEMULA Auto-Sync Service
Sistema automatizado de sincronização entre documentos .docx e help_tab.py

Features:
- Monitoramento automático de mudanças nos documentos
- Sincronização instantânea ao detectar modificações
- Interface web para controle remoto
- Logs detalhados de todas as operações
- Notificações de status
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from threading import Thread
import threading
from docs_sync import DocxContentExtractor, HelpTabUpdater, DocumentWatcher


class QemulaAutoSyncService:
    """Serviço de sincronização automática para QEMULA"""
    
    def __init__(self, config_file="sync_config.json"):
        self.config_file = Path(config_file)
        self.config = self.load_config()
        self.setup_logging()
        self.running = False
        self.observer = None
        self.last_sync_status = {"success": False, "timestamp": None, "message": ""}
        
    def load_config(self):
        """Carrega configuração do arquivo JSON"""
        default_config = {
            "docs_path": "docs",
            "help_tab_path": "frontend/help_tab.py", 
            "auto_sync": True,
            "sync_interval": 5,  # segundos para debounce
            "log_level": "INFO",
            "notifications": True,
            "backup_enabled": True,
            "max_backups": 5
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    default_config.update(config)
            except Exception as e:
                print(f"Erro ao carregar configuração: {e}")
        
        return default_config
    
    def save_config(self):
        """Salva configuração no arquivo JSON"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Erro ao salvar configuração: {e}")
    
    def setup_logging(self):
        """Configura sistema de logging"""
        log_level = getattr(logging, self.config.get('log_level', 'INFO'))
        
        # Configurar logger
        self.logger = logging.getLogger('QemulaSync')
        self.logger.setLevel(log_level)
        
        # Remover handlers existentes
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Handler para arquivo
        log_file = Path('logs') / f'qemula_sync_{datetime.now().strftime("%Y%m%d")}.log'
        log_file.parent.mkdir(exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(log_level)
        
        # Handler para console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        
        # Formato de log
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def start_service(self):
        """Inicia o serviço de sincronização"""
        try:
            base_path = Path.cwd().parent if Path.cwd().name == 'doc_sync' else Path.cwd()  # Ajustar para nova estrutura
            docs_path = base_path / self.config['docs_path']
            help_tab_path = base_path / self.config['help_tab_path']
            
            if not docs_path.exists():
                raise FileNotFoundError(f"Pasta de documentos não encontrada: {docs_path}")
            
            if not help_tab_path.exists():
                raise FileNotFoundError(f"Arquivo help_tab.py não encontrado: {help_tab_path}")
            
            self.logger.info("🚀 Iniciando QEMULA Auto-Sync Service")
            self.logger.info(f"📁 Monitorando: {docs_path}")
            self.logger.info(f"🎯 Destino: {help_tab_path}")
            
            # Sincronização inicial
            self.perform_sync()
            
            if self.config.get('auto_sync', True):
                # Iniciar monitoramento automático
                self.start_file_monitoring(docs_path, help_tab_path)
                self.running = True
                self.logger.info("👁️ Monitoramento automático ativado")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao iniciar serviço: {e}")
            return False
    
    def start_file_monitoring(self, docs_path, help_tab_path):
        """Inicia monitoramento de arquivos"""
        from watchdog.observers import Observer
        
        self.watcher = DocumentWatcher(docs_path, help_tab_path)
        self.watcher.sync_callback = self.on_sync_completed
        
        self.observer = Observer()
        self.observer.schedule(self.watcher, str(docs_path), recursive=False)
        self.observer.start()
    
    def stop_service(self):
        """Para o serviço"""
        self.running = False
        if self.observer:
            self.observer.stop()
            self.observer.join()
        self.logger.info("🛑 Serviço de sincronização parado")
    
    def perform_sync(self):
        """Executa sincronização manual"""
        try:
            base_path = Path.cwd().parent if Path.cwd().name == 'doc_sync' else Path.cwd()  # Ajustar para nova estrutura
            docs_path = base_path / self.config['docs_path']
            help_tab_path = base_path / self.config['help_tab_path']
            
            extractor = DocxContentExtractor(docs_path)
            updater = HelpTabUpdater(help_tab_path)
            
            self.logger.info("📚 Extraindo conteúdo dos documentos...")
            documents = extractor.extract_all_documents()
            
            if not documents:
                self.last_sync_status = {
                    "success": False,
                    "timestamp": datetime.now().isoformat(),
                    "message": "Nenhum documento .docx encontrado"
                }
                self.logger.warning("⚠️ Nenhum documento .docx encontrado")
                return False
            
            self.logger.info(f"📄 Documentos processados: {', '.join(documents.keys())}")
            
            # Atualizar help_tab
            success = updater.update_help_tab(documents)
            
            self.last_sync_status = {
                "success": success,
                "timestamp": datetime.now().isoformat(),
                "message": f"Sincronização {'bem-sucedida' if success else 'falhada'} - {len(documents)} documentos processados"
            }
            
            if success:
                self.logger.info("✅ Sincronização concluída com sucesso!")
                if self.config.get('notifications', True):
                    self.send_notification("Sincronização concluída", "help_tab.py atualizado com sucesso")
            else:
                self.logger.error("❌ Falha na sincronização")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Erro durante sincronização: {e}")
            self.last_sync_status = {
                "success": False,
                "timestamp": datetime.now().isoformat(),
                "message": f"Erro: {str(e)}"
            }
            return False
    
    def on_sync_completed(self, success, message=""):
        """Callback chamado quando sincronização é completada"""
        self.last_sync_status = {
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "message": message
        }
    
    def send_notification(self, title, message):
        """Envia notificação do sistema (se disponível)"""
        try:
            if sys.platform == "win32":
                # Usar notificação do Windows
                import subprocess
                subprocess.run([
                    'powershell', '-Command',
                    f'Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show("{message}", "{title}")'
                ], capture_output=True)
        except:
            pass  # Ignorar se não conseguir enviar notificação
    
    def get_status(self):
        """Retorna status atual do serviço"""
        return {
            "running": self.running,
            "last_sync": self.last_sync_status,
            "config": self.config,
            "uptime": time.time() if self.running else 0
        }
    
    def update_config(self, new_config):
        """Atualiza configuração"""
        self.config.update(new_config)
        self.save_config()
        self.logger.info("⚙️ Configuração atualizada")


def main():
    """Função principal"""
    print("🔧 QEMULA Auto-Sync Service v1.0")
    print("=" * 50)
    
    service = QemulaAutoSyncService()
    
    try:
        # Iniciar serviço
        if not service.start_service():
            print("❌ Falha ao iniciar o serviço")
            return
        
        print("\n📋 Comandos disponíveis:")
        print("  sync     - Forçar sincronização manual")
        print("  status   - Mostrar status do serviço")
        print("  config   - Mostrar configuração atual")
        print("  logs     - Mostrar logs recentes")
        print("  stop     - Parar monitoramento automático")
        print("  start    - Iniciar monitoramento automático")
        print("  quit     - Sair do serviço")
        print("=" * 50)
        
        # Loop de comandos
        while True:
            try:
                command = input("\n> ").strip().lower()
                
                if command == 'quit':
                    break
                elif command == 'sync':
                    print("🔄 Executando sincronização manual...")
                    service.perform_sync()
                elif command == 'status':
                    status = service.get_status()
                    print(f"\n📊 Status do Serviço:")
                    print(f"  🔄 Executando: {'Sim' if status['running'] else 'Não'}")
                    print(f"  🕒 Última sync: {status['last_sync']['timestamp']}")
                    print(f"  ✅ Sucesso: {'Sim' if status['last_sync']['success'] else 'Não'}")
                    print(f"  💬 Mensagem: {status['last_sync']['message']}")
                elif command == 'config':
                    print(f"\n⚙️ Configuração Atual:")
                    for key, value in service.config.items():
                        print(f"  {key}: {value}")
                elif command == 'logs':
                    print("\n📋 Logs recentes:")
                    log_file = Path('logs') / f'qemula_sync_{datetime.now().strftime("%Y%m%d")}.log'
                    if log_file.exists():
                        with open(log_file, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                            for line in lines[-10:]:  # Últimas 10 linhas
                                print(f"  {line.strip()}")
                    else:
                        print("  Nenhum log encontrado")
                elif command == 'stop':
                    service.config['auto_sync'] = False
                    service.stop_service()
                    print("🛑 Monitoramento automático parado")
                elif command == 'start':
                    service.config['auto_sync'] = True
                    service.start_service()
                    print("▶️ Monitoramento automático iniciado")
                elif command == 'help':
                    print("\n📋 Comandos disponíveis:")
                    print("  sync, status, config, logs, stop, start, quit, help")
                elif command:
                    print("❓ Comando não reconhecido. Digite 'help' para ajuda.")
                    
            except KeyboardInterrupt:
                break
    
    except KeyboardInterrupt:
        print("\n\n👋 Encerrando serviço...")
    finally:
        service.stop_service()
        print("✅ Serviço encerrado")


if __name__ == "__main__":
    main()
