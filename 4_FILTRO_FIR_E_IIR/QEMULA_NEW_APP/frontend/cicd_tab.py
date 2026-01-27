from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QTextEdit, 
                             QFrame, QLineEdit, QSplitter, QListWidget, QTabWidget,
                             QListWidgetItem, QCheckBox, QScrollArea, QSlider,
                             QComboBox, QSpinBox, QGroupBox, QGridLayout, QTreeWidget,
                             QTreeWidgetItem, QProgressBar, QSplitterHandle, QFileDialog,
                             QMessageBox)
from PySide6.QtCore import Qt, QSize, Signal, QPropertyAnimation, QRect, QTimer, QThread, QUrl, QProcess
from PySide6.QtGui import QFont, QPalette, QColor, QIcon, QPainter, QPen, QBrush, QPixmap, QDesktopServices
import sys
import os
import subprocess

# Tentar importar yaml, mas não falhar se não estiver disponível
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    print("PyYAML not available - YAML functionality will be limited")

class CICDStepItem(QWidget):
    """Widget para um item de step do CI/CD"""
    stepToggled = Signal(str, bool)
    
    def __init__(self, step_name, step_description, step_commands=None, parent=None):
        super().__init__(parent)
        self.step_name = step_name
        self.step_description = step_description
        self.step_commands = step_commands or []
        self.is_enabled = False
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Checkbox para habilitar/desabilitar o step
        self.checkbox = QCheckBox()
        self.checkbox.toggled.connect(self.on_toggle)
        layout.addWidget(self.checkbox)
        
        # Informações do step
        info_layout = QVBoxLayout()
        
        # Nome do step
        name_label = QLabel(self.step_name)
        name_label.setFont(QFont("Arial", 12, QFont.Bold))
        info_layout.addWidget(name_label)
        
        # Descrição do step
        desc_label = QLabel(self.step_description)
        desc_label.setFont(QFont("Arial", 10))
        desc_label.setStyleSheet("color: #666666;")
        desc_label.setWordWrap(True)
        info_layout.addWidget(desc_label)
        
        layout.addLayout(info_layout)
        layout.addStretch()
        
        # Status indicator
        self.status_label = QLabel("●")
        self.status_label.setFont(QFont("Arial", 16))
        self.update_status()
        layout.addWidget(self.status_label)
        
        self.setStyleSheet("""
            CICDStepItem {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                margin: 2px;
            }
            CICDStepItem:hover {
                background-color: #f8f9fa;
                border-color: #007bff;
            }
        """)
    
    def on_toggle(self, checked):
        self.is_enabled = checked
        self.update_status()
        self.stepToggled.emit(self.step_name, checked)
    
    def update_status(self):
        if self.is_enabled:
            self.status_label.setStyleSheet("color: #4caf50;")
        else:
            self.status_label.setStyleSheet("color: #ccc;")
    
    def set_enabled(self, enabled):
        self.checkbox.setChecked(enabled)

class YAMLPreviewWidget(QTextEdit):
    """Widget para preview do arquivo YAML gerado"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setFont(QFont("Consolas", 10))
        self.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 10px;
                font-family: 'Consolas', 'Courier New', monospace;
            }
        """)
        self.setPlaceholderText("Generated YAML will appear here...")

class ActWorkerThread(QThread):
    """Thread worker para executar act em background"""
    output_received = Signal(str)
    error_received = Signal(str)
    finished_execution = Signal(int)
    
    def __init__(self, act_command, working_dir, parent=None):
        super().__init__(parent)
        self.act_command = act_command
        self.working_dir = working_dir
        self.process = None
        
    def run(self):
        """Executar o comando act"""
        try:
            # Configurar encoding para Windows
            import locale
            encoding = 'utf-8'
            
            # Tentar determinar o encoding do sistema
            try:
                encoding = locale.getpreferredencoding() or 'utf-8'
            except:
                encoding = 'utf-8'
            
            self.process = subprocess.Popen(
                self.act_command,
                cwd=self.working_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                shell=True,
                bufsize=1,
                encoding=encoding,
                errors='replace'  # Substituir caracteres problemáticos
            )
            
            # Ler output linha por linha em tempo real
            for line in iter(self.process.stdout.readline, ''):
                if line:
                    # Limpar caracteres de controle e não-ASCII problemáticos
                    clean_line = ''.join(char if ord(char) < 128 else '?' for char in line.strip())
                    if clean_line:  # Só emitir se a linha não estiver vazia após limpeza
                        self.output_received.emit(clean_line)
                    
            self.process.wait()
            self.finished_execution.emit(self.process.returncode)
            
        except Exception as e:
            self.error_received.emit(f"Error executing act: {str(e)}")
            self.finished_execution.emit(-1)
    
    def stop_execution(self):
        """Parar a execução do processo"""
        if self.process and self.process.poll() is None:
            self.process.terminate()
            self.process.wait(timeout=5)
            if self.process.poll() is None:
                self.process.kill()

class QemulaCICDApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QEMULA CI/CD Configuration")
        self.setGeometry(100, 100, 1400, 800)
        
        # Configurações CI/CD disponíveis baseadas no CI_workflow.yaml
        self.available_steps = {
            "spellcheck": {
                "description": "Spell check on code and documentation files",
                "commands": [
                    "actions/checkout@v4",
                    "docker/login-action@v1",
                    "codespell-project/actions-codespell@master"
                ]
            },
            "test_calculate_crc_1": {
                "description": "Run test for CRC calculation function (first variant)",
                "commands": [
                    "source venv/bin/activate",
                    "pytest -v -n auto -k \"test_calculate_crc_1\" Docker_Raw_Codes/src-interface/test/"
                ]
            },
            "test_validate_packet": {
                "description": "Test packet validation functionality",
                "commands": [
                    "source venv/bin/activate",
                    "pytest -v -n auto -k \"test_validate_packet\" Docker_Raw_Codes/src-interface/test/"
                ]
            },
            "test_process_packet": {
                "description": "Test packet processing functionality",
                "commands": [
                    "source venv/bin/activate",
                    "pytest -v -n auto -k \"test_process_packet\" Docker_Raw_Codes/src-interface/test/"
                ]
            },
            "test_calculate_crc_2": {
                "description": "Run test for CRC calculation function (second variant)",
                "commands": [
                    "source venv/bin/activate",
                    "pytest -v -n auto -k \"test_calculate_crc_2\" Docker_Raw_Codes/src-interface/test/"
                ]
            },
            "test_identify_command": {
                "description": "Test command identification functionality",
                "commands": [
                    "source venv/bin/activate",
                    "pytest -v -n auto -k \"test_identify_command\" Docker_Raw_Codes/src-interface/test/"
                ]
            },
            "test_construct_packet": {
                "description": "Test packet construction functionality",
                "commands": [
                    "source venv/bin/activate",
                    "pytest -v -n auto -k \"test_construct_packet\" Docker_Raw_Codes/src-interface/test/"
                ]
            },
            "test_failed_recieve": {
                "description": "Test failed receive scenarios and error handling",
                "commands": [
                    "source venv/bin/activate",
                    "pytest -v -n auto -k \"test_failed_recieve\" Docker_Raw_Codes/src-interface/test/"
                ]
            },
            "build_and_test": {
                "description": "Build Docker containers and run protocol testing",
                "commands": [
                    "docker-compose build",
                    "docker-compose up -d",
                    "python3 Testing_Codes/Protocol_Testing_Code/main.py"
                ]
            },
            "test_the_instrument": {
                "description": "Comprehensive instrument testing with Docker containers",
                "commands": [
                    "docker-compose build",
                    "docker-compose up -d",
                    "python3 Testing_Codes/Protocol_Testing_Code/main3.py",
                    "python3 Testing_Codes/Protocol_Testing_Code/client_instrument.py",
                    "python3 Testing_Codes/Protocol_Testing_Code/main4.py"
                ]
            },
            "clear-cache": {
                "description": "Clear GitHub Actions cache to optimize storage",
                "commands": [
                    "actions/github-script@v6"
                ]
            },
            "deploy": {
                "description": "Deploy to NAS via FTP (continuous deployment)",
                "commands": [
                    "lftp -u \"$FTP_USER\",\"$FTP_PASS\" ftp://syn_ds224p_nsee.local"
                ]
            }
        }
        
        self.selected_steps = {}
        self.setup_ui()
        self.apply_styles()
        
        # Inicializar variáveis para execução com act
        self.act_worker = None
        self.is_running = False
        
        # Adicionar mensagem inicial aos logs
        self.log_message("🚀 QEMULA CI/CD Pipeline Configuration initialized")
        self.log_message("📋 Select steps from the left panel or choose a preset to begin")
        self.log_message("⚡ Act mode enabled - workflows will run locally with act")
        self.check_act_availability()
        
    def setup_ui(self):
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal horizontal
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar esquerda
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar)
        
        # Área principal
        main_area = self.create_main_area()
        main_layout.addWidget(main_area)
    
    def create_sidebar(self):
        sidebar = QFrame()
        sidebar.setFixedWidth(220)
        sidebar.setFrameStyle(QFrame.Box)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(10, 20, 10, 10)
        layout.setSpacing(5)
        
        # Título QEMULA APP
        title = QLabel("QEMULA APP")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        layout.addSpacing(20)
        
        # Menu items
        menu_items = [
            ("Docker", False),
            ("Control", False),
            ("Transciever SPW", False),
            ("Transciever UART", False),
            ("CI/CD", True),  # Item ativo
            ("Settings", False),
            ("Help", False)
        ]
        
        for item_text, is_active in menu_items:
            item = QPushButton(item_text)
            item.setFixedHeight(40)
            item.setFont(QFont("Arial", 10))
            if is_active:
                item.setStyleSheet("""
                    QPushButton {
                        background-color: #666666;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        text-align: left;
                        padding-left: 15px;
                    }
                """)
            else:
                item.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        color: #666666;
                        border: none;
                        border-radius: 4px;
                        text-align: left;
                        padding-left: 15px;
                    }
                    QPushButton:hover {
                        background-color: #f0f0f0;
                    }
                """)
            layout.addWidget(item)
        
        layout.addStretch()
        return sidebar
    
    def create_main_area(self):
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Header
        header = self.create_header()
        layout.addWidget(header)

        # Conteúdo principal dividido em duas colunas
        content_splitter = QSplitter(Qt.Horizontal)
        
        # Coluna esquerda - Seleção de steps
        left_panel = self.create_steps_panel()
        content_splitter.addWidget(left_panel)
        
        # Coluna direita - Preview e controles
        right_panel = self.create_preview_panel()
        content_splitter.addWidget(right_panel)
        
        # Configurar proporções do splitter
        content_splitter.setSizes([600, 800])
        
        layout.addWidget(content_splitter)

        return main_widget
    
    def create_header(self):
        from PySide6.QtGui import QPixmap, QDesktopServices
        from PySide6.QtCore import QUrl
        header = QFrame()
        header.setFixedHeight(60)  # Definir altura fixa menor
        layout = QHBoxLayout(header)
        layout.setContentsMargins(10, 5, 10, 5)  # Margens menores
        
        # Título da interface
        title = QLabel("CI/CD Pipeline Configuration")
        title.setFont(QFont("Arial", 14, QFont.Bold))  # Fonte menor
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Status QEMULA run
        status_label = QLabel("QEMULA run")
        status_label.setFont(QFont("Arial", 10))  # Fonte menor
        layout.addWidget(status_label)
        
        # Pause icon
        pause_icon = QLabel("⏸️")
        pause_icon.setFont(QFont("Arial", 14))  # Fonte menor
        layout.addWidget(pause_icon)
        
        layout.addStretch()
        
        # Social icons
        icons_layout = QHBoxLayout()
        icon_files = [
            "images/docker.png",
            "images/email.png", 
            "images/github.png",
            "images/podman.png"
        ]
        doc_urls = [
            "https://docs.docker.com/",
            "https://nsee.maua.br",
            "https://github.com/FFCfelps1/QEMULA_Oficial_Rep",
            "https://podman.io/docs"
        ]
        
        for icon_path, url in zip(icon_files, doc_urls):
            btn = QPushButton()
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("background: transparent; border: none;")
            try:
                pixmap = QPixmap(icon_path)
                pixmap = pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)  # Ícones menores
                btn.setIcon(QIcon(pixmap))
                btn.setIconSize(QSize(32, 32))  # Tamanho menor
            except:
                btn.setText("🔗")
                btn.setFont(QFont("Arial", 16))  # Fonte menor
            btn.setFixedSize(36, 36)  # Botão menor
            btn.clicked.connect(lambda checked, link=url: QDesktopServices.openUrl(QUrl(link)))
            icons_layout.addWidget(btn)
        layout.addLayout(icons_layout)
        return header
    
    def create_steps_panel(self):
        """Criar painel de seleção de steps"""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
            }
        """)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Título do painel
        title_label = QLabel("Available CI/CD Steps")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setStyleSheet("border: none; color: #333333; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Controles superiores
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)
        
        select_all_btn = QPushButton("Select All")
        select_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        select_all_btn.clicked.connect(self.select_all_steps)
        controls_layout.addWidget(select_all_btn)
        
        clear_all_btn = QPushButton("Clear All")
        clear_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #545b62;
            }
        """)
        clear_all_btn.clicked.connect(self.clear_all_steps)
        controls_layout.addWidget(clear_all_btn)
        
        controls_layout.addStretch()
        
        # Preset configurations
        preset_label = QLabel("Presets:")
        preset_label.setFont(QFont("Arial", 10))
        preset_label.setStyleSheet("border: none; color: #666666;")
        controls_layout.addWidget(preset_label)
        
        preset_combo = QComboBox()
        preset_combo.addItems([
            "Custom",
            "Quick Tests",
            "Full QEMULA Pipeline",
            "Code Quality Only",
            "Protocol Tests Only",
            "Docker Tests Only"
        ])
        preset_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 5px;
                background-color: white;
                min-width: 120px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
            }
        """)
        preset_combo.currentTextChanged.connect(self.apply_preset)
        controls_layout.addWidget(preset_combo)
        
        layout.addLayout(controls_layout)
        
        # Scroll area para os steps
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Criar items para cada step disponível
        self.step_widgets = {}
        for step_name, step_info in self.available_steps.items():
            step_widget = CICDStepItem(
                step_name, 
                step_info["description"], 
                step_info["commands"]
            )
            step_widget.stepToggled.connect(self.on_step_toggled)
            self.step_widgets[step_name] = step_widget
            scroll_layout.addWidget(step_widget)
        
        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #cccccc;
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #999999;
            }
        """)
        
        layout.addWidget(scroll_area)
        return panel
    
    def create_preview_panel(self):
        """Criar painel de preview e controles"""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
            }
        """)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Título do painel
        title_label = QLabel("Pipeline Configuration")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setStyleSheet("border: none; color: #333333; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Tabs para diferentes views
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: white;
            }
            QTabWidget::tab-bar {
                alignment: center;
            }
            QTabBar::tab {
                background-color: #f0f0f0;
                padding: 8px 16px;
                margin: 2px;
                border-radius: 4px;
                border: 1px solid #cccccc;
            }
            QTabBar::tab:selected {
                background-color: #007bff;
                color: white;
                border-color: #007bff;
            }
            QTabBar::tab:hover {
                background-color: #e0e0e0;
            }
        """)
        
        # Tab 1: YAML Preview
        yaml_tab = QWidget()
        yaml_layout = QVBoxLayout(yaml_tab)
        
        # Header do YAML preview
        yaml_header = QHBoxLayout()
        yaml_label = QLabel("Generated YAML Configuration:")
        yaml_label.setFont(QFont("Arial", 12, QFont.Bold))
        yaml_header.addWidget(yaml_label)
        
        yaml_header.addStretch()
        
        # Botões de ação
        save_btn = QPushButton("💾 Save YAML")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        save_btn.clicked.connect(self.save_yaml)
        yaml_header.addWidget(save_btn)
        
        export_btn = QPushButton("📤 Export to GitHub")
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)
        export_btn.clicked.connect(self.export_to_github)
        yaml_header.addWidget(export_btn)
        
        yaml_layout.addLayout(yaml_header)
        
        # YAML preview widget
        self.yaml_preview = YAMLPreviewWidget()
        yaml_layout.addWidget(self.yaml_preview)
        
        tab_widget.addTab(yaml_tab, "YAML Preview")
        
        # Tab 2: Pipeline Visualization
        viz_tab = QWidget()
        viz_layout = QVBoxLayout(viz_tab)
        
        viz_label = QLabel("Pipeline Flow Visualization:")
        viz_label.setFont(QFont("Arial", 12, QFont.Bold))
        viz_layout.addWidget(viz_label)
        
        # Pipeline flow widget
        self.pipeline_flow = self.create_pipeline_flow()
        viz_layout.addWidget(self.pipeline_flow)
        
        tab_widget.addTab(viz_tab, "Pipeline Flow")
        
        # Tab 3: Execution Settings
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)
        
        settings_label = QLabel("Execution Settings:")
        settings_label.setFont(QFont("Arial", 12, QFont.Bold))
        settings_layout.addWidget(settings_label)
        
        # Settings controls
        settings_form = self.create_settings_form()
        settings_layout.addWidget(settings_form)
        
        tab_widget.addTab(settings_tab, "Settings")
        
        layout.addWidget(tab_widget)
        
        # Logs area
        logs_group = QFrame()
        logs_group.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
            }
        """)
        logs_layout = QVBoxLayout(logs_group)
        logs_layout.setContentsMargins(15, 15, 15, 15)
        
        logs_title = QLabel("Execution Logs")
        logs_title.setFont(QFont("Arial", 12, QFont.Bold))
        logs_title.setStyleSheet("border: none; color: #333333; margin-bottom: 5px;")
        logs_layout.addWidget(logs_title)
        
        logs_controls = QHBoxLayout()
        logs_controls.setSpacing(10)
        
        self.run_pipeline_btn = QPushButton("🚀 Run Pipeline with Act")
        self.run_pipeline_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        self.run_pipeline_btn.clicked.connect(self.run_pipeline)
        logs_controls.addWidget(self.run_pipeline_btn)
        
        self.stop_pipeline_btn = QPushButton("⏹️ Stop")
        self.stop_pipeline_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        self.stop_pipeline_btn.clicked.connect(self.stop_pipeline)
        self.stop_pipeline_btn.setEnabled(False)
        logs_controls.addWidget(self.stop_pipeline_btn)
        
        self.stop_pipeline_btn.setEnabled(False)
        logs_controls.addWidget(self.stop_pipeline_btn)
        
        clear_logs_btn = QPushButton("🗑️ Clear Logs")
        clear_logs_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #545b62;
            }
        """)
        clear_logs_btn.clicked.connect(self.clear_logs)
        logs_controls.addWidget(clear_logs_btn)
        
        logs_controls.addStretch()
        
        logs_layout.addLayout(logs_controls)
        
        # Logs text area
        self.logs_area = QTextEdit()
        self.logs_area.setReadOnly(True)
        self.logs_area.setFont(QFont("Consolas", 9))
        self.logs_area.setMaximumHeight(150)
        self.logs_area.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #00ff00;
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Consolas', 'Courier New', monospace;
            }
        """)
        self.logs_area.setPlaceholderText("Pipeline execution logs will appear here...")
        logs_layout.addWidget(self.logs_area)
        
        layout.addWidget(logs_group)
        
        return panel
    
    def create_pipeline_flow(self):
        """Criar visualização do fluxo do pipeline"""
        flow_widget = QScrollArea()
        flow_content = QWidget()
        flow_layout = QVBoxLayout(flow_content)
        
        # Esta será atualizada quando steps forem selecionados
        self.flow_layout = flow_layout
        self.update_pipeline_flow()
        
        flow_widget.setWidget(flow_content)
        flow_widget.setWidgetResizable(True)
        flow_widget.setStyleSheet("""
            QScrollArea {
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: #f8f9fa;
            }
        """)
        
        return flow_widget
    
    def create_settings_form(self):
        """Criar formulário de configurações"""
        form_widget = QScrollArea()
        form_content = QWidget()
        form_layout = QGridLayout(form_content)
        
        row = 0
        
        # Python version
        form_layout.addWidget(QLabel("Python Version:"), row, 0)
        python_combo = QComboBox()
        python_combo.addItems(["3.8", "3.9", "3.10", "3.11", "3.12"])
        python_combo.setCurrentText("3.9")
        form_layout.addWidget(python_combo, row, 1)
        row += 1
        
        # Operating systems
        form_layout.addWidget(QLabel("Target OS:"), row, 0)
        os_combo = QComboBox()
        os_combo.addItems(["ubuntu-latest", "windows-latest", "macos-latest", "ubuntu-20.04"])
        form_layout.addWidget(os_combo, row, 1)
        row += 1
        
        # Docker registry
        form_layout.addWidget(QLabel("Docker Registry:"), row, 0)
        registry_input = QLineEdit("docker.io")
        form_layout.addWidget(registry_input, row, 1)
        row += 1
        
        # Timeout
        form_layout.addWidget(QLabel("Job Timeout (minutes):"), row, 0)
        timeout_spin = QSpinBox()
        timeout_spin.setRange(1, 480)
        timeout_spin.setValue(60)
        form_layout.addWidget(timeout_spin, row, 1)
        row += 1
        
        # Parallel jobs
        form_layout.addWidget(QLabel("Max Parallel Jobs:"), row, 0)
        parallel_spin = QSpinBox()
        parallel_spin.setRange(1, 10)
        parallel_spin.setValue(3)
        form_layout.addWidget(parallel_spin, row, 1)
        row += 1
        
        # Cache enabled
        cache_check = QCheckBox("Enable Dependency Caching")
        cache_check.setChecked(True)
        form_layout.addWidget(cache_check, row, 0, 1, 2)
        row += 1
        
        # Notifications
        notify_check = QCheckBox("Send Email Notifications")
        form_layout.addWidget(notify_check, row, 0, 1, 2)
        row += 1
        
        form_layout.setRowStretch(row, 1)
        
        form_widget.setWidget(form_content)
        form_widget.setWidgetResizable(True)
        form_widget.setMaximumHeight(300)
        
        return form_widget
    
    def on_step_toggled(self, step_name, enabled):
        """Callback quando um step é habilitado/desabilitado"""
        if enabled:
            self.selected_steps[step_name] = self.available_steps[step_name]
        else:
            self.selected_steps.pop(step_name, None)
        
        self.update_yaml_preview()
        self.update_pipeline_flow()
        self.log_message(f"Step '{step_name}' {'enabled' if enabled else 'disabled'}")
    
    def select_all_steps(self):
        """Selecionar todos os steps"""
        for widget in self.step_widgets.values():
            widget.set_enabled(True)
    
    def clear_all_steps(self):
        """Limpar todos os steps"""
        for widget in self.step_widgets.values():
            widget.set_enabled(False)
    
    def apply_preset(self, preset_name):
        """Aplicar configuração preset"""
        presets = {
            "Quick Tests": ["spellcheck", "test_calculate_crc_1", "test_validate_packet"],
            "Full QEMULA Pipeline": list(self.available_steps.keys()),
            "Code Quality Only": ["spellcheck"],
            "Protocol Tests Only": ["spellcheck", "test_calculate_crc_1", "test_validate_packet", 
                                   "test_process_packet", "test_calculate_crc_2", "test_identify_command", 
                                   "test_construct_packet", "test_failed_recieve"],
            "Docker Tests Only": ["spellcheck", "build_and_test", "test_the_instrument"]
        }
        
        if preset_name in presets:
            # Primeiro limpar todos os steps
            self.clear_all_steps()
            
            # Depois aplicar os steps do preset
            steps_to_enable = presets[preset_name]
            for step_name in steps_to_enable:
                if step_name in self.step_widgets:
                    self.step_widgets[step_name].set_enabled(True)
            
            # Log da ação
            self.log_message(f"Applied preset: {preset_name} ({len(steps_to_enable)} steps)")
            
            # Forçar atualização das visualizações
            self.update_yaml_preview()
            self.update_pipeline_flow()
    
    def update_yaml_preview(self):
        """Atualizar preview do YAML"""
        yaml_config = {
            "name": "QEMULA CI Workflow",
            "on": {
                "pull_request": True,
                "push": True,
                "schedule": [
                    {"cron": "0 3 * * 2"}  # run every Tuesday at 3 AM UTC
                ]
            },
            "jobs": {}
        }
        
        if self.selected_steps:
            # Adicionar jobs baseados nos steps selecionados
            for step_name in self.selected_steps:
                step_info = self.selected_steps[step_name]
                
                # Configuração específica para cada job
                if step_name == "spellcheck":
                    yaml_config["jobs"][step_name] = {
                        "runs-on": "self-hosted",
                        "steps": [
                            {"name": "Checkout", "uses": "actions/checkout@v4"},
                            {
                                "name": "Login to DockerHub",
                                "uses": "docker/login-action@v1",
                                "with": {
                                    "username": "${{ secrets.DOCKER_USERNAME }}",
                                    "password": "${{ secrets.DOCKER_PASSWORD }}"
                                }
                            },
                            {
                                "name": "Spell check",
                                "uses": "codespell-project/actions-codespell@master",
                                "with": {
                                    "check_filenames": True,
                                    "check_hidden": True,
                                    "ignore_words_file": "codespell-ignore-words-list.txt",
                                    "skip": "Control_Interface_Related_Codes, Delivery_Docker"
                                }
                            }
                        ]
                    }
                elif step_name.startswith("test_"):
                    needs = ["spellcheck"]
                    if step_name == "test_process_packet":
                        needs = ["test_calculate_crc_1", "test_validate_packet"]
                    elif step_name == "test_construct_packet":
                        needs = ["test_calculate_crc_2", "test_identify_command"]
                    elif step_name == "test_failed_recieve":
                        needs = ["test_construct_packet"]
                    
                    yaml_config["jobs"][step_name] = {
                        "runs-on": "self-hosted",
                        "needs": needs,
                        "steps": [
                            {"name": "Checkout repository", "uses": "actions/checkout@v2"},
                            {
                                "name": "Configurar Python do sistema",
                                "run": 'echo "PYTHON_LOCATION=/usr/bin/python3.11" >> $GITHUB_ENV\necho "PATH=$PYTHON_LOCATION/bin:$PATH" >> $GITHUB_ENV'
                            },
                            {"name": "Criar ambiente virtual", "run": "python3 -m venv venv"},
                            {
                                "name": "Ativar ambiente virtual e instalar dependências",
                                "run": "source venv/bin/activate\npip install --upgrade pip\npip install -r requirements.txt\npip install pytest-xdist"
                            },
                            {
                                "name": f"Run {step_name}",
                                "env": {"PYTHONPATH": "${{ github.workspace }}/Docker_Raw_Codes/src-interface/test"},
                                "run": f"source venv/bin/activate\npytest -v -n auto -k \"{step_name}\" Docker_Raw_Codes/src-interface/test/"
                            }
                        ]
                    }
                elif step_name == "build_and_test":
                    yaml_config["jobs"][step_name] = {
                        "runs-on": "self-hosted",
                        "needs": ["spellcheck"],
                        "steps": [
                            {"name": "Checkout repository", "uses": "actions/checkout@v2"},
                            {"name": "Set up Docker Buildx", "uses": "docker/setup-buildx-action@v3"},
                            {
                                "name": "Login to DockerHub",
                                "uses": "docker/login-action@v1",
                                "with": {
                                    "username": "${{ secrets.DOCKER_USERNAME }}",
                                    "password": "${{ secrets.DOCKER_PASSWORD }}"
                                }
                            },
                            {
                                "name": "Build Docker Compose services",
                                "run": "cd Docker_Raw_Codes\ndocker-compose build"
                            },
                            {
                                "name": "Run Docker Compose services",
                                "run": "cd Docker_Raw_Codes\ndocker-compose up -d"
                            },
                            {
                                "name": "Run protocol testing",
                                "run": "source venv/bin/activate\npython3 Testing_Codes/Protocol_Testing_Code/main.py"
                            }
                        ]
                    }
                elif step_name == "test_the_instrument":
                    yaml_config["jobs"][step_name] = {
                        "runs-on": "self-hosted",
                        "needs": ["build_and_test"],
                        "steps": [
                            {"name": "Checkout repository", "uses": "actions/checkout@v2"},
                            {"name": "Set up Docker Buildx", "uses": "docker/setup-buildx-action@v3"},
                            {
                                "name": "Build and run Docker services",
                                "run": "cd Docker_Raw_Codes\ndocker-compose build\ndocker-compose up -d"
                            },
                            {
                                "name": "Run comprehensive instrument tests",
                                "run": "source venv/bin/activate\npython3 Testing_Codes/Protocol_Testing_Code/main3.py\npython3 Testing_Codes/Protocol_Testing_Code/client_instrument.py\npython3 Testing_Codes/Protocol_Testing_Code/main4.py"
                            }
                        ]
                    }
                elif step_name == "clear-cache":
                    yaml_config["jobs"][step_name] = {
                        "runs-on": "self-hosted",
                        "needs": ["test_the_instrument", "test_failed_recieve", "test_process_packet"],
                        "permissions": {
                            "actions": "write",
                            "contents": "read"
                        },
                        "steps": [
                            {"name": "Checkout repository", "uses": "actions/checkout@v2"},
                            {
                                "name": "Clear GitHub Actions cache",
                                "uses": "actions/github-script@v6",
                                "with": {
                                    "script": "console.log('Starting cache cleanup...');\n// Cache cleanup script here"
                                }
                            }
                        ]
                    }
                elif step_name == "deploy":
                    yaml_config["jobs"][step_name] = {
                        "runs-on": "self-hosted",
                        "needs": ["clear-cache"],
                        "steps": [
                            {
                                "name": "Deploy to NAS via FTP with lftp",
                                "run": 'lftp -u "$FTP_USER","$FTP_PASS" ftp://syn_ds224p_nsee.local -e "set ssl:verify-certificate no; mirror -R ./ \'/Documentos do NSEE/Github/QEMULA-Rep\'; quit"',
                                "env": {
                                    "FTP_USER": "${{ secrets.FTP_USER }}",
                                    "FTP_PASS": "${{ secrets.FTP_PASS }}"
                                }
                            }
                        ]
                    }
        
        # Verificar se YAML está disponível, caso contrário usar formato simples
        if YAML_AVAILABLE:
            yaml_text = yaml.dump(yaml_config, default_flow_style=False, sort_keys=False)
        else:
            # Gerar YAML manualmente se PyYAML não estiver disponível
            yaml_text = self.generate_yaml_manually(yaml_config)
        
        self.yaml_preview.setPlainText(yaml_text)
    
    def generate_yaml_manually(self, config):
        """Gerar YAML manualmente quando PyYAML não está disponível"""
        yaml_lines = []
        yaml_lines.append(f"name: {config['name']}")
        yaml_lines.append("")
        yaml_lines.append("on:")
        yaml_lines.append("  pull_request:")
        yaml_lines.append("  push:")
        yaml_lines.append("  schedule:")
        yaml_lines.append("    - cron: \"0 3 * * 2\"")
        yaml_lines.append("")
        yaml_lines.append("jobs:")
        
        for job_name, job_config in config['jobs'].items():
            yaml_lines.append(f"  {job_name}:")
            yaml_lines.append(f"    runs-on: {job_config.get('runs-on', 'self-hosted')}")
            
            if 'needs' in job_config:
                if isinstance(job_config['needs'], list):
                    if len(job_config['needs']) == 1:
                        yaml_lines.append(f"    needs: {job_config['needs'][0]}")
                    else:
                        yaml_lines.append("    needs: [" + ", ".join(job_config['needs']) + "]")
                else:
                    yaml_lines.append(f"    needs: {job_config['needs']}")
            
            if 'permissions' in job_config:
                yaml_lines.append("    permissions:")
                for perm, value in job_config['permissions'].items():
                    yaml_lines.append(f"      {perm}: {value}")
            
            yaml_lines.append("    steps:")
            
            for step in job_config.get('steps', []):
                yaml_lines.append(f"      - name: {step['name']}")
                if 'uses' in step:
                    yaml_lines.append(f"        uses: {step['uses']}")
                if 'with' in step:
                    yaml_lines.append("        with:")
                    for key, value in step['with'].items():
                        if isinstance(value, bool):
                            yaml_lines.append(f"          {key}: {str(value).lower()}")
                        else:
                            yaml_lines.append(f"          {key}: {value}")
                if 'run' in step:
                    if '\n' in step['run']:
                        yaml_lines.append("        run: |")
                        for line in step['run'].split('\n'):
                            yaml_lines.append(f"          {line}")
                    else:
                        yaml_lines.append(f"        run: {step['run']}")
                if 'env' in step:
                    yaml_lines.append("        env:")
                    for key, value in step['env'].items():
                        yaml_lines.append(f"          {key}: {value}")
                yaml_lines.append("")
            yaml_lines.append("")
        
        return "\n".join(yaml_lines)
    
    def update_pipeline_flow(self):
        """Atualizar visualização do fluxo do pipeline"""
        # Limpar layout anterior
        for i in reversed(range(self.flow_layout.count())):
            child = self.flow_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        if not self.selected_steps:
            no_steps_label = QLabel("No steps selected. Choose steps from the left panel.")
            no_steps_label.setAlignment(Qt.AlignCenter)
            no_steps_label.setStyleSheet("color: #666; font-style: italic; padding: 20px;")
            self.flow_layout.addWidget(no_steps_label)
            return
        
        # Adicionar steps selecionados
        for i, step_name in enumerate(self.selected_steps.keys()):
            step_frame = QFrame()
            step_frame.setStyleSheet("""
                QFrame {
                    background-color: #e3f2fd;
                    border: 2px solid #2196f3;
                    border-radius: 4px;
                    padding: 10px;
                    margin: 5px;
                }
            """)
            
            step_layout = QVBoxLayout(step_frame)
            
            # Número do step
            step_number = QLabel(f"Step {i+1}")
            step_number.setFont(QFont("Arial", 10, QFont.Bold))
            step_number.setStyleSheet("color: #1976d2;")
            step_layout.addWidget(step_number)
            
            # Nome do step
            step_label = QLabel(step_name)
            step_label.setFont(QFont("Arial", 12, QFont.Bold))
            step_layout.addWidget(step_label)
            
            # Comandos
            commands = self.available_steps[step_name]["commands"]
            if commands:
                commands_text = "\n".join(f"• {cmd}" for cmd in commands[:3])
                if len(commands) > 3:
                    commands_text += f"\n... and {len(commands) - 3} more"
                
                commands_label = QLabel(commands_text)
                commands_label.setFont(QFont("Arial", 9))
                commands_label.setStyleSheet("color: #666;")
                step_layout.addWidget(commands_label)
            
            self.flow_layout.addWidget(step_frame)
            
            # Adicionar seta entre steps (exceto no último)
            if i < len(self.selected_steps) - 1:
                arrow_label = QLabel("⬇")
                arrow_label.setAlignment(Qt.AlignCenter)
                arrow_label.setFont(QFont("Arial", 16))
                arrow_label.setStyleSheet("color: #2196f3; margin: 5px;")
                self.flow_layout.addWidget(arrow_label)
        
        self.flow_layout.addStretch()
    
    def save_yaml(self):
        """Salvar arquivo YAML"""
        if not self.selected_steps:
            QMessageBox.warning(self, "Warning", "No steps selected. Please select at least one step.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Save CI/CD Configuration", 
            "qemula-cicd.yml", 
            "YAML Files (*.yml *.yaml);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write(self.yaml_preview.toPlainText())
                QMessageBox.information(self, "Success", f"YAML configuration saved to:\n{file_path}")
                self.log_message(f"YAML configuration saved to: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file:\n{str(e)}")
    
    def export_to_github(self):
        """Exportar para GitHub Actions"""
        if not self.selected_steps:
            QMessageBox.warning(self, "Warning", "No steps selected. Please select at least one step.")
            return
        
        github_path = ".github/workflows"
        if not os.path.exists(github_path):
            reply = QMessageBox.question(
                self, 
                "Create GitHub Workflow Directory",
                f"Directory '{github_path}' does not exist. Create it?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                try:
                    os.makedirs(github_path, exist_ok=True)
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to create directory:\n{str(e)}")
                    return
            else:
                return
        
        file_path = os.path.join(github_path, "qemula-cicd.yml")
        try:
            with open(file_path, 'w') as f:
                f.write(self.yaml_preview.toPlainText())
            QMessageBox.information(self, "Success", f"GitHub Actions workflow exported to:\n{file_path}")
            self.log_message(f"GitHub Actions workflow exported to: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export workflow:\n{str(e)}")
    
    def run_pipeline(self):
        """Executar pipeline usando act"""
        if not self.selected_steps:
            QMessageBox.warning(self, "Warning", "No steps selected. Please select at least one step.")
            return
        
        if self.is_running:
            self.log_message("⚠️ Pipeline is already running")
            return
            
        self.is_running = True
        self.run_pipeline_btn.setEnabled(False)
        self.stop_pipeline_btn.setEnabled(True)
        
        self.run_act_pipeline()
    
    def check_act_availability(self):
        """Verificar se act está instalado e disponível"""
        try:
            result = subprocess.run(["act", "--version"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                version = result.stdout.strip()
                self.log_message(f"✅ Act is available: {version}")
                # Também verificar se Docker está disponível
                self.check_docker_availability()
            else:
                self.log_message("❌ Act command failed - please ensure act is installed and in PATH")
        except subprocess.TimeoutExpired:
            self.log_message("⏰ Act check timed out")
        except FileNotFoundError:
            self.log_message("❌ Act not found - please install act from https://github.com/nektos/act")
        except Exception as e:
            self.log_message(f"❌ Error checking act: {str(e)}")
    
    def check_docker_availability(self):
        """Verificar se Docker está disponível"""
        try:
            result = subprocess.run(["docker", "version"], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.log_message("✅ Docker is available and running")
            else:
                self.log_message("❌ Docker command failed - please ensure Docker is running")
                self.log_message("💡 Tip: Start Docker Desktop and try again")
        except subprocess.TimeoutExpired:
            self.log_message("⏰ Docker check timed out - Docker may not be running")
        except FileNotFoundError:
            self.log_message("❌ Docker not found - please install Docker Desktop")
        except Exception as e:
            self.log_message(f"❌ Error checking Docker: {str(e)}")
    
    def run_act_pipeline(self):
        """Executar pipeline usando act"""
        try:
            # Verificar se o arquivo de workflow existe
            workflow_path = ".github/workflows/CI_workflow.yaml"
            if not os.path.exists(workflow_path):
                self.log_message("❌ Workflow file not found at .github/workflows/CI_workflow.yaml")
                self.pipeline_finished()
                return
            
            # Verificar se Docker está rodando antes de tentar usar act
            self.log_message("� Checking Docker availability...")
            try:
                docker_check = subprocess.run(["docker", "ps"], capture_output=True, text=True, timeout=5)
                if docker_check.returncode != 0:
                    self.log_message("❌ Docker is not running or not accessible")
                    self.log_message("💡 Please start Docker Desktop and try again")
                    self.pipeline_finished()
                    return
                else:
                    self.log_message("✅ Docker is running")
            except Exception as e:
                self.log_message(f"❌ Cannot access Docker: {str(e)}")
                self.log_message("💡 Please ensure Docker Desktop is installed and running")
                self.pipeline_finished()
                return
            
            self.log_message("�🚀 Starting Act execution of CI/CD pipeline...")
            self.log_message(f"📁 Using workflow: {workflow_path}")
            
            # Construir comando act com configurações específicas para Windows
            act_command = ["act"]
            
            # Se steps específicos foram selecionados, tentar rodar jobs específicos
            if len(self.selected_steps) < len(self.available_steps):
                selected_jobs = list(self.selected_steps.keys())
                self.log_message(f"🎯 Selected jobs: {', '.join(selected_jobs)}")
                self.log_message("ℹ️ Note: Act will run the complete workflow")
            else:
                self.log_message("🎯 Running all available jobs")
            
            # Adicionar flags úteis para Windows
            act_command.extend([
                "--rm",  # Remove containers após execução
                "--pull=false",  # Não fazer pull automático das imagens
                "--platform", "ubuntu-latest=catthehacker/ubuntu:act-latest",  # Plataforma específica
                "--container-daemon-socket", "-"  # Usar socket padrão
            ])
            
            # Executar em background thread
            working_dir = os.getcwd()
            command_str = " ".join(f'"{cmd}"' if " " in cmd else cmd for cmd in act_command)
            self.log_message(f"🔧 Executing: {command_str}")
            
            self.act_worker = ActWorkerThread(command_str, working_dir)
            self.act_worker.output_received.connect(self.on_act_output)
            self.act_worker.error_received.connect(self.on_act_error)
            self.act_worker.finished_execution.connect(self.on_act_finished)
            self.act_worker.start()
            
        except Exception as e:
            self.log_message(f"❌ Error starting act execution: {str(e)}")
            self.pipeline_finished()
    
    def on_act_output(self, output):
        """Callback para output do act"""
        # Filtrar e formatar output do act
        if output.strip():
            # Filtrar mensagens de debug verbosas que não são úteis para o usuário
            debug_filters = [
                "level=debug",
                "Handling container host",
                "Unable to load etag",
                "Defaulting container socket",
                "docker pull image=",
                "using DockerAuthConfig"
            ]
            
            # Verificar se a linha contém algum filtro de debug
            should_filter = any(filter_text in output for filter_text in debug_filters)
            
            if not should_filter:
                # Aplicar formatação baseada no conteúdo
                if "ERROR" in output.upper() or "FAIL" in output.upper():
                    self.log_message(f"❌ [ACT] {output}")
                elif "WARNING" in output.upper() or "WARN" in output.upper():
                    self.log_message(f"⚠️ [ACT] {output}")
                elif "INFO" in output.upper():
                    self.log_message(f"ℹ️ [ACT] {output}")
                elif "SUCCESS" in output.upper() or "COMPLETE" in output.upper():
                    self.log_message(f"✅ [ACT] {output}")
                elif output.startswith("["):
                    # Logs de jobs/steps
                    self.log_message(f"📋 [ACT] {output}")
                else:
                    # Output geral
                    self.log_message(f"[ACT] {output}")
    
    def on_act_error(self, error):
        """Callback para erros do act"""
        self.log_message(f"❌ [ACT ERROR] {error}")
    
    def on_act_finished(self, return_code):
        """Callback quando act termina"""
        if return_code == 0:
            self.log_message("✅ Act pipeline execution completed successfully!")
        else:
            self.log_message(f"❌ Act pipeline execution failed with code {return_code}")
        
        self.pipeline_finished()
    
    def pipeline_finished(self):
        """Callback quando pipeline termina (sucesso ou erro)"""
        self.is_running = False
        self.run_pipeline_btn.setEnabled(True)
        self.stop_pipeline_btn.setEnabled(False)
        
        if self.act_worker:
            self.act_worker.quit()
            self.act_worker.wait()
            self.act_worker = None
    
    def stop_pipeline(self):
        """Parar execução do pipeline"""
        if not self.is_running:
            return
            
        self.log_message("⏹️ Stopping pipeline execution...")
        
        if self.act_worker:
            self.act_worker.stop_execution()
            self.log_message("🛑 Act execution stopped by user")
        
        self.pipeline_finished()
    
    def clear_logs(self):
        """Limpar logs"""
        self.logs_area.clear()
    
    def log_message(self, message):
        """Adicionar mensagem aos logs"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.logs_area.append(f"[{timestamp}] {message}")
    
    def apply_styles(self):
        """Aplicar estilos globais"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 4px;
                margin-top: 1ex;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                background-color: white;
            }
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #cccccc;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
                border-color: #999999;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
            QComboBox, QSpinBox, QLineEdit {
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 6px;
                background-color: white;
            }
            QTabWidget::pane {
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #f0f0f0;
                border: 1px solid #cccccc;
                border-bottom-color: transparent;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom-color: white;
            }
            QTabBar::tab:hover {
                background-color: #e0e0e0;
            }
        """)

def main():
    app = QApplication(sys.argv)
    
    # Configurar tema
    app.setStyle('Fusion')
    
    window = QemulaCICDApp()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
