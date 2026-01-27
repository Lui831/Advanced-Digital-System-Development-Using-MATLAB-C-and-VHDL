"""
QEMULA Resources Update System
Sistema de atualização de recursos da aplicação QEMULA

Inclui:
- Sincronização automática de documentação (.docx -> help_tab.py)
- Atualização de imagens e assets
- Verificação de integridade de arquivos
- Geração de relatórios
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime

# Importar módulo de sincronização da nova localização
try:
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent / 'doc_sync'))
    from sync_integration import sync_help_documentation, get_documentation_status
    SYNC_AVAILABLE = True
except ImportError:
    SYNC_AVAILABLE = False
    print("⚠️ Módulo de sincronização não disponível")


class QemulaResourceUpdater:
    """Gerenciador de recursos do QEMULA"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.report = {
            'timestamp': datetime.now().isoformat(),
            'operations': [],
            'errors': [],
            'status': 'started'
        }
    
    def log_operation(self, operation, success=True, details=""):
        """Registra uma operação no relatório"""
        self.report['operations'].append({
            'operation': operation,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
        
        if not success:
            self.report['errors'].append({
                'operation': operation,
                'details': details,
                'timestamp': datetime.now().isoformat()
            })
    
    def update_documentation(self):
        """Atualiza documentação do help_tab com base nos arquivos .docx"""
        print("📚 Atualizando documentação...")
        
        if not SYNC_AVAILABLE:
            self.log_operation("update_documentation", False, "Módulo de sincronização não disponível")
            return False
        
        try:
            # Verificar status antes da sincronização
            status = get_documentation_status()
            if not status:
                self.log_operation("update_documentation", False, "Não foi possível obter status da documentação")
                return False
            
            print(f"  📄 Encontrados {len(status['docx_files'])} documentos .docx")
            
            # Executar sincronização
            success = sync_help_documentation()
            
            if success:
                self.log_operation("update_documentation", True, f"Sincronizados {len(status['docx_files'])} documentos")
                print("  ✅ Documentação atualizada com sucesso")
            else:
                self.log_operation("update_documentation", False, "Falha na sincronização")
                print("  ❌ Falha na atualização da documentação")
            
            return success
            
        except Exception as e:
            error_msg = f"Erro durante atualização da documentação: {e}"
            self.log_operation("update_documentation", False, error_msg)
            print(f"  ❌ {error_msg}")
            return False
    
    def verify_image_resources(self):
        """Verifica se as imagens necessárias estão disponíveis"""
        print("🖼️ Verificando recursos de imagem...")
        
        images_path = self.base_path / 'images'
        if not images_path.exists():
            self.log_operation("verify_images", False, "Pasta images/ não encontrada")
            print("  ❌ Pasta images/ não encontrada")
            return False
        
        # Imagens esperadas baseadas no help_tab.py
        expected_images = [
            'debug.png',
            'docker.png', 
            'email.png',
            'emulation.png',
            'github.png',
            'help.png',
            'podman.png',
            'qemula.png',
            'settings.png'
        ]
        
        missing_images = []
        existing_images = []
        
        for img in expected_images:
            img_path = images_path / img
            if img_path.exists():
                existing_images.append(img)
            else:
                missing_images.append(img)
        
        if missing_images:
            self.log_operation("verify_images", False, f"Imagens ausentes: {', '.join(missing_images)}")
            print(f"  ⚠️ Imagens ausentes: {', '.join(missing_images)}")
        else:
            self.log_operation("verify_images", True, f"Todas as {len(expected_images)} imagens encontradas")
            print(f"  ✅ Todas as {len(expected_images)} imagens encontradas")
        
        print(f"  📊 Status: {len(existing_images)}/{len(expected_images)} imagens disponíveis")
        return len(missing_images) == 0
    
    def check_python_dependencies(self):
        """Verifica se as dependências Python estão instaladas"""
        print("🐍 Verificando dependências Python...")
        
        required_packages = [
            'PySide6',
            'python-docx', 
            'watchdog'
        ]
        
        missing_packages = []
        installed_packages = []
        
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
                installed_packages.append(package)
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            self.log_operation("check_dependencies", False, f"Pacotes ausentes: {', '.join(missing_packages)}")
            print(f"  ❌ Pacotes ausentes: {', '.join(missing_packages)}")
            print(f"  💡 Execute: pip install {' '.join(missing_packages)}")
        else:
            self.log_operation("check_dependencies", True, "Todas as dependências instaladas")
            print(f"  ✅ Todas as dependências estão instaladas")
        
        return len(missing_packages) == 0
    
    def verify_file_structure(self):
        """Verifica se a estrutura de arquivos está correta"""
        print("📁 Verificando estrutura de arquivos...")
        
        expected_structure = {
            'main.py': 'Arquivo principal',
            'frontend/': 'Pasta da interface',
            'frontend/help_tab.py': 'Tab de ajuda',
            'backend/': 'Pasta do backend',
            'docs/': 'Pasta de documentação',
            'images/': 'Pasta de imagens',
            'requirements.txt': 'Dependências Python'
        }
        
        missing_items = []
        existing_items = []
        
        for item, description in expected_structure.items():
            item_path = self.base_path / item
            if item_path.exists():
                existing_items.append(item)
            else:
                missing_items.append(f"{item} ({description})")
        
        if missing_items:
            self.log_operation("verify_structure", False, f"Itens ausentes: {', '.join(missing_items)}")
            print(f"  ⚠️ Itens ausentes: {', '.join(missing_items)}")
        else:
            self.log_operation("verify_structure", True, "Estrutura de arquivos completa")
            print("  ✅ Estrutura de arquivos completa")
        
        print(f"  📊 Status: {len(existing_items)}/{len(expected_structure)} itens encontrados")
        return len(missing_items) == 0
    
    def generate_report(self):
        """Gera relatório final"""
        self.report['status'] = 'completed'
        self.report['summary'] = {
            'total_operations': len(self.report['operations']),
            'successful_operations': len([op for op in self.report['operations'] if op['success']]),
            'failed_operations': len(self.report['errors']),
            'completion_time': datetime.now().isoformat()
        }
        
        # Salvar relatório
        report_file = self.base_path / 'logs' / f'update_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, indent=2, ensure_ascii=False)
        
        return report_file
    
    def run_full_update(self):
        """Executa atualização completa de recursos"""
        print("🔧 QEMULA Resource Updater v1.0")
        print("=" * 50)
        print(f"📅 Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Executar todas as verificações e atualizações
        operations = [
            ('Estrutura de Arquivos', self.verify_file_structure),
            ('Dependências Python', self.check_python_dependencies),
            ('Recursos de Imagem', self.verify_image_resources),
            ('Documentação', self.update_documentation)
        ]
        
        results = {}
        
        for name, operation in operations:
            print(f"🔍 {name}:")
            try:
                results[name] = operation()
            except Exception as e:
                print(f"  ❌ Erro inesperado: {e}")
                results[name] = False
                self.log_operation(name.lower().replace(' ', '_'), False, str(e))
            print()
        
        # Resumo final
        print("=" * 50)
        print("📊 RESUMO FINAL:")
        
        successful = sum(1 for success in results.values() if success)
        total = len(results)
        
        for name, success in results.items():
            status = "✅" if success else "❌"
            print(f"  {status} {name}")
        
        print()
        print(f"🎯 Taxa de Sucesso: {successful}/{total} ({successful/total*100:.1f}%)")
        
        # Gerar relatório
        report_file = self.generate_report()
        print(f"📄 Relatório salvo em: {report_file}")
        
        if successful == total:
            print("🎉 Todos os recursos foram atualizados com sucesso!")
            return True
        else:
            print("⚠️ Algumas operações falharam. Verifique o relatório para detalhes.")
            return False


def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='QEMULA Resource Updater')
    parser.add_argument('--docs-only', action='store_true', help='Atualizar apenas documentação')
    parser.add_argument('--verify-only', action='store_true', help='Apenas verificar, sem atualizar')
    parser.add_argument('--quiet', action='store_true', help='Modo silencioso')
    
    args = parser.parse_args()
    
    updater = QemulaResourceUpdater()
    
    if args.docs_only:
        # Atualizar apenas documentação
        success = updater.update_documentation()
        sys.exit(0 if success else 1)
    elif args.verify_only:
        # Apenas verificações
        print("🔍 Modo verificação - nenhuma atualização será feita")
        print()
        updater.verify_file_structure()
        updater.check_python_dependencies()
        updater.verify_image_resources()
        report_file = updater.generate_report()
        print(f"\n📄 Relatório salvo em: {report_file}")
    else:
        # Atualização completa
        success = updater.run_full_update()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
