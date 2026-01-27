import sys
import os
import threading
import time
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QTextEdit, 
                             QFrame, QLineEdit, QSplitter, QListWidget, QTabWidget,
                             QListWidgetItem, QCheckBox, QScrollArea, QSlider,
                             QComboBox, QSpinBox, QGroupBox, QGridLayout, QStackedWidget,
                             QSplashScreen)
from PySide6.QtCore import Qt, QSize, Signal, QPropertyAnimation, QRect, QUrl, QThread
from PySide6.QtGui import QFont, QPalette, QColor, QIcon, QPainter, QPen, QBrush, QPixmap, QDesktopServices

# Adicionar o diretório atual ao path para permitir importações
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Importar os widgets específicos das outras abas
try:
    from frontend.control_tab import QemulaApp as ControlTab
except ImportError as e:
    print(f"Error importing control_tab: {e}")
    ControlTab = None

try:
    from frontend.docker_tab import QemulaDockerApp as DockerTab
except ImportError as e:
    print(f"Error importing docker_tab: {e}")
    DockerTab = None

try:
    from frontend.settings_tab import QemulaSettingsApp as SettingsTab
except ImportError as e:
    print(f"Error importing settings_tab: {e}")
    SettingsTab = None

try:
    from frontend.transciever_spw_tab import QemulaTransceiverSPWApp as SPWTab
except ImportError as e:
    print(f"Error importing transciever_spw_tab: {e}")
    SPWTab = None

try:
    from frontend.transciever_uart_tab import QemulaTransceiverUARTApp as UARTTab
except ImportError as e:
    print(f"Error importing transciever_uart_tab: {e}")
    UARTTab = None

try:
    from frontend.help_tab import QemulaHelpApp as HelpTab, AccordionItem
except ImportError as e:
    print(f"Error importing help_tab: {e}")
    HelpTab = None
    AccordionItem = None

try:
    from frontend.cicd_tab import QemulaCICDApp as CICDTab
except ImportError as e:
    print(f"Error importing cicd_tab: {e}")
    CICDTab = None

# Importar o backend diretamente no main
try:
    from backend.protocol_interface import ProtocolInterface
except ImportError as e:
    print(f"Error importing protocol_interface: {e}")
    ProtocolInterface = None

class ToggleSwitch(QWidget):
    """Widget de switch personalizado"""
    toggled = Signal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(60, 30)
        self._checked = False
        self._animation_duration = 200
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Desenhar o fundo do switch
        rect = self.rect().adjusted(2, 2, -2, -2)
        radius = rect.height() // 2
        
        if self._checked:
            painter.setBrush(QBrush(QColor(100, 200, 100)))  # Verde quando ativo
        else:
            painter.setBrush(QBrush(QColor(200, 200, 200)))  # Cinza quando inativo
        
        painter.setPen(QPen(QColor(150, 150, 150), 1))
        painter.drawRoundedRect(rect, radius, radius)
        
        # Desenhar o botão do switch
        button_radius = radius - 2
        if self._checked:
            button_x = rect.right() - button_radius * 2 - 2
        else:
            button_x = rect.left() + 2
            
        button_rect = rect.adjusted(0, 0, 0, 0)
        button_rect.setLeft(button_x)
        button_rect.setRight(button_x + button_radius * 2)
        button_rect.setTop(rect.top() + 2)
        button_rect.setBottom(rect.bottom() - 2)
        
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.setPen(QPen(QColor(150, 150, 150), 1))
        painter.drawEllipse(button_rect)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._checked = not self._checked
            self.toggled.emit(self._checked)
            self.update()
        super().mousePressEvent(event)
    
    def isChecked(self):
        return self._checked
    
    def setChecked(self, checked):
        if self._checked != checked:
            self._checked = checked
            self.update()
            self.toggled.emit(self._checked)

class EmulationWorkerThread(QThread):
    """Worker thread para executar comandos de emulação em background"""
    # Sinais para comunicação com a thread principal
    finished = Signal(dict)  # Emitido quando a operação termina
    error = Signal(str)      # Emitido quando há erro
    log_message = Signal(str)  # Emitido para logging
    
    def __init__(self, protocol, operation_type, *args, **kwargs):
        super().__init__()
        self.protocol = protocol
        self.operation_type = operation_type
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        """Executa a operação em background"""
        try:
            if self.operation_type == "start_emulation":
                self.log_message.emit("Executing start emulation in background thread...")
                response = self.protocol.send_start_emulation()
                
                # Para start emulation, tratar casos especiais onde timeout é normal
                if response is None:
                    self.log_message.emit("Start emulation command sent - server may be initializing")
                    self.finished.emit({"return": "Command sent", "status": "initializing"})
                elif isinstance(response, dict) and "error" in response:
                    error_msg = response["error"]
                    # Se for timeout, tratar como normal para start emulation
                    if "timeout" in error_msg.lower() or "waiting for server response" in error_msg.lower():
                        self.log_message.emit("Start emulation command sent - server is processing (timeout is normal)")
                        self.finished.emit({"return": "Command sent - processing", "status": "processing"})
                    elif "empty response" in error_msg.lower():
                        self.log_message.emit("Start emulation command sent - no immediate response (normal)")
                        self.finished.emit({"return": "Command sent - no response", "status": "sent"})
                    else:
                        # Outros erros são reportados normalmente
                        self.finished.emit(response)
                else:
                    self.finished.emit(response)
                    
            elif self.operation_type == "stop_emulation":
                self.log_message.emit("Executing stop emulation in background thread...")
                response = self.protocol.send_quit_emulation()
                self.finished.emit(response or {"return": "Stop command sent"})
            elif self.operation_type == "pause_emulation":
                self.log_message.emit("Executing pause emulation in background thread...")
                response = self.protocol.send_pause_machine()
                self.finished.emit(response or {"return": "Pause command sent"})
            elif self.operation_type == "unpause_emulation":
                self.log_message.emit("Executing unpause emulation in background thread...")
                response = self.protocol.send_unpause_machine()
                self.finished.emit(response or {"return": "Unpause command sent"})
            else:
                self.error.emit(f"Unknown operation type: {self.operation_type}")
        except Exception as e:
            self.error.emit(f"Error in {self.operation_type}: {str(e)}")

class QemulaMainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QEMULA APP")
        self.setGeometry(100, 100, 1400, 800)
        self.current_tab = 0  # 0: Docker, 1: Control, 2: SPW, 3: UART, 4: CI/CD, 5: Settings, 6: Help
        
        # Inicializar o protocolo backend para a aba Control
        self.protocol = None
        if ProtocolInterface:
            try:
                self.protocol = ProtocolInterface()
                print("Backend protocol interface initialized")
            except Exception as e:
                print(f"Error initializing backend: {e}")
        
        # Inicializar worker thread para operações de emulação
        self.emulation_worker = None
        
        # Inicializar variáveis SPW
        self.spw_receiver = None
        self.spw_is_connected = False
        
        # Inicializar referência para UART app
        self.uart_app = None
        
        # Inicializar referência para CI/CD app
        self.cicd_app = None
        
        # Inicializar estado dos botões de debug
        self.debug_button_states = [False, False, False]  # [btn_0, btn_1, btn_2]
        
        # Inicializar estado dos botões de settings
        self.settings_button_states = [False, False, False]  # [btn_0, btn_1, btn_2]
        
        # Inicializar lista para armazenar referências dos accordions de help
        self.accordion_items = []
        
        self.setup_ui()
        self.apply_styles()
    
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
        
        # Área principal com stacked widget
        self.stacked_widget = QStackedWidget()
        
        # Criar widgets para cada aba extraindo apenas o conteúdo principal
        self.docker_widget = self.create_docker_content()
        self.control_widget = self.create_control_content()
        self.spw_widget = self.create_spw_content()
        self.uart_widget = self.create_uart_content()
        self.cicd_widget = self.create_cicd_content()
        self.settings_widget = self.create_settings_content()
        self.help_widget = self.create_help_content()
        
        # Adicionar widgets ao stacked widget
        self.stacked_widget.addWidget(self.docker_widget)
        self.stacked_widget.addWidget(self.control_widget)
        self.stacked_widget.addWidget(self.spw_widget)
        self.stacked_widget.addWidget(self.uart_widget)
        self.stacked_widget.addWidget(self.cicd_widget)
        self.stacked_widget.addWidget(self.settings_widget)
        self.stacked_widget.addWidget(self.help_widget)
        
        main_layout.addWidget(self.stacked_widget)
        
        # Definir aba inicial
        self.switch_to_tab(1)  # Iniciar com Control
    
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
        self.menu_items = [
            ("Docker", 0),
            ("Control", 1),
            ("Transciever SPW", 2),
            ("Transciever UART", 3),
            ("CI/CD", 4),
            ("Settings", 5),
            ("Help", 6)
        ]
        
        self.menu_buttons = []
        
        for item_text, tab_index in self.menu_items:
            item = QPushButton(item_text)
            item.setFixedHeight(40)
            item.setFont(QFont("Arial", 10))
            item.clicked.connect(lambda checked, idx=tab_index: self.switch_to_tab(idx))
            
            # Estilo inicial (todos inativos)
            item.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #666666;
                    border: none;
                    border-radius: 8px;
                    text-align: left;
                    padding-left: 15px;
                }
                QPushButton:hover {
                    background-color: #f0f0f0;
                }
            """)
            
            self.menu_buttons.append(item)
            layout.addWidget(item)
        
        layout.addStretch()
        return sidebar
    
    def switch_to_tab(self, tab_index):
        """Muda para a aba especificada"""
        self.current_tab = tab_index
        self.stacked_widget.setCurrentIndex(tab_index)
        
        # Atualizar estilos dos botões
        for i, button in enumerate(self.menu_buttons):
            if i == tab_index:
                # Botão ativo
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #666666;
                        color: white;
                        border: none;
                        border-radius: 8px;
                        text-align: left;
                        padding-left: 15px;
                    }
                """)
            else:
                # Botão inativo
                button.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        color: #666666;
                        border: none;
                        border-radius: 8px;
                        text-align: left;
                        padding-left: 15px;
                    }
                    QPushButton:hover {
                        background-color: #f0f0f0;
                    }
                """)
    
    def create_docker_content(self):
        """Criar conteúdo da aba Docker"""
        if DockerTab is None:
            # Fallback se não conseguiu importar
            fallback_widget = QWidget()
            layout = QVBoxLayout(fallback_widget)
            error_label = QLabel("Docker Tab not available - import error")
            error_label.setStyleSheet("color: red; font-size: 14px;")
            layout.addWidget(error_label)
            return fallback_widget
            
        try:
            # Usar a implementação existente, mas adaptar para remover a sidebar
            docker_app = DockerTab()
            # Extrair apenas a área principal
            main_area = docker_app.create_main_area()
            return main_area
        except Exception as e:
            print(f"Error creating docker content: {e}")
            fallback_widget = QWidget()
            layout = QVBoxLayout(fallback_widget)
            error_label = QLabel(f"Error loading Docker Tab: {str(e)}")
            error_label.setStyleSheet("color: red; font-size: 14px;")
            layout.addWidget(error_label)
            return fallback_widget
    
    def create_control_content(self):
        """Criar conteúdo da aba Control com backend integrado"""
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Header
        header = self.create_control_header()
        layout.addWidget(header)

        # Tabs de controle
        tabs = self.create_control_tabs()
        layout.addWidget(tabs)

        # System logs
        logs_area = self.create_control_logs()
        layout.addWidget(logs_area)

        return main_widget
    
    def create_control_header(self):
        """Criar header da aba Control"""
        header = QFrame()
        header.setFixedHeight(60)  # Definir altura fixa menor
        layout = QHBoxLayout(header)
        layout.setContentsMargins(10, 5, 10, 5)  # Margens menores
        
        # Título da interface
        title = QLabel("Control Interface")
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
    
    def create_settings_content(self):
        """Criar conteúdo da aba Settings (apenas configurações, sem help)"""
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Header
        header = self.create_settings_header()
        layout.addWidget(header)

        # Scroll area para o conteúdo
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(20)
        
        # Seções de configuração (sem help)
        general_section = self.create_general_settings()
        scroll_layout.addWidget(general_section)
        
        connection_section = self.create_connection_settings()
        scroll_layout.addWidget(connection_section)
        
        scroll_layout.addStretch()
        
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        layout.addWidget(scroll_area)

        return main_widget
    
    def create_settings_header(self):
        header = QFrame()
        header.setFixedHeight(60)  # Definir altura fixa menor
        layout = QHBoxLayout(header)
        layout.setContentsMargins(10, 5, 10, 5)  # Margens menores
        
        # Título da interface
        title = QLabel("Application Settings")
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
    
    def create_general_settings(self):
        # Seção de configurações gerais
        group = QGroupBox("General Settings")
        group.setFont(QFont("Arial", 14, QFont.Bold))
        layout = QVBoxLayout(group)
        layout.setSpacing(15)
        
        # Auto-start application
        autostart_layout = QHBoxLayout()
        autostart_label = QLabel("Auto-start QEMULA on system boot")
        autostart_label.setFont(QFont("Arial", 12))
        autostart_layout.addWidget(autostart_label)
        autostart_layout.addStretch()
        
        self.autostart_switch = ToggleSwitch()
        autostart_layout.addWidget(self.autostart_switch)
        layout.addLayout(autostart_layout)
        
        # Log level
        log_layout = QHBoxLayout()
        log_label = QLabel("Log Level:")
        log_label.setFont(QFont("Arial", 12))
        log_layout.addWidget(log_label)
        
        self.log_combo = QComboBox()
        self.log_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        self.log_combo.setCurrentText("INFO")
        self.log_combo.setFixedWidth(120)
        log_layout.addWidget(self.log_combo)
        log_layout.addStretch()
        layout.addLayout(log_layout)
        
        # Max log files
        max_logs_layout = QHBoxLayout()
        max_logs_label = QLabel("Maximum log files to keep:")
        max_logs_label.setFont(QFont("Arial", 12))
        max_logs_layout.addWidget(max_logs_label)
        
        self.max_logs_spin = QSpinBox()
        self.max_logs_spin.setMinimum(1)
        self.max_logs_spin.setMaximum(100)
        self.max_logs_spin.setValue(10)
        self.max_logs_spin.setFixedWidth(80)
        max_logs_layout.addWidget(self.max_logs_spin)
        max_logs_layout.addStretch()
        layout.addLayout(max_logs_layout)
        
        return group
    
    def create_connection_settings(self):
        # Seção de configurações de conexão
        group = QGroupBox("Connection Settings")
        group.setFont(QFont("Arial", 14, QFont.Bold))
        layout = QVBoxLayout(group)
        layout.setSpacing(15)
        
        # SPW Connection timeout
        spw_timeout_layout = QHBoxLayout()
        spw_timeout_label = QLabel("SPW Connection Timeout (ms):")
        spw_timeout_label.setFont(QFont("Arial", 12))
        spw_timeout_layout.addWidget(spw_timeout_label)
        
        self.spw_timeout_spin = QSpinBox()
        self.spw_timeout_spin.setMinimum(100)
        self.spw_timeout_spin.setMaximum(30000)
        self.spw_timeout_spin.setValue(5000)
        self.spw_timeout_spin.setFixedWidth(100)
        spw_timeout_layout.addWidget(self.spw_timeout_spin)
        spw_timeout_layout.addStretch()
        layout.addLayout(spw_timeout_layout)
        
        # UART Baud Rate
        uart_baud_layout = QHBoxLayout()
        uart_baud_label = QLabel("UART Baud Rate:")
        uart_baud_label.setFont(QFont("Arial", 12))
        uart_baud_layout.addWidget(uart_baud_label)
        
        self.uart_baud_combo = QComboBox()
        self.uart_baud_combo.addItems(["9600", "19200", "38400", "57600", "115200"])
        self.uart_baud_combo.setCurrentText("115200")
        self.uart_baud_combo.setFixedWidth(120)
        uart_baud_layout.addWidget(self.uart_baud_combo)
        uart_baud_layout.addStretch()
        layout.addLayout(uart_baud_layout)
        
        # Auto-reconnect
        reconnect_layout = QHBoxLayout()
        reconnect_label = QLabel("Auto-reconnect on connection loss")
        reconnect_label.setFont(QFont("Arial", 12))
        reconnect_layout.addWidget(reconnect_label)
        reconnect_layout.addStretch()
        
        self.reconnect_switch = ToggleSwitch()
        self.reconnect_switch.setChecked(True)
        reconnect_layout.addWidget(self.reconnect_switch)
        layout.addLayout(reconnect_layout)
        
        return group
    
    def create_spw_content(self):
        """Criar conteúdo da aba SPW"""
        try:
            # Importar os componentes necessários
            from backend.reciever import SpaceWireReceiver
            from PySide6.QtWidgets import QFileDialog
            from PySide6.QtCore import QTimer
            import datetime
            
            # Criar widget principal
            main_widget = QWidget()
            layout = QVBoxLayout(main_widget)
            layout.setContentsMargins(20, 20, 20, 20)
            layout.setSpacing(20)

            # Header
            header = self.create_spw_header()
            layout.addWidget(header)

            # Conteúdo principal - dividido em duas seções
            content_layout = QVBoxLayout()
            
            # Seção superior - Received Data e Start Connection
            top_section = self.create_spw_top_section()
            content_layout.addWidget(top_section)
            
            # Seção inferior - Data Transmit e botões
            bottom_section = self.create_spw_bottom_section()
            content_layout.addWidget(bottom_section)
            
            layout.addLayout(content_layout)

            return main_widget
            
        except Exception as e:
            print(f"Error creating spw content: {e}")
            fallback_widget = QWidget()
            layout = QVBoxLayout(fallback_widget)
            error_label = QLabel(f"Error loading SPW Tab: {str(e)}")
            error_label.setStyleSheet("color: red; font-size: 14px;")
            layout.addWidget(error_label)
            return fallback_widget
    
    def create_uart_content(self):
        """Criar conteúdo da aba UART"""
        if UARTTab is None:
            # Fallback se não conseguiu importar
            fallback_widget = QWidget()
            layout = QVBoxLayout(fallback_widget)
            error_label = QLabel("UART Tab not available - import error")
            error_label.setStyleSheet("color: red; font-size: 14px;")
            layout.addWidget(error_label)
            return fallback_widget
            
        try:
            # Criar uma instância da UART app e manter referência
            self.uart_app = UARTTab()
            # Extrair apenas a área principal (sem sidebar)
            main_area = self.uart_app.create_main_area()
            return main_area
        except Exception as e:
            print(f"Error creating uart content: {e}")
            import traceback
            traceback.print_exc()
            fallback_widget = QWidget()
            layout = QVBoxLayout(fallback_widget)
            error_label = QLabel(f"Error loading UART Tab: {str(e)}")
            error_label.setStyleSheet("color: red; font-size: 14px;")
            layout.addWidget(error_label)
            return fallback_widget
    
    def create_cicd_content(self):
        """Criar conteúdo da aba CI/CD"""
        if CICDTab is None:
            # Fallback se não conseguiu importar
            fallback_widget = QWidget()
            layout = QVBoxLayout(fallback_widget)
            error_label = QLabel("CI/CD Tab not available - import error")
            error_label.setStyleSheet("color: red; font-size: 14px;")
            layout.addWidget(error_label)
            return fallback_widget
            
        try:
            # Criar uma instância completa da CI/CD app
            self.cicd_app = CICDTab()
            
            # Extrair APENAS a área principal (sem sidebar) da aplicação CI/CD
            main_area = self.cicd_app.create_main_area()
            
            return main_area
        except Exception as e:
            print(f"Error creating cicd content: {e}")
            import traceback
            traceback.print_exc()
            fallback_widget = QWidget()
            layout = QVBoxLayout(fallback_widget)
            error_label = QLabel(f"Error loading CI/CD Tab: {str(e)}")
            error_label.setStyleSheet("color: red; font-size: 14px;")
            layout.addWidget(error_label)
            return fallback_widget
    
    def create_help_content(self):
        """Criar conteúdo da aba Help"""
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Header
        header = self.create_help_header()
        layout.addWidget(header)

        # Scroll area para o conteúdo
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(20)
        
        # Seção de ajuda com accordions
        help_section = self.create_help_section()
        scroll_layout.addWidget(help_section)
        
        scroll_layout.addStretch()
        
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        layout.addWidget(scroll_area)

        return main_widget
    
    def create_help_header(self):
        header = QFrame()
        header.setFixedHeight(60)  # Definir altura fixa menor
        layout = QHBoxLayout(header)
        layout.setContentsMargins(10, 5, 10, 5)  # Margens menores
        
        # Título da interface
        title = QLabel("Help & Documentation")
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
    
    def create_help_section(self):
        # Seção de ajuda com accordions completos
        group = QGroupBox("QEMULA Complete Documentation & Help Guide 📚")
        group.setFont(QFont("Arial", 14, QFont.Bold))
        layout = QVBoxLayout(group)
        layout.setSpacing(10)
        
        # Adicionar uma introdução antes dos accordions
        intro_label = QLabel("""
        <div style='background-color: #e3f2fd; padding: 15px; border-radius: 8px; margin-bottom: 10px;'>
        <h3 style='color: #1976d2; margin: 0;'>📋 QEMULA Application v0.1.0 - Complete User Manual</h3>
        <p style='margin: 5px 0 0 0; color: #424242;'>
        Welcome to the comprehensive documentation for QEMULA - your complete QEMU emulation management solution.
        Expand any section below to access detailed information about specific features and functionality.
        </p>
        </div>
        """)
        intro_label.setWordWrap(True)
        layout.addWidget(intro_label)
        
        # Lista para armazenar referências dos accordion items
        self.accordion_items = []
        
        # Itens de ajuda completos baseados na documentação oficial
        help_items = [
            ("Official Requirements", """
QEMULA Official Requirements

Introduction:
Table of signatures

Introduction:
The Embedded Electronic Systems Center (NSEE) of the Instituto Mauá de Tecnologia (IMT) has a solid record of accomplishment in developing solutions for space missions, which began in 2011 with the SimuCam project for the European Space Agency's (ESA) PLATO mission, in partnership with institutions such as LESIA, DLR, and IWF. Although SimuCam is not the focus of this work, its success positioned NSEE as an important collaborator in international space projects.
As a result of this expertise, NSEE was invited to participate in the VERITAS and EnVision missions led by NASA's Jet Propulsion Laboratory (JPL) and ESA. Both missions aims to study Venus to understand its geological evolution and assess conditions for life. Within them, the German Aerospace Center (DLR) is developing the Venus Emissivity Mapper (VEM), a spectrometer that includes an optical component and an electronic control unit called VenSpec-M. The software and optics of VenSpec-M are being developed by the DLR, and the partnership with NSEE involves the development of a virtualized version of the electronic interfaces of this instrument using the QEMU emulator.
The main goal of this project is to create a virtualized environment that allows for the development and validation of space software without the need for physical hardware, regarding the control unit VenSpec-M. The virtualization of VenSpec-M aims to faithfully replicate the characteristics and behavior of the real hardware, including the simulation of a virtual SpaceWire link for communication with other control units. This enables the configuration of test data and the injection of simulated faults, functionalities that would be unfeasible or risky on validated physical hardware. Additionally, the virtualized system will be integrated into continuous integration (CI/CD) pipelines, allowing for autonomous testing and validation of the software developed for VenSpec-M.

German Aerospace Center::
The German Aerospace Center, known as DLR (Deutsches Zentrum für Luft- und Raumfahrt), is Germany's national research center for aeronautics, space, energy, transport, and security. Established to conduct research and development activities in these fields, DLR plays a crucial role in advancing scientific knowledge and technological innovations, not just within Germany but globally.
DLR collaborates with various international partners, including space agencies like NASA and ESA (European Space Agency). Its involvement in major missions, such as those exploring Mars, the Moon, or studying Earth's climate, highlights its global influence. For example, DLR is involved in high-profile missions like Mars Express, Rosetta, and VERITAS, providing essential technologies like scientific instruments and control systems.
DLR's efforts position it as a leader in aerospace innovation, shaping the future of space exploration, air travel, and sustainable technology.

Embedded Electronic Systems Center::
The NSEE (Núcleo de Sistemas Eletrônicos Embarcados), or Embedded Electronic Systems Center, is a specialized research and development center within the Instituto Mauá de Tecnologia (IMT) in Brazil. The center focuses on the design, development, and integration of advanced embedded electronic systems, particularly for challenging applications in space, aeronautics, and other high-tech industries.
The NSEE is committed to technological innovation, integrating cutting-edge tools like continuous integration/continuous deployment (CI/CD) pipelines into its processes. This ensures that the software and hardware systems it develops are rigorously tested and validated through automated processes, enhancing the reliability and performance of the solutions for critical applications.
Through its expertise in embedded electronics and international collaborations, NSEE plays a crucial role in advancing space technology and other high-stakes sectors that require robust, reliable electronic systems.

2.1. 	General Structure:
To provide a detailed description of the project, its overall structure and data flow will be specified with a focus on normal operation.
Figure 1 – General overview of QEMULA's Structure.
Source: the authors.
From Figure 1 above, it is possible to understand the general structure of QEMULA itself. Ideally, QEMULA is contained within a Docker container, isolated from an external system, and exposes at least three TCP/IP links that fall into three different categories:
Control Link: Comprising a single TCP/IP link, it is responsible for receiving commands and sending reports related to the control and interaction with the emulated instrument.
Instrument Link: Comprising an arbitrary number of TCP/IP links, it is responsible for the transmission and reception of data, which are essentially analogous to the SpaceWire protocol, in direct communication with the emulated instrument.
Debug Link: Comprising a single TCP/IP connected to QEMULA Controller, it is responsible for sending and receiving Debug commands through an interface mediated by the GDB Server. Its presence at emulation time is optional: the user may configure the GDB Server exclusively by Instrument Link commands, debugging the test code indirectly.
For the last two categories of TCP/IP links, there is no immediate need for a dedicated interface with the emulated QEMU instrument, as they are directly connected to it. However, for the first category, the implementation of a controller is required, which will receive user commands and requests for the system based on a defined protocol. The controller will then take appropriate actions within the system or on the emulated instrument. In certain cases, the received command may also require information from the emulated instrument, in which case the controller will be responsible for generating and sending an appropriate report through the Control Link.
It is important to note that the modular structure presented here may undergo changes during the further development and expansion of QEMULA, to meet future requirements that may arise.

2.2. 	System Data Flow:
Figure 2 – General overview of QEMULA's Data Flow.
Source: the authors.
Figure 2 presents a flow diagram illustrating the data flow within QEMULA, an environment designed to simulate a range of use cases detailed in the accompanying documentation.
The process begins with the user submitting the packets that will be simulated. These packets are essential for driving the simulation scenarios. Once the packets are received, they undergo processing and normalization to conform to the internal protocol of the DLR CI-CD Actor interface.
After normalization, the packets are ready for transmission. The Socket Transmitter takes over at this stage, managing the transfer of control data between the user interface and the system's Control Link (or Control Interface). This transmission occurs over TCP, so it is necessary to correctly configure the socket's address and transmission port.
The next stage in the data flow involves enabling the socket for communication. Although this description does not go into the potential causes of failure, it is assumed that the protocol message is successfully transmitted to the Control Interface. The first action of the Control Interface upon receiving the packet is to process its contents, which involves interpreting the header and body. This is handled by the Receiver routines, which classify the packets based on predefined message code tables. Once classified, the message is stored in a FIFO Buffer, where it waits for further processing.
Access to this buffer is managed by a routine known as Try Get Buffer, which retrieves the first item in the queue, allowing the packet to proceed. However, whether the packet advances depend on feedback from the QEMU State Machine, which operates in two primary states:
CONFIG: Responsible for configuring all simulation parameters.
RUN: Indicates that the emulated hardware is ready to accept simulation data.
Once the required conditions are met, the packet moves forward to the processing stage. During this phase, control methods are identified, and the system advances to execute one of several operations in QEMU. These include various commands, which can be seen at QEMULA's User Manual (QEMULA-UM-I0.1).
Certain commands interact directly with the QEMU Monitor's library, issuing commands and receiving answers from the running QEMU machine. Before proceeding, the system requires a response from the Socket Controller channel. Once received, the control edge code compiles and repackages the packet, which is then externalized from the Docker environment via TCP. This is achieved through communication between the Sender and Receiver components of the user interface.
This description represents the first version of the QEMULA environment, focusing on the control requirements and the interface between QEMU, Docker, and the user. A careful review of the content is advised, and any necessary adjustments should be made to both the diagram and the accompanying text.

QEMULA's Use Cases:
The QEMULA system, essentially, encompasses two general use cases in its operation: system execution and system configuration.
In the configuration use case, four specific use cases are derived, namely the configuration of emulation parameters, code injection, logging setup, and housekeeping configuration. For the execution use case, three specific use cases are derived, comprising emulation control and management, interaction with the emulated instrument, and operation in debug mode. The overall representation of the system's use cases, and their respective derivations can be better visualized in Figure 1 below.

Requirements:
This section outlines the expected requirements for the QEMULA project. Beginning with a general requirements diagram, these requirements will be detailed and specified for further clarity.
To clarify the types of imperative terms used in each specification, refer to Table 1 below.
Table 1 – Description of usual imperative terms used in requirements.
Source: the authors.
Complementing the terms presented, the types of verification designed for testing the proposed requirements will also be described. These definitions can be found in Table 2.
Table 2 – Description of verification terms used in requirements.
Source: the authors.

4.1. 	Requirements Diagram and General Overview:
In Figure 2 below, the conceptual groupings of the requirements are outlined, which include Main Requirements, Emulation Requirements, Control Interface Requirements, Debug Requirements, and Instrument Interface Requirements.
Figure 2 – General requirements of QEMULA.
Source: the authors.

4.2. 	Main Requirements:
Note 1: modular architecture enables future customization and adaptation of the system to meet upcoming requirements.

4.3. 	Emulation Requirements:
Note 1: this requirement matches the specification proposed at QEM-REQ-MA-10.
Note 2: ultimately, this would lead to entirely emulating all of VenSpec-M software interfaces device, proposed in QEM-REQ-MA-01.

4.4 	Control Interface Requirements:
Note 1: this statement is true even if QEMULA doesn't have the need to return extra information.
Note 1: like pausing the emulation, dumping memory…
Note 1: CONFIG_STATE and RUN_STATE, as described in QEM-REQ-MA-06.
Note 1: this ensures that future customization and addition of new requisitions and answers is possible and viable.
Note 1: the execution status should be better specified at the requisition and answer packages description.
Note 1: for each type of package, the content of its header and body must be specified, based on the specific type of function to which it is related.
Note 1: this is especially relevant to the "Inject external code" operation pointed in QEM-REQ-CI-14, because of the possible size of the software to be tested in QEMULA.

4.5 	Instrument Interface Requirements:
Note 1: Depending on the version of the emulated instrument implemented, there may be a varying number of stdout-type devices that require a specific TCP/IP link.
Note 1: this term is utilized here, because it's not imperatively necessary that the SpW Codecs must be directly connected with the instrument TCP/IP links.
Note 1: including its package structure, control and data characters and timecodes, especially.
Note 1: this ensures transferred data liability.
Note 1: this depends directly of DLR's specifications, as shown in document RA-01.

Last Updated: 2025-09-02 17:06
Source: Official Requirements.docx
            """),

            ("Introduction", """
QEMULA is an integrated environment and framework designed to emulate the logical processing of the VenSpec-M processing unit. This unit is a core component of the Venus Emissivity Mapper (VEM) spectrometer instrument, which will support the VERITAS and EnVision missions. One of the primary objectives of QEMULA is to provide a virtual testing environment that replicates the behavior of the satellite's embedded hardware responsible for processing spectrometer data.

To achieve accurate emulation of VenSpec-M hardware configurations, the NSEE team conducted an in-depth analysis of QEMU, an open-source software developed by Fabrice Bellard. QEMU enables processor emulation and full system virtualization, making it an ideal foundation for this project. Following extensive comparisons and testing, the team selected QEMU as the core of QEMULA due to its compatibility with the LEON3 processor from Frontgrade Gaisler, its seamless integration with most relevant peripherals, and its adaptability for creating custom components.

This manual provides guidance on the emulation and simulation of the VenSpec-M processing unit, emphasizing the SpaceWire communication protocol. It outlines the software components and digital infrastructure required to meet the testing specifications, as detailed in the QEMULA Official Requirements document.

To meet the requirements of the first delivery, the user can interact with QEMULA through the following system TCP/IP interfaces:

Control Interface: A layer and set of frameworks responsible for managing and supervising the general operation of the simulations carried out by the QEMU emulator running inside of QEMULA. Also, this interface enables debugging capabilities when the emulation is running, through a GDB Server provided directly by QEMU.  This interface has only 1 TCP/IP link and its own control protocol, which will be better described later in this document.

Instrument Interface: Responsible for enabling communication between QEMULA's user and the emulated instrument itself. Because the main emulated system interfaces are, essentially, SpaceWire (SpW) links, this interface aims to emulate their behaviour, providing several TCP/IP links that replicate the instruments real SpW interfaces.

Debug Interface: A module designed to monitor and address errors or failures during the execution and testing of software within QEMULA. This interface enables users to track performance issues, bugs, and unexpected behaviors, allowing for the analysis of both hardware and software operations to pinpoint the source and nature of errors. The connection is primarily managed by a GDB server within QEMULA, which can be externalized or kept internal during emulation.

The following items in this document will detail the use and preparation of the environment to meet the requirements of the first release of the project, with detailed instructions on how to operate the delivered system.

Last Updated: 2025-09-02 17:06
Source: QEMULA_User_Manual.docx
            """),

            ("Processor:", """
64-bit processor (x86_64 or ARM) with at least two nuclei available.

Hardware virtualization support (Intel VT-x or AMD-V) is recommended for optimized performance but not strictly necessary.

Last Updated: 2025-09-02 17:06
Source: QEMULA_User_Manual.docx
            """),

            ("Installation", """
To run the application, the user only needs to have the main Docker components (Engine, Compose, and Build) or Docker Desktop installed. The following sections will comprehend instructive links and pages on how to install Docker in different operational systems.

Last Updated: 2025-09-02 17:06
Source: QEMULA_User_Manual.docx
            """),

            ("To finish, the user must only enable Docker:", """
When successfully installed, the user could see the Docker Desktop icon available (if the system has a graphical interface), as seen in Figure 1.

For more questions on how to install Docker Desktop on Ubuntu/Debian, please visit the Docker Manuals on this link.

Last Updated: 2025-09-02 17:06
Source: QEMULA_User_Manual.docx
            """),

            ("3.2.    For other Linux distributions (Red Hat Enterprise and others)", """
In a Linux environment, the user needs to follow the instructions on how to install Docker Desktop, following the instructions available on this link.

It is recommended to install Docker Desktop due to its compatibility and stability. However, if preferred, users can opt to install Docker Engine, Docker Compose, and Docker Build separately by following the instructions provided at this link.

Last Updated: 2025-09-02 17:06
Source: QEMULA_User_Manual.docx
            """),

            ("3.3.    For Windows (x86 and ARM)", """
In a Windows environment, the user needs to follow the instructions on how to install Docker Desktop, following the instructions available on this link.

Last Updated: 2025-09-02 17:06
Source: QEMULA_User_Manual.docx
            """),

            ("Configuration and Initialization", """
To set up QEMULA, the user must first download the latest release available in the NSEE repository via the provided link.

Initialization involves running two scripts available in the downloaded release directory. First, execute the configure_qemula script to load QEMULA's image and prepare the environment. Then, execute the start_qemula script to launch QEMULA Docker container. Finally, execute the stop_qemula script to stop QEMULA, when convenient. Note that all scripts require Docker Desktop (or Docker Engine) to be running beforehand. Also, no additional configuration is necessary for running QEMULA when the system's image is already loaded, so configure_qemula script can only be executed one time, while start_qemula and stop_qemula can be executed multiple times.

For Windows users, the .bat scripts should be executed, which are located on the /Windows/ directory. Linux users should run the corresponding .sh scripts, which are located on the /Linux_Unix/ directory. Both versions perform the same functions, tailored to their respective operating systems.

PS: For Linux environments, if the scripts couldn't be executed, it may be necessary to execute the following commands:

After that, the system should be initialized correctly. Then, the user needs to connect to QEMULA's control link to send requisitions and receive answers, connecting to port 4322 of localhost.

When needed, the user should have the capability to connect to QEMULA's instrument link and debug link:

PS: For debugging purposes, it is important that the code to be tested in QEMULA's environment be compiled with a -g flag, preferably without any optimizations enabled.

Last Updated: 2025-09-02 17:06
Source: QEMULA_User_Manual.docx
            """),

            ("QEMULA's Control Interface Usage", """
In this topic, some steps will be outlined so that the user or system can arbitrarily command the behavior of QEMULA through its defined control interface, as well as manage the codes to be tested and the emulation itself.

Initially, the user must connect to the QEMULA system through the control interface, which is open via a TCP/IP server at IP localhost:4322.

Once the connection is successfully established, the user or system can then send requisitions for QEMULA to execute predetermined actions. These requisitions involve answers from QEMULA, both defined through a standardized protocol (see QEMULA's Official Requirements for more information).

It is important to note that the QEMULA system operates in two different states: configuration (CONFIG) and execution (RUN). Therefore, it is the user's responsibility to configure the emulation parameters and related settings during the CONFIG state of the machine, to begin the emulation itself and transition it to RUN mode.

Essentially, every requisition will take the form described in Figure 2 below.

Thus, it is up to the user to determine the COMMAND_ID to be used, which is an arbitrary and unique value specific to each requisition sent. The other fields will be elaborated on in the future. The general format of an answer, the response packet from QEMULA, can be seen below in Figure 3.

Each answer packet received by the user contains the same ANSWER_ID that matches the COMMAND_ID of the request that generated the answer. This allows the user to associate the received answer with a previously sent request. The other package fields will also be elaborated on in the future.

In this way, the fields particular to each type of requisition supported by the system can be viewed in the Table 1 below.

Table 1 – Requisitions packages supported and their respective fields.

Source: the authors.

PS: the commands marked in red are not implemented in this first version, being reserved for future improvements.

In this way, the user will be able to send commands that configure the emulation and start the emulation in the CONFIG state using the "Start Emulation" requisition, as well as commands that manage and terminate the emulation, using the "Quit Emulation" in the RUN state, generalizing the behavior of the machine.

PS: It is imperative to mention that the system can automatically transition from the RUN state to the CONFIG state if the injected .ELF code completes its execution. Similarly, as previously mentioned, this transition can also occur artificially if the user submits a 'Quit Emulation' request.

Complementing the table above, it is also necessary to display the fields of the answer packets according to their originating requisition. The BODY_CONTENT field of each generated answer is shown in Table 2 below.

Table 2 – Answer packages supported and their respective fields.

Source: the authors.

With respect to the ANSWER_STATUS field in each answer, its values are detailed in Table 3, reflecting whether any errors were encountered by the system during the processing of the originating request.

Table 3 – Relation between the ANSWER_STATUS values and its execution status.

Source: the authors.

In this way, the user will be able to send commands that configure the emulation and start it in the CONFIG state, as well as commands that manage and terminate it in the RUN state, generalizing the behavior of the machine.

For the RUN state, it is possible to visualize that the user can send also send GDB debug commands to QEMULA's GDB interface. For that, the user must configure debugging mode in the CONFIG state without enabling the debug interface, transition to the RUN state and, finally, send the Control Interface GDB related requisitions.

It is worth noting that, for both the request and response packets, the 2-byte CRC is determined using the CRC16-CITT algorithm, with an initial hexadecimal value of 0xFFFF.

Last Updated: 2025-09-02 17:06
Source: QEMULA_User_Manual.docx
            """),

            ("QEMULA's Debug Interface Usage", """
The QEMULA debug interface becomes accessible only after the user enables the debug mode and configures the debug interface in the system's CONFIG state, subsequently transitioning to the RUN mode.

Therefore, the user must connect to the system's TCP/IP debug port, assuming it operates as a standard GDB Server. Once connected, the user can debug the code under test through its completion using the interfaces provided by GDB. It is imperative that the user specifies, via the GDB Server, the code symbols to be debugged. To do so, the user must previously download the BCC binaries provided by Frontgrade Gaisler (available on this link), which include the GDB related ones, and insert them into the system's PATH, subsequently executing the following commands:

Then, GDB should be able to connect with QEMU's debugging server, enabling the user to debug the previously injected .ELF code. When the user chooses to artificially stop the emulation through the "Quit Emulation" command, the Debug Link closes automatically.

Last Updated: 2025-09-02 17:06
Source: QEMULA_User_Manual.docx
            """),

            ("QEMULA's Instrument Interface Usage", """
The QEMULA instrument interface, composed of multiple TCP/IP links, provides direct communication between the user and the emulated SpaceWire communication interfaces of the emulated instrument. The instrument interface not only provides SpaceWire link emulation, but also any communication channel that belongs to the instrument (UART links, for example). The data can be multiplexed or not (TBD) and was formatted to be similar to the real SpaceWire format, allowing artifacts such as EEPs to be injected at any time, or disconnections errors and such. The instrument link is still being developed, due to its need to properly integrate to the low-level simulation and data controller.

Particularly when utilizing the SpaceWire interfaces of the emulated system, communication is established as illustrated in Figure 4 below. Ideally, each atomic unit of communication—comprising N-Chars, Timecodes, Tokens, among others—is encapsulated within a 16-bit TCP/IP packet. Of these 16 bits, 8 are allocated for defining the packet's identifier, while the remaining 8 bits carry the data payload. Within the identifier field, 4 bits are reserved to indicate the source or destination of the TCP/IP packet, and the remaining 4 bits specify its category (e.g., N-Char, Timecode, Token, Error, etc.).

Figure 4 – General structure of a QEMULA' s SpaceWire over TCP/IP atomic package.

Source: the authors.

Like the debug interface, the user can connect to the instrument ports at any point while the system is in its RUN state. Also, the instrument interface is automatically closed if the user artificially terminates the emulation via the 'Quit Emulation' command or if the inserted code reaches the end of its execution.

Last Updated: 2025-09-02 17:06
Source: QEMULA_User_Manual.docx
            """),

            ("QEMULA's Basic Tutorial with Provided Testing Code", """
To provide an initial testing platform for the delivered system, a Python script named QEMULAs_Testing_Code.py was developed, which is available on QEMULA's release. This script establishes a connection with the QEMULA system's control link, enabling the exchange of requests and responses.

This section, therefore, presents a straightforward tutorial for initializing QEMULA, using the developed testing code as a foundation for system control.

Initially, the user must configure the QEMULA runtime environment using the configure_qemula script while running Docker Desktop or Docker Engine. Subsequently, the start_qemula script should be executed to launch the system. As mentioned previously, Both scripts must be used with attention to the operational system: .bat scripts for Windows and .sh scripts for Linux/Unix.

Once the system is running, the user must execute the QEMULAs_Testing_Code.py script using the Python3 interpreter available on the system. If done successfully, the user must visualize the screen as seen in Figure 4 below, representing the code's main menu:

Thus, upon initialization, the script connects to the QEMULA control link, enabling the transmission of the commands listed in its menu. Each command sent elicits a response from the system, which is displayed to the user in a manner similar to that shown in Figure 5, as exemplified by the execution of a "Verify State" command.

As previously described in this manual, only specific commands can be accepted by QEMULA in certain operational states. Therefore, users must pay attention to the command groupings detailed in the menu:

General Commands: These can be sent in any QEMULA state.

CONFIG Commands: These must be sent only while QEMULA is in the CONFIG state. To verify the system's state, the 'Verify State' command can be used.

RUN Commands: These must be sent only while QEMULA is in the RUN state. To verify the system's state, the 'Verify State' command can be used.

Finally, in a typical system execution, the following commands are recommended to be executed in this order: Inject .ELF, Inject AHBROM, Config RAM, Config Debug, Set OS ABI for Debug, and Start Emulation. Afterward, the QEMU emulated system will be initialized, enabling the execution of commands related to the RUN state of QEMULA, according to the user's needs. When necessary, the user may send the Quit Emulation command to end the QEMU emulation and return to the CONFIG state of the system.

Last Updated: 2025-09-02 17:06
Source: QEMULA_User_Manual.docx
            """)
        ]
        
        # Usar AccordionItem se disponível, senão usar implementação simples
        if AccordionItem:
            for title, content in help_items:
                accordion_item = AccordionItem(title, content)
                self.accordion_items.append(accordion_item)
                layout.addWidget(accordion_item)
        else:
            # Fallback para implementação simples se AccordionItem não estiver disponível
            for title, content in help_items:
                accordion_item = self.create_accordion_item(title, content)
                layout.addWidget(accordion_item)
        
        return group
    
    def create_accordion_item(self, title, content):
        """Criar um item accordion expansível"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header do accordion
        header = QPushButton(f"{title} ▼")
        header.setFixedHeight(50)
        header.setStyleSheet("""
            QPushButton {
                background-color: #333333;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                text-align: left;
                padding-left: 20px;
                padding-right: 20px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
        """)
        
        # Conteúdo do accordion
        content_widget = QWidget()
        content_widget.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border: 1px solid #e0e0e0;
                border-top: none;
                border-radius: 0 0 8px 8px;
                padding: 15px;
            }
        """)
        
        content_layout = QVBoxLayout(content_widget)
        content_label = QLabel(content)
        content_label.setWordWrap(True)
        content_label.setFont(QFont("Arial", 11))
        content_layout.addWidget(content_label)
        
        content_widget.setVisible(False)
        
        def toggle_content():
            is_visible = content_widget.isVisible()
            content_widget.setVisible(not is_visible)
            icon = "▲" if not is_visible else "▼"
            header.setText(f"{title} {icon}")
        
        header.clicked.connect(toggle_content)
        
        layout.addWidget(header)
        layout.addWidget(content_widget)
        
        return container
    
    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }
            QTabWidget::pane {
                border: 1px solid #cccccc;
                border-radius: 4px;
            }
            QTabWidget::tab-bar {
                alignment: center;
            }
            QTabBar::tab {
                background-color: #f0f0f0;
                padding: 8px 16px;
                margin: 2px;
                border-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #007bff;
                color: white;
            }
            QLineEdit {
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 5px;
                font-size: 11px;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QComboBox, QSpinBox {
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 5px;
                background-color: white;
            }
            QComboBox:hover, QSpinBox:hover {
                border-color: #007bff;
            }
        """)
    
    # Métodos para Control Tab
    def create_control_tabs(self):
        """Criar tabs da aba Control"""
        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.North)
        
        # Tab Emulation
        emulation_tab = self.create_emulation_tab()
        tabs.addTab(emulation_tab, "Emulation")
        
        # Tab Debug
        debug_tab = self.create_debug_tab()
        tabs.addTab(debug_tab, "Debug")
        
        # Tab Settings
        settings_tab = self.create_control_settings_tab()
        tabs.addTab(settings_tab, "Settings")
        
        return tabs
    
    def create_emulation_tab(self):
        """Criar aba de emulação com design conforme imagem"""
        emulation_tab = QWidget()
        layout = QVBoxLayout(emulation_tab)
        layout.setSpacing(30)
        layout.setContentsMargins(50, 50, 50, 50)
        
        # Primeira linha - Pause Emulation, Unpause Emulation, Read I/O
        first_row = QHBoxLayout()
        first_row.setSpacing(80)
        
        # Pause Emulation
        pause_btn = QPushButton("⏸️ Pause Emulation")
        pause_btn.setFixedSize(180, 50)
        pause_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a1a1a;
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 13px;
                font-weight: bold;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #333333;
            }
        """)
        pause_btn.setToolTip("Temporarily suspend the current emulation session.\nThe virtual machine state is preserved and can be resumed later.")
        pause_btn.clicked.connect(self.on_pause_emulation)
        first_row.addWidget(pause_btn)
        
        # Unpause Emulation
        unpause_btn = QPushButton("▶️ Unpause Emulation")
        unpause_btn.setFixedSize(180, 50)
        unpause_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a1a1a;
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 13px;
                font-weight: bold;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #333333;
            }
        """)
        unpause_btn.setToolTip("Resume a previously paused emulation session.\nThe virtual machine will continue from where it was paused.")
        unpause_btn.clicked.connect(self.on_unpause_emulation)
        first_row.addWidget(unpause_btn)
        
        # Read I/O
        read_io_btn = QPushButton("📖 Read I/O")
        read_io_btn.setFixedSize(160, 50)
        read_io_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a1a1a;
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 13px;
                font-weight: bold;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #333333;
            }
        """)
        read_io_btn.setToolTip("Read data from a specific memory address in the virtual machine.\nEnter the hexadecimal address in the field below (e.g., 0x1000 or 1000).")
        read_io_btn.clicked.connect(self.on_read_io)
        first_row.addWidget(read_io_btn)
        
        layout.addLayout(first_row)
        
        # Campo de entrada para endereço (alinhado com Read I/O)
        addr_input_row = QHBoxLayout()
        addr_input_row.setSpacing(80)
        
        # Espaço equivalente aos dois primeiros botões
        spacer1 = QWidget()
        spacer1.setFixedWidth(180)  # Pause Emulation
        addr_input_row.addWidget(spacer1)
        
        spacer2 = QWidget()
        spacer2.setFixedWidth(180)  # Unpause Emulation
        addr_input_row.addWidget(spacer2)
        
        # Campo de entrada alinhado com Read I/O
        self.addr_input = QLineEdit()
        self.addr_input.setPlaceholderText("Enter ADDR in hex:")
        self.addr_input.setFixedSize(160, 40)
        self.addr_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #cccccc;
                border-radius: 20px;
                padding: 10px 15px;
                font-size: 13px;
                background-color: #f8f9fa;
                color: #666666;
            }
            QLineEdit:focus {
                border-color: #007bff;
                background-color: white;
                color: black;
            }
        """)
        self.addr_input.setToolTip("Enter the hexadecimal memory address to read from.\nSupported formats: 0x1000, 1000, 0X1000")
        addr_input_row.addWidget(self.addr_input)
        
        layout.addLayout(addr_input_row)
        
        # Segunda linha - Stop Emulation, Start Emulation, Write I/O
        second_row = QHBoxLayout()
        second_row.setSpacing(80)
        
        # Stop Emulation
        stop_btn = QPushButton("⏹️ Stop Emulation")
        stop_btn.setFixedSize(180, 50)
        stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a1a1a;
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 13px;
                font-weight: bold;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #333333;
            }
        """)
        stop_btn.setToolTip("Terminate the current emulation session completely.\nAll virtual machine state will be lost and needs to be restarted.")
        stop_btn.clicked.connect(self.on_stop_emulation)
        second_row.addWidget(stop_btn)
        
        # Start Emulation
        start_btn = QPushButton("▶️ Start Emulation")
        start_btn.setFixedSize(180, 50)
        start_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a1a1a;
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 13px;
                font-weight: bold;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #333333;
            }
        """)
        start_btn.setToolTip("Initialize and start a new QEMU virtual machine emulation session.\nThis may take several seconds to complete. Server timeouts are normal during startup.")
        start_btn.clicked.connect(self.on_start_emulation)
        second_row.addWidget(start_btn)
        
        # Write I/O
        write_io_btn = QPushButton("✏️ Write I/O")
        write_io_btn.setFixedSize(160, 50)
        write_io_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a1a1a;
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 13px;
                font-weight: bold;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #333333;
            }
        """)
        write_io_btn.setToolTip("Write data to a specific memory address in the virtual machine.\nEnter address and value in the field below using format: ADDR/VAL (e.g., 1000/FF).")
        write_io_btn.clicked.connect(self.on_write_io)
        second_row.addWidget(write_io_btn)
        
        layout.addLayout(second_row)
        
        # Campo de entrada para valor (alinhado com Write I/O)
        val_input_row = QHBoxLayout()
        val_input_row.setSpacing(80)
        
        # Espaço equivalente aos dois primeiros botões
        spacer3 = QWidget()
        spacer3.setFixedWidth(180)  # Stop Emulation
        val_input_row.addWidget(spacer3)
        
        spacer4 = QWidget()
        spacer4.setFixedWidth(180)  # Start Emulation
        val_input_row.addWidget(spacer4)
        
        # Campo de entrada alinhado com Write I/O
        self.val_input = QLineEdit()
        self.val_input.setPlaceholderText("Enter ADDR/VAL in hex:")
        self.val_input.setFixedSize(160, 40)
        self.val_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #cccccc;
                border-radius: 20px;
                padding: 10px 15px;
                font-size: 13px;
                background-color: #f8f9fa;
                color: #666666;
            }
            QLineEdit:focus {
                border-color: #007bff;
                background-color: white;
                color: black;
            }
        """)
        self.val_input.setToolTip("Enter address and value to write in format: ADDR/VAL\nExample: 1000/FF (writes value FF to address 1000)\nBoth address and value should be in hexadecimal.")
        val_input_row.addWidget(self.val_input)
        
        layout.addLayout(val_input_row)
        
        layout.addStretch()
        return emulation_tab
    
    def create_debug_tab(self):
        """Criar aba de debug com design alinhado e moderno"""
        debug_tab = QWidget()
        layout = QVBoxLayout(debug_tab)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Primeira linha de botões - Step Into, Configure Debug, Verify Variable
        first_row = QHBoxLayout()
        
        # Step Into (esquerda)
        step_into_btn = QPushButton("🔍 Step Into")
        step_into_btn.setFixedSize(180, 40)
        step_into_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a1a1a;
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #333333;
            }
        """)
        step_into_btn.setToolTip("Execute a single instruction in the debugger.\nThis allows step-by-step debugging through the code execution.")
        step_into_btn.clicked.connect(self.on_step_into)
        first_row.addWidget(step_into_btn)
        
        # Spacer para centralizar
        spacer1 = QWidget()
        spacer1.setFixedWidth(80)
        first_row.addWidget(spacer1)
        
        # Configure Debug (centro)
        configure_debug_btn = QPushButton("⚙️ Configure Debug")
        configure_debug_btn.setFixedSize(180, 40)
        configure_debug_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a1a1a;
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #333333;
            }
        """)
        configure_debug_btn.setToolTip("Configure debugging mode settings.\nUse the numbered buttons (0, 1, 2) below for specific debug modes:\n• Mode 0: Basic debugging\n• Mode 1: Standard debugging\n• Mode 2: Comprehensive debugging")
        configure_debug_btn.clicked.connect(self.on_configure_debug)
        first_row.addWidget(configure_debug_btn)
        
        # Spacer para centralizar
        spacer2 = QWidget()
        spacer2.setFixedWidth(80)
        first_row.addWidget(spacer2)
        
        # Verify Variable (direita)
        verify_var_btn = QPushButton("🔍 Verify Variable")
        verify_var_btn.setFixedSize(180, 40)
        verify_var_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a1a1a;
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #333333;
            }
        """)
        verify_var_btn.setToolTip("Check the current value of a specific variable in the debugger.\nEnter the variable name in the input field below.")
        verify_var_btn.clicked.connect(self.on_verify_variable)
        first_row.addWidget(verify_var_btn)
        
        layout.addLayout(first_row)
        
        # Linha de inputs para Step Into, Configure Debug, Verify Variable
        inputs_row1 = QHBoxLayout()
        
        # Spacer vazio para Step Into (não precisa de input)
        empty_spacer1 = QWidget()
        empty_spacer1.setFixedWidth(180)
        inputs_row1.addWidget(empty_spacer1)
        
        # Spacer para manter espaçamento
        spacer_1 = QWidget()
        spacer_1.setFixedWidth(80)
        inputs_row1.addWidget(spacer_1)
        
        # Botões 0, 1, 2 para Configure Debug
        debug_buttons_layout = QHBoxLayout()
        debug_buttons_layout.setSpacing(10)
        
        # Botão 0
        self.debug_btn_0 = QPushButton("0")
        self.debug_btn_0.setFixedSize(50, 35)
        self.debug_btn_0.setCheckable(True)
        self.debug_btn_0.setToolTip("0 - No debug mode\nDisables debugging features for maximum performance.")
        self.debug_btn_0.clicked.connect(lambda: self.toggle_debug_button(0))
        self.update_debug_button_style(self.debug_btn_0, False)
        debug_buttons_layout.addWidget(self.debug_btn_0)
        
        # Botão 1
        self.debug_btn_1 = QPushButton("1")
        self.debug_btn_1.setFixedSize(50, 35)
        self.debug_btn_1.setCheckable(True)
        self.debug_btn_1.setToolTip("1 - Debug mode with discrete interface\nEnables debugging with discrete interface for controlled debugging operations.")
        self.debug_btn_1.clicked.connect(lambda: self.toggle_debug_button(1))
        self.update_debug_button_style(self.debug_btn_1, False)
        debug_buttons_layout.addWidget(self.debug_btn_1)
        
        # Botão 2
        self.debug_btn_2 = QPushButton("2")
        self.debug_btn_2.setFixedSize(50, 35)
        self.debug_btn_2.setCheckable(True)
        self.debug_btn_2.setToolTip("2 - Debug mode with implicit interface\nEnables debugging with implicit interface for advanced debugging operations.")
        self.debug_btn_2.clicked.connect(lambda: self.toggle_debug_button(2))
        self.update_debug_button_style(self.debug_btn_2, False)
        debug_buttons_layout.addWidget(self.debug_btn_2)
        
        # Widget container para os botões
        debug_buttons_widget = QWidget()
        debug_buttons_widget.setLayout(debug_buttons_layout)
        debug_buttons_widget.setFixedWidth(180)
        inputs_row1.addWidget(debug_buttons_widget)
        
        # Spacer para manter espaçamento
        spacer_2 = QWidget()
        spacer_2.setFixedWidth(80)
        inputs_row1.addWidget(spacer_2)
        
        # Input para Verify Variable
        self.var_input = QLineEdit()
        self.var_input.setPlaceholderText("Variable name:")
        self.var_input.setFixedSize(180, 30)
        self.var_input.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                border: 2px solid #ddd;
                border-radius: 15px;
                font-size: 11px;
            }
            QLineEdit:focus {
                border-color: #4CAF50;
            }
        """)
        self.var_input.setToolTip("Enter the name of the variable you want to inspect.\nExample: myVariable, counter, status_register")
        inputs_row1.addWidget(self.var_input)
        
        layout.addLayout(inputs_row1)
        
        # Segunda linha de botões - Delete Breakpoint, Continue, Command GDB
        second_row = QHBoxLayout()
        
        # Delete Breakpoint (esquerda)
        delete_bp_btn = QPushButton("🗑️ Delete Breakpoint")
        delete_bp_btn.setFixedSize(180, 40)
        delete_bp_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a1a1a;
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #333333;
            }
        """)
        delete_bp_btn.setToolTip("Remove a previously set breakpoint.\nEnter the breakpoint address in the input field below.")
        delete_bp_btn.clicked.connect(self.on_delete_breakpoint)
        second_row.addWidget(delete_bp_btn)
        
        # Spacer
        spacer3 = QWidget()
        spacer3.setFixedWidth(80)
        second_row.addWidget(spacer3)
        
        # Continue Emulation (centro)
        continue_btn = QPushButton("▶ Continue Emulation")
        continue_btn.setFixedSize(180, 40)
        continue_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a1a1a;
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #333333;
            }
        """)
        continue_btn.setToolTip("Resume execution after debugging operations.\nContinues running the emulation from the current state.")
        continue_btn.clicked.connect(self.on_continue_emulation)
        second_row.addWidget(continue_btn)
        
        # Spacer
        spacer4 = QWidget()
        spacer4.setFixedWidth(80)
        second_row.addWidget(spacer4)
        
        # Command GDB (direita)
        gdb_cmd_btn = QPushButton("💻 Command GDB")
        gdb_cmd_btn.setFixedSize(180, 40)
        gdb_cmd_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a1a1a;
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #333333;
            }
        """)
        gdb_cmd_btn.setToolTip("Execute a custom GDB command.\nEnter any valid GDB command in the input field below.\nExamples: info registers, print variable, backtrace")
        gdb_cmd_btn.clicked.connect(self.on_command_gdb)
        second_row.addWidget(gdb_cmd_btn)
        
        layout.addLayout(second_row)
        
        # Linha de inputs para Delete Breakpoint, Continue, Command GDB
        inputs_row2 = QHBoxLayout()
        
        # Input para Delete Breakpoint
        self.delete_bp_input = QLineEdit()
        self.delete_bp_input.setPlaceholderText("Line number:")
        self.delete_bp_input.setFixedSize(180, 30)
        self.delete_bp_input.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                border: 2px solid #ddd;
                border-radius: 15px;
                font-size: 11px;
            }
            QLineEdit:focus {
                border-color: #4CAF50;
            }
        """)
        self.delete_bp_input.setToolTip("Enter the line number or address of the breakpoint to delete.\nExample: 42, 0x1000, or memory address")
        inputs_row2.addWidget(self.delete_bp_input)
        
        # Spacer para manter espaçamento
        spacer_3 = QWidget()
        spacer_3.setFixedWidth(80)
        inputs_row2.addWidget(spacer_3)
        
        # Spacer vazio para Continue (não precisa de input)
        empty_spacer3 = QWidget()
        empty_spacer3.setFixedWidth(180)
        inputs_row2.addWidget(empty_spacer3)
        
        # Spacer para manter espaçamento
        spacer_4 = QWidget()
        spacer_4.setFixedWidth(80)
        inputs_row2.addWidget(spacer_4)
        
        # Input para Command GDB
        self.gdb_input = QLineEdit()
        self.gdb_input.setPlaceholderText("GDB command:")
        self.gdb_input.setFixedSize(180, 30)
        self.gdb_input.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                border: 2px solid #ddd;
                border-radius: 15px;
                font-size: 11px;
            }
            QLineEdit:focus {
                border-color: #4CAF50;
            }
        """)
        self.gdb_input.setToolTip("Enter a GDB command to execute.\nCommon commands:\n• info registers - Show CPU registers\n• print <variable> - Print variable value\n• backtrace - Show call stack\n• list - Show source code")
        inputs_row2.addWidget(self.gdb_input)
        
        layout.addLayout(inputs_row2)
        
        # Terceira linha de botões - Configure Breakpoint, Next Line, Finish Execution
        third_row = QHBoxLayout()
        
        # Configure Breakpoint (esquerda)
        config_bp_btn = QPushButton("📍 Configure Breakpoint")
        config_bp_btn.setFixedSize(180, 40)
        config_bp_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a1a1a;
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #333333;
            }
        """)
        config_bp_btn.setToolTip("Set a new breakpoint at a specific line or address.\nEnter the line number or memory address in the input field below.")
        config_bp_btn.clicked.connect(self.on_configure_breakpoint)
        third_row.addWidget(config_bp_btn)
        
        # Spacer
        spacer5 = QWidget()
        spacer5.setFixedWidth(80)
        third_row.addWidget(spacer5)
        
        # Next Line (centro)
        next_line_btn = QPushButton("⏭️ Next Line")
        next_line_btn.setFixedSize(180, 40)
        next_line_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a1a1a;
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #333333;
            }
        """)
        next_line_btn.setToolTip("Execute the next line of code without stepping into function calls.\nSimilar to 'step over' in traditional debuggers.")
        next_line_btn.clicked.connect(self.on_next_line)
        third_row.addWidget(next_line_btn)
        
        # Spacer
        spacer6 = QWidget()
        spacer6.setFixedWidth(80)
        third_row.addWidget(spacer6)
        
        # Finish Execution (direita)
        finish_exec_btn = QPushButton("🏁 Finish Execution")
        finish_exec_btn.setFixedSize(180, 40)
        finish_exec_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a1a1a;
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #333333;
            }
        """)
        finish_exec_btn.setToolTip("Execute until the current function returns.\nSimilar to 'step out' in traditional debuggers.")
        finish_exec_btn.clicked.connect(self.on_finish_execution)
        third_row.addWidget(finish_exec_btn)
        
        layout.addLayout(third_row)
        
        # Linha de inputs para Configure Breakpoint, Next Line, Finish Execution
        inputs_row3 = QHBoxLayout()
        
        # Input para Configure Breakpoint
        self.config_bp_input = QLineEdit()
        self.config_bp_input.setPlaceholderText("Line number:")
        self.config_bp_input.setFixedSize(180, 30)
        self.config_bp_input.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                border: 2px solid #ddd;
                border-radius: 15px;
                font-size: 11px;
            }
            QLineEdit:focus {
                border-color: #4CAF50;
            }
        """)
        self.config_bp_input.setToolTip("Enter the line number or memory address where you want to set a breakpoint.\nExample: 42, 0x1000, main+10")
        inputs_row3.addWidget(self.config_bp_input)
        
        # Spacer para manter espaçamento
        spacer_5 = QWidget()
        spacer_5.setFixedWidth(80)
        inputs_row3.addWidget(spacer_5)
        
        # Spacer vazio para Next Line (não precisa de input)
        empty_spacer4 = QWidget()
        empty_spacer4.setFixedWidth(180)
        inputs_row3.addWidget(empty_spacer4)
        
        # Spacer para manter espaçamento
        spacer_6 = QWidget()
        spacer_6.setFixedWidth(80)
        inputs_row3.addWidget(spacer_6)
        
        # Spacer vazio para Finish Execution (não precisa de input)
        empty_spacer5 = QWidget()
        empty_spacer5.setFixedWidth(180)
        inputs_row3.addWidget(empty_spacer5)
        
        layout.addLayout(inputs_row3)
        
        layout.addStretch()
        return debug_tab
    
    def create_control_settings_tab(self):
        """Criar aba de settings do control com design conforme imagem"""
        settings_tab = QWidget()
        layout = QVBoxLayout(settings_tab)
        layout.setSpacing(40)
        layout.setContentsMargins(50, 50, 50, 50)
        
        # Primeira linha - Verify State, Configure Debug, Inject AHBROM
        first_row = QHBoxLayout()
        first_row.setSpacing(80)
        
        # Verify State
        verify_state_btn = QPushButton("🛠️ Verify State")
        verify_state_btn.setFixedSize(160, 50)
        verify_state_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a1a1a;
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 13px;
                font-weight: bold;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #333333;
            }
        """)
        verify_state_btn.setToolTip("Check the current state of the virtual machine.\nReturns status information about the emulation environment.")
        verify_state_btn.clicked.connect(self.on_verify_state)
        first_row.addWidget(verify_state_btn)
        
        # Configure Debug
        configure_debug_btn = QPushButton("👤 Configure Debug")
        configure_debug_btn.setFixedSize(160, 50)
        configure_debug_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a1a1a;
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 13px;
                font-weight: bold;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #333333;
            }
        """)
        configure_debug_btn.setToolTip("Configure debugging mode for the emulation.\nUse the numbered buttons (0, 1, 2) below to select specific debug modes.")
        # Removido: configure_debug_btn.clicked.connect(self.on_configure_debug)
        # Agora use os botões numerados 0, 1, 2 para configurar debug com modo específico
        first_row.addWidget(configure_debug_btn)
        
        # Inject AHBROM
        inject_ahb_btn = QPushButton("📁 Inject AHBROM")
        inject_ahb_btn.setFixedSize(160, 50)
        inject_ahb_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a1a1a;
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 13px;
                font-weight: bold;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #333333;
            }
        """)
        inject_ahb_btn.setToolTip("Inject AHBROM (AHB ROM) data into the virtual machine.\nLoads ROM data into the AHB bus memory space for emulation.")
        inject_ahb_btn.clicked.connect(self.on_inject_ahbrom)
        first_row.addWidget(inject_ahb_btn)
        
        layout.addLayout(first_row)
        
        # Segunda linha - botões numerados 0, 1, 2
        second_row = QHBoxLayout()
        second_row.addStretch()
        
        # Botões numerados com comportamento de radio button
        self.settings_btn_0 = QPushButton("0")
        self.settings_btn_0.setFixedSize(60, 50)
        self.settings_btn_0.setCheckable(True)
        self.settings_btn_0.setToolTip("0 - No debug mode\nDisables debugging features for maximum performance.")
        self.settings_btn_0.clicked.connect(lambda: self.toggle_settings_button(0))
        self.update_settings_button_style(self.settings_btn_0, False)
        second_row.addWidget(self.settings_btn_0)
        
        second_row.addSpacing(30)
        
        self.settings_btn_1 = QPushButton("1")
        self.settings_btn_1.setFixedSize(60, 50)
        self.settings_btn_1.setCheckable(True)
        self.settings_btn_1.setToolTip("1 - Debug mode with discrete interface\nEnables debugging with discrete interface for controlled debugging operations.")
        self.settings_btn_1.clicked.connect(lambda: self.toggle_settings_button(1))
        self.update_settings_button_style(self.settings_btn_1, False)
        second_row.addWidget(self.settings_btn_1)
        
        second_row.addSpacing(30)
        
        self.settings_btn_2 = QPushButton("2")
        self.settings_btn_2.setFixedSize(60, 50)
        self.settings_btn_2.setCheckable(True)
        self.settings_btn_2.setToolTip("2 - Debug mode with implicit interface\nEnables debugging with implicit interface for advanced debugging operations.")
        self.settings_btn_2.clicked.connect(lambda: self.toggle_settings_button(2))
        self.update_settings_button_style(self.settings_btn_2, False)
        second_row.addWidget(self.settings_btn_2)
        
        second_row.addStretch()
        layout.addLayout(second_row)
        
        # Terceira linha - Inject Elf, Configure RAM, Configure OS ABI
        third_row = QHBoxLayout()
        third_row.setSpacing(80)
        
        # Inject Elf
        inject_elf_btn = QPushButton("📁 Inject Elf")
        inject_elf_btn.setFixedSize(160, 50)
        inject_elf_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a1a1a;
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 13px;
                font-weight: bold;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #333333;
            }
        """)
        inject_elf_btn.setToolTip("Inject an ELF (Executable and Linkable Format) file into the virtual machine.\nLoads executable code and data into the emulated system memory.")
        inject_elf_btn.clicked.connect(self.on_inject_elf)
        third_row.addWidget(inject_elf_btn)
        
        # Configure RAM
        config_ram_btn = QPushButton("⚙️ Configure RAM")
        config_ram_btn.setFixedSize(160, 50)
        config_ram_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a1a1a;
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 13px;
                font-weight: bold;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #333333;
            }
        """)
        config_ram_btn.setToolTip("Configure RAM (Random Access Memory) settings for the virtual machine.\nSet memory size, allocation parameters, and memory layout options.\nEnter RAM value in the field below.")
        config_ram_btn.clicked.connect(self.on_configure_ram)
        third_row.addWidget(config_ram_btn)
        
        # Configure OS ABI
        config_abi_btn = QPushButton("📁 Configure OS ABI")
        config_abi_btn.setFixedSize(160, 50)
        config_abi_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a1a1a;
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 13px;
                font-weight: bold;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #333333;
            }
        """)
        config_abi_btn.setToolTip("Configure OS ABI (Operating System Application Binary Interface).\nSet system call interfaces, calling conventions, and OS-specific parameters for the emulated environment.")
        config_abi_btn.clicked.connect(self.on_configure_os_abi)
        third_row.addWidget(config_abi_btn)
        
        layout.addLayout(third_row)
        
        # Campo de entrada RAM centralizado
        ram_input_row = QHBoxLayout()
        ram_input_row.addStretch()
        
        self.ram_value_input = QLineEdit()
        self.ram_value_input.setPlaceholderText("Enter RAM value")
        self.ram_value_input.setFixedSize(200, 40)
        self.ram_value_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #cccccc;
                border-radius: 20px;
                padding: 10px 15px;
                font-size: 13px;
                background-color: #f8f9fa;
                color: #666666;
            }
            QLineEdit:focus {
                border-color: #007bff;
                background-color: white;
                color: black;
            }
        """)
        self.ram_value_input.setToolTip("Enter RAM configuration value.\nSupported formats: Size in MB (e.g., 512, 1024) or hexadecimal values.\nUsed with 'Configure RAM' button above.")
        ram_input_row.addWidget(self.ram_value_input)
        ram_input_row.addStretch()
        
        layout.addLayout(ram_input_row)
        
        layout.addStretch()
        return settings_tab
    
    def create_control_logs(self):
        """Criar área de logs do Control"""
        logs_frame = QFrame()
        layout = QVBoxLayout(logs_frame)
        
        # Header com título e botão clear
        header_layout = QHBoxLayout()
        
        # Título
        title = QLabel("Systems Logs:")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Botão Clear Logs
        clear_logs_btn = QPushButton("🗑️ Clear Logs")
        clear_logs_btn.setFixedSize(120, 35)
        clear_logs_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 17px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:pressed {
                background-color: #a71e2a;
            }
        """)
        clear_logs_btn.clicked.connect(self.clear_control_logs)
        header_layout.addWidget(clear_logs_btn)
        
        layout.addLayout(header_layout)
        
        # Área de logs
        self.control_logs_text = QTextEdit()
        self.control_logs_text.setMinimumHeight(200)
        self.control_logs_text.setReadOnly(True)
        self.control_logs_text.setStyleSheet("""
            QTextEdit {
                background-color: #e5e5e5;
                border: 1px solid #cccccc;
                border-radius: 8px;
                padding: 10px;
                font-family: monospace;
                font-size: 10px;
            }
        """)
        self.control_logs_text.setPlaceholderText("System logs will appear here...")
        layout.addWidget(self.control_logs_text)
        
        # Log inicial
        if self.protocol:
            self.log_control_message("QEMULA APP started - Backend connected")
            if self.protocol.is_connected():
                self.log_control_message("Backend connected successfully!")
            else:
                self.log_control_message("Backend waiting for server connection...")
        else:
            self.log_control_message("Backend not available")
        
        return logs_frame
    
    def log_control_message(self, message):
        """Adiciona mensagem aos logs do control"""
        if hasattr(self, 'control_logs_text') and self.control_logs_text:
            import datetime
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            self.control_logs_text.append(f"[{timestamp}] {message}")
    
    def clear_control_logs(self):
        """Limpa todos os logs do control"""
        if hasattr(self, 'control_logs_text') and self.control_logs_text:
            self.control_logs_text.clear()
            self.log_control_message("Logs cleared by user")
    
    def show_control_message(self, title, message):
        """Mostra uma mensagem para o usuário"""
        from PySide6.QtWidgets import QMessageBox
        msg_box = QMessageBox()
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec()
    
    def handle_protocol_response(self, response, action_name):
        """Processa a resposta do protocolo e mostra ao usuário"""
        # Verificar se a resposta é válida
        if response is None:
            self.log_control_message(f"{action_name} executed - No response from server (normal for background operations)")
            return
        
        # Verificar se response é um dicionário
        if not isinstance(response, dict):
            self.log_control_message(f"{action_name} executed: {response}")
            return
        
        # Tratar respostas com erro
        if "error" in response and response["error"]:
            error_msg = response["error"]
            
            # Para start emulation, timeouts e respostas vazias são normais
            if action_name == "Start Emulation":
                if any(keyword in error_msg.lower() for keyword in ["timeout", "empty response", "waiting for server response"]):
                    self.log_control_message(f"{action_name} command sent - server response timeout (this is normal for emulation start)")
                    return
            
            # Outros erros são reportados normalmente
            self.log_control_message(f"Error in {action_name}: {error_msg}")
            self.show_control_message("Error", f"Error executing {action_name}:\n{error_msg}")
        else:
            # Resposta bem-sucedida
            return_value = response.get('return', 'Success')
            if return_value and return_value != '-':
                self.log_control_message(f"{action_name} executed: {return_value}")
            else:
                self.log_control_message(f"{action_name} executed successfully")
            
            # Mostrar dados retornados se houver
            if response.get('body') and response['body'] != '-':
                self.log_control_message(f"Returned data: {response['body']}")
    
    # Métodos de comando do protocolo
    def on_verify_state(self):
        """Verifica o estado da máquina"""
        if not self.protocol:
            self.show_control_message("Error", "Backend not available")
            return
        
        self.log_control_message("Checking machine state...")
        response = self.protocol.send_verify_state()
        self.handle_protocol_response(response, "Verify State")
        if response.get('machine_state'):
            self.log_control_message(f"Machine state: {response['machine_state']}")
    
    def on_start_emulation(self):
        """Inicia a emulação em uma thread separada"""
        if not self.protocol:
            self.show_control_message("Error", "Backend not available")
            return
        
        # Verificar se já existe uma thread rodando
        if self.emulation_worker and self.emulation_worker.isRunning():
            self.log_control_message("Emulation command already running in background...")
            return
        
        self.log_control_message("Starting emulation in background thread...")
        self.log_control_message("Note: Start emulation may take time and server timeouts are normal")
        
        # Criar e configurar worker thread
        self.emulation_worker = EmulationWorkerThread(self.protocol, "start_emulation")
        
        # Conectar sinais
        self.emulation_worker.finished.connect(self.on_emulation_finished)
        self.emulation_worker.error.connect(self.on_emulation_error)
        self.emulation_worker.log_message.connect(self.log_control_message)
        
        # Iniciar thread
        self.emulation_worker.start()
    
    def on_emulation_finished(self, response):
        """Callback quando a operação de emulação termina com sucesso"""
        self.handle_protocol_response(response, "Start Emulation")
        
        # Verificar se é uma resposta de inicialização ou processamento
        if isinstance(response, dict):
            status = response.get('status')
            if status == 'initializing':
                self.log_control_message("Emulation is starting - this may take a few moments...")
            elif status == 'processing':
                self.log_control_message("Emulation command sent - server is processing (this is normal)")
            elif status == 'sent':
                self.log_control_message("Emulation command sent successfully")
            else:
                self.log_control_message("Emulation command completed in background thread")
        else:
            self.log_control_message("Emulation command completed in background thread")
    
    def on_emulation_error(self, error_message):
        """Callback quando há erro na operação de emulação"""
        self.log_control_message(f"Emulation thread error: {error_message}")
        self.show_control_message("Error", f"Error in emulation thread:\n{error_message}")
    
    def on_pause_emulation(self):
        """Pausa a emulação em uma thread separada"""
        if not self.protocol:
            self.show_control_message("Error", "Backend not available")
            return
        
        # Verificar se já existe uma thread rodando
        if self.emulation_worker and self.emulation_worker.isRunning():
            self.log_control_message("Emulation command already running in background...")
            return
        
        self.log_control_message("Pausing emulation in background thread...")
        
        # Criar e configurar worker thread
        self.emulation_worker = EmulationWorkerThread(self.protocol, "pause_emulation")
        
        # Conectar sinais
        self.emulation_worker.finished.connect(lambda response: self.handle_protocol_response(response, "Pause Emulation"))
        self.emulation_worker.error.connect(self.on_emulation_error)
        self.emulation_worker.log_message.connect(self.log_control_message)
        
        # Iniciar thread
        self.emulation_worker.start()
    
    def on_stop_emulation(self):
        """Para a emulação em uma thread separada"""
        if not self.protocol:
            self.show_control_message("Error", "Backend not available")
            return
        
        # Verificar se já existe uma thread rodando
        if self.emulation_worker and self.emulation_worker.isRunning():
            self.log_control_message("Emulation command already running in background...")
            return
        
        self.log_control_message("Stopping emulation in background thread...")
        
        # Criar e configurar worker thread
        self.emulation_worker = EmulationWorkerThread(self.protocol, "stop_emulation")
        
        # Conectar sinais
        self.emulation_worker.finished.connect(lambda response: self.handle_protocol_response(response, "Stop Emulation"))
        self.emulation_worker.error.connect(self.on_emulation_error)
        self.emulation_worker.log_message.connect(self.log_control_message)
        
        # Iniciar thread
        self.emulation_worker.start()
    
    def on_unpause_emulation(self):
        """Despausa a emulação em uma thread separada"""
        if not self.protocol:
            self.show_control_message("Error", "Backend not available")
            return
        
        # Verificar se já existe uma thread rodando
        if self.emulation_worker and self.emulation_worker.isRunning():
            self.log_control_message("Emulation command already running in background...")
            return
        
        self.log_control_message("Unpausing emulation in background thread...")
        
        # Criar e configurar worker thread
        self.emulation_worker = EmulationWorkerThread(self.protocol, "unpause_emulation")
        
        # Conectar sinais
        self.emulation_worker.finished.connect(lambda response: self.handle_protocol_response(response, "Unpause Emulation"))
        self.emulation_worker.error.connect(self.on_emulation_error)
        self.emulation_worker.log_message.connect(self.log_control_message)
        
        # Iniciar thread
        self.emulation_worker.start()
    
    def on_read_io(self):
        """Lê I/O do endereço especificado"""
        if not self.protocol:
            self.show_control_message("Error", "Backend not available")
            return
            
        addr_input = getattr(self, 'addr_input', None)
        if not addr_input or not addr_input.text().strip():
            self.show_control_message("Error", "Please enter a valid address for reading.")
            return
        
        try:
            addr_text = addr_input.text().strip()
            if addr_text.lower().startswith('0x'):
                addr = int(addr_text, 16)
            else:
                addr = int(addr_text, 16)
            
            self.log_control_message(f"Reading I/O from address 0x{addr:08X}...")
            response = self.protocol.send_read_io(addr)
            self.handle_protocol_response(response, "Read I/O")
        except ValueError:
            self.show_control_message("Error", "Invalid address. Use hexadecimal format (e.g.: 0x1000 or 1000).")
        except Exception as e:
            self.log_control_message(f"Error reading I/O: {str(e)}")
    
    def on_write_io(self):
        """Escreve I/O no endereço especificado"""
        if not self.protocol:
            self.show_control_message("Error", "Backend not available")
            return
            
        val_input = getattr(self, 'val_input', None)
        if not val_input or not val_input.text().strip():
            self.show_control_message("Error", "Please enter address and value for writing (format: ADDR/VAL).")
            return
        
        try:
            value_text = val_input.text().strip()
            if '/' not in value_text:
                self.show_control_message("Error", "Invalid format. Use ADDR/VAL in hexadecimal (e.g.: 1000/FF).")
                return
            
            addr_str, val_str = value_text.split('/', 1)
            addr = int(addr_str.strip(), 16)
            value = int(val_str.strip(), 16)
            
            self.log_control_message(f"Writing value 0x{value:02X} to address 0x{addr:08X}...")
            response = self.protocol.send_write_io(addr, value)
            self.handle_protocol_response(response, "Write I/O")
        except ValueError:
            self.show_control_message("Error", "Invalid format. Use ADDR/VAL in hexadecimal (e.g.: 1000/FF).")
        except Exception as e:
            self.log_control_message(f"Error writing I/O: {str(e)}")
    
    # Métodos para botões de debug
    def on_step_into(self):
        """Executa step into"""
        if not self.protocol:
            self.show_control_message("Error", "Backend not available")
            return
        
        self.log_control_message("Executing step into...")
        response = self.protocol.send_step_into()
        self.handle_protocol_response(response, "Step Into")
    
    def on_configure_debug(self):
        """Configura o debug (modo 1 por padrão)"""
        if not self.protocol:
            self.show_control_message("Error", "Backend not available")
            return
        
        print("DEBUG: 'Configure Debug' button clicked - sending mode 1")  # Debug print
        self.log_control_message("Configuring debug...")
        response = self.protocol.send_config_debug(1)  # Modo 1 por padrão
        self.handle_protocol_response(response, "Configure Debug")
    
    def on_configure_debug_mode(self, mode):
        """Configura o debug com modo específico (0, 1 ou 2)"""
        if not self.protocol:
            self.show_control_message("Error", "Backend not available")
            return
        
        print(f"DEBUG: Enviando modo {mode} para configure_debug")  # Debug print
        self.log_control_message(f"Configuring debug mode {mode}...")
        response = self.protocol.send_config_debug(mode)
        self.handle_protocol_response(response, f"Configure Debug Mode {mode}")
    
    def toggle_debug_button(self, button_index):
        """Toggle do estado do botão de debug (0, 1 ou 2) - comportamento de radio button"""
        print(f"DEBUG: Button {button_index} clicked")  # Debug print
        
        # Se o botão já está selecionado, desselecionar
        if self.debug_button_states[button_index]:
            print(f"DEBUG: Deselecting button {button_index}")  # Debug print
            self.debug_button_states[button_index] = False
            button = getattr(self, f'debug_btn_{button_index}')
            self.update_debug_button_style(button, False)
        else:
            print(f"DEBUG: Selecting button {button_index}")  # Debug print
            # Desselecionar todos os outros botões primeiro
            for i in range(3):
                if i != button_index and self.debug_button_states[i]:
                    self.debug_button_states[i] = False
                    other_button = getattr(self, f'debug_btn_{i}')
                    self.update_debug_button_style(other_button, False)
            
            # Selecionar o botão atual
            self.debug_button_states[button_index] = True
            button = getattr(self, f'debug_btn_{button_index}')
            self.update_debug_button_style(button, True)
            
            # Executar a ação de debug para o botão selecionado
            # button_index 0 -> mode 0, button_index 1 -> mode 1, button_index 2 -> mode 2
            print(f"DEBUG: Chamando on_configure_debug_mode({button_index})")  # Debug print
            self.on_configure_debug_mode(button_index)
    
    def update_debug_button_style(self, button, is_selected):
        """Atualiza o estilo visual do botão debug baseado no estado de seleção"""
        if is_selected:
            # Estilo quando selecionado (azul)
            button.setStyleSheet("""
                QPushButton {
                    background-color: #007bff;
                    color: white;
                    border: none;
                    border-radius: 25px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #0056b3;
                }
            """)
        else:
            # Estilo quando não selecionado (escuro)
            button.setStyleSheet("""
                QPushButton {
                    background-color: #1a1a1a;
                    color: white;
                    border: none;
                    border-radius: 25px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #333333;
                }
            """)
    
    def toggle_settings_button(self, button_index):
        """Toggle do estado do botão de settings (0, 1 ou 2) - comportamento de radio button"""
        # Se o botão já está selecionado, desselecionar
        if self.settings_button_states[button_index]:
            self.settings_button_states[button_index] = False
            button = getattr(self, f'settings_btn_{button_index}')
            self.update_settings_button_style(button, False)
        else:
            # Desselecionar todos os outros botões primeiro
            for i in range(3):
                if i != button_index and self.settings_button_states[i]:
                    self.settings_button_states[i] = False
                    other_button = getattr(self, f'settings_btn_{i}')
                    self.update_settings_button_style(other_button, False)
            
            # Selecionar o botão atual
            self.settings_button_states[button_index] = True
            button = getattr(self, f'settings_btn_{button_index}')
            self.update_settings_button_style(button, True)
            
            # Executar a ação para o botão selecionado (pode ser customizada)
            self.on_settings_button_action(button_index)
    
    def update_settings_button_style(self, button, is_selected):
        """Atualiza o estilo visual do botão settings baseado no estado de seleção"""
        if is_selected:
            # Estilo quando selecionado (azul)
            button.setStyleSheet("""
                QPushButton {
                    background-color: #007bff;
                    color: white;
                    border: none;
                    border-radius: 25px;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #0056b3;
                }
            """)
        else:
            # Estilo quando não selecionado (escuro)
            button.setStyleSheet("""
                QPushButton {
                    background-color: #1a1a1a;
                    color: white;
                    border: none;
                    border-radius: 25px;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #333333;
                }
            """)
    
    def on_settings_button_action(self, button_number):
        """Ação executada quando um botão de settings é selecionado"""
        print(f"DEBUG: Settings button {button_number} selected")  # Debug print
        # Usar o mesmo método que os botões de debug para enviar o modo correto
        print(f"DEBUG: Calling on_configure_debug_mode({button_number}) from Settings tab")  # Debug print
        self.on_configure_debug_mode(button_number)
        
        if hasattr(self, 'log_control_message'):
            self.log_control_message(f"Configuração modo {button_number} ativada")
    
    def on_verify_variable(self):
        """Verifica uma variável"""
        if not self.protocol:
            self.show_control_message("Error", "Backend not available")
            return
            
        var_input = getattr(self, 'var_input', None)
        if not var_input or not var_input.text().strip():
            self.show_control_message("Error", "Please enter the variable name.")
            return
        
        var_name = var_input.text().strip()
        self.log_control_message(f"Checking variable: {var_name}...")
        response = self.protocol.send_verify_variable(var_name)
        self.handle_protocol_response(response, "Verify Variable")
    
    def on_delete_breakpoint(self):
        """Deleta um breakpoint"""
        if not self.protocol:
            self.show_control_message("Error", "Backend not available")
            return
            
        delete_bp_input = getattr(self, 'delete_bp_input', None)
        if not delete_bp_input or not delete_bp_input.text().strip():
            self.show_control_message("Error", "Please enter the breakpoint line number.")
            return
        
        try:
            line = int(delete_bp_input.text().strip())
            self.log_control_message(f"Deleting breakpoint at line {line}...")
            response = self.protocol.send_delete_breakpoint(line)
            self.handle_protocol_response(response, "Delete Breakpoint")
        except ValueError:
            self.show_control_message("Error", "Invalid line number.")
        except Exception as e:
            self.log_control_message(f"Error deleting breakpoint: {str(e)}")
    
    def on_configure_breakpoint(self):
        """Configura um breakpoint"""
        if not self.protocol:
            self.show_control_message("Error", "Backend not available")
            return
            
        config_bp_input = getattr(self, 'config_bp_input', None)
        if not config_bp_input or not config_bp_input.text().strip():
            self.show_control_message("Error", "Please enter the breakpoint line number.")
            return
        
        try:
            line = int(config_bp_input.text().strip())
            self.log_control_message(f"Configuring breakpoint at line {line}...")
            response = self.protocol.send_config_breakpoint(line)
            self.handle_protocol_response(response, "Configure Breakpoint")
        except ValueError:
            self.show_control_message("Error", "Invalid line number.")
        except Exception as e:
            self.log_control_message(f"Error configuring breakpoint: {str(e)}")
    
    def on_continue_emulation(self):
        """Continua a emulação"""
        if not self.protocol:
            self.show_control_message("Error", "Backend not available")
            return
        
        self.log_control_message("Continuing emulation...")
        response = self.protocol.send_continue_emulation()
        self.handle_protocol_response(response, "Continue Emulation")
    
    def on_next_line(self):
        """Executa próxima linha"""
        if not self.protocol:
            self.show_control_message("Error", "Backend not available")
            return
        
        self.log_control_message("Executing next line...")
        response = self.protocol.send_next_line()
        self.handle_protocol_response(response, "Next Line")
    
    def on_finish_execution(self):
        """Finaliza execução"""
        if not self.protocol:
            self.show_control_message("Error", "Backend not available")
            return
        
        self.log_control_message("Finishing execution...")
        response = self.protocol.send_finish_execution()
        self.handle_protocol_response(response, "Finish Execution")
    
    def on_command_gdb(self):
        """Envia comando GDB"""
        if not self.protocol:
            self.show_control_message("Error", "Backend not available")
            return
            
        gdb_input = getattr(self, 'gdb_input', None)
        if not gdb_input or not gdb_input.text().strip():
            self.show_control_message("Error", "Please enter a GDB command.")
            return
        
        command = gdb_input.text().strip()
        self.log_control_message(f"Sending GDB command: {command}...")
        response = self.protocol.send_gdb_command(command)
        self.handle_protocol_response(response, "GDB Command")
    
    def on_inject_elf(self):
        """Injeta arquivo ELF"""
        if not self.protocol:
            self.show_control_message("Error", "Backend not available")
            return
        
        from PySide6.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getOpenFileName(self, "Select ELF file", "", "All files (*.*)")
        if file_path:
            try:
                with open(file_path, 'rb') as f:
                    elf_data = f.read()
                
                self.log_control_message(f"Injecting ELF file: {file_path}...")
                response = self.protocol.send_inject_elf(elf_data)
                self.handle_protocol_response(response, "Inject ELF")
            except Exception as e:
                self.show_control_message("Error", f"Error reading ELF file: {str(e)}")
    
    def on_inject_ahbrom(self):
        """Injeta arquivo AHBROM"""
        if not self.protocol:
            self.show_control_message("Error", "Backend not available")
            return
        
        from PySide6.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getOpenFileName(self, "Select AHBROM file", "", "ROM files (*.rom *.bin);;All files (*.*)")
        if file_path:
            try:
                with open(file_path, 'rb') as f:
                    ahb_data = f.read()
                
                self.log_control_message(f"Injecting AHBROM file: {file_path}...")
                response = self.protocol.send_inject_ahbrom(ahb_data)
                self.handle_protocol_response(response, "Inject AHBROM")
            except Exception as e:
                self.show_control_message("Error", f"Error reading AHBROM file: {str(e)}")
    
    def on_configure_ram(self):
        """Configura RAM"""
        if not self.protocol:
            self.show_control_message("Error", "Backend not available")
            return
            
        ram_value_input = getattr(self, 'ram_value_input', None)
        if not ram_value_input or not ram_value_input.text().strip():
            self.show_control_message("Error", "Please enter the RAM size in bytes.")
            return
        
        try:
            ram_size = int(ram_value_input.text().strip())
            if ram_size <= 0:
                self.show_control_message("Error", "RAM size must be greater than zero.")
                return
            
            self.log_control_message(f"Configuring RAM: {ram_size} bytes...")
            response = self.protocol.send_config_ram(ram_size)
            self.handle_protocol_response(response, "Configure RAM")
        except ValueError:
            self.show_control_message("Error", "Invalid RAM size. Use numbers only.")
        except Exception as e:
            self.log_control_message(f"Error configuring RAM: {str(e)}")
    
    def on_configure_os_abi(self):
        """Configura OS ABI (linux por padrão)"""
        if not self.protocol:
            self.show_control_message("Error", "Backend not available")
            return
        
        self.log_control_message("Configuring OS ABI to linux...")
        response = self.protocol.send_set_os_abi("linux")
        self.handle_protocol_response(response, "Configure OS ABI")

    # Métodos para SPW Tab
    def create_spw_header(self):
        """Criar header da aba SPW"""
        header = QFrame()
        layout = QHBoxLayout(header)
        
        # Título da interface
        title = QLabel("Transceiver SPW Interface")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Status QEMULA run
        status_label = QLabel("QEMULA run")
        status_label.setFont(QFont("Arial", 12))
        layout.addWidget(status_label)
        
        # Pause icon
        pause_icon = QLabel("⏸️")
        pause_icon.setFont(QFont("Arial", 16))
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
                pixmap = pixmap.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                btn.setIcon(QIcon(pixmap))
                btn.setIconSize(QSize(48, 48))
            except:
                btn.setText("🔗")
                btn.setFont(QFont("Arial", 24))
            btn.setFixedSize(52, 52)
            btn.clicked.connect(lambda checked, link=url: QDesktopServices.openUrl(QUrl(link)))
            icons_layout.addWidget(btn)
        layout.addLayout(icons_layout)
        
        return header
    
    def create_spw_top_section(self):
        """Criar seção superior da tab SPW"""
        # Layout horizontal para Received Data e Start Connection
        top_layout = QHBoxLayout()
        
        # Seção Received Data
        received_frame = QFrame()
        received_frame.setFrameStyle(QFrame.Box)
        received_layout = QVBoxLayout(received_frame)
        received_layout.setContentsMargins(20, 20, 20, 20)
        received_layout.setSpacing(15)
        
        # Título Received Data
        received_title = QLabel("Received Data")
        received_title.setFont(QFont("Arial", 14, QFont.Bold))
        received_layout.addWidget(received_title)
        
        # Área de dados recebidos
        self.spw_received_text = QTextEdit()
        self.spw_received_text.setReadOnly(True)
        self.spw_received_text.setMinimumHeight(200)
        self.spw_received_text.setStyleSheet("""
            QTextEdit {
                background-color: #e5e5e5;
                border: 1px solid #cccccc;
                border-radius: 8px;
                padding: 10px;
                font-family: monospace;
                font-size: 11px;
            }
        """)
        self.spw_received_text.setPlaceholderText("Received data will appear here...")
        received_layout.addWidget(self.spw_received_text)
        
        top_layout.addWidget(received_frame, 2)  # Ocupar 2/3 do espaço
        
        # Seção Start Connection
        connection_frame = QFrame()
        connection_frame.setFrameStyle(QFrame.Box)
        connection_layout = QVBoxLayout(connection_frame)
        connection_layout.setContentsMargins(20, 20, 20, 20)
        connection_layout.setSpacing(15)
        
        # Título Start Connection
        connection_title = QLabel("SPW Connection")
        connection_title.setFont(QFont("Arial", 14, QFont.Bold))
        connection_layout.addWidget(connection_title)
        
        # Campos de configuração
        # Host
        host_layout = QHBoxLayout()
        host_label = QLabel("Host:")
        host_label.setFont(QFont("Arial", 10))
        host_label.setFixedWidth(40)
        self.spw_host_input = QLineEdit()
        self.spw_host_input.setText("localhost")
        self.spw_host_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 5px;
                font-size: 10px;
            }
        """)
        host_layout.addWidget(host_label)
        host_layout.addWidget(self.spw_host_input)
        connection_layout.addLayout(host_layout)
        
        # Port
        port_layout = QHBoxLayout()
        port_label = QLabel("Port:")
        port_label.setFont(QFont("Arial", 10))
        port_label.setFixedWidth(40)
        self.spw_port_input = QLineEdit()
        self.spw_port_input.setText("5054")
        self.spw_port_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 5px;
                font-size: 10px;
            }
        """)
        port_layout.addWidget(port_label)
        port_layout.addWidget(self.spw_port_input)
        connection_layout.addLayout(port_layout)
        
        # Status da conexão
        self.spw_connection_status = QLabel("Disconnected")
        self.spw_connection_status.setFont(QFont("Arial", 10, QFont.Bold))
        self.spw_connection_status.setStyleSheet("color: red;")
        self.spw_connection_status.setAlignment(Qt.AlignCenter)
        connection_layout.addWidget(self.spw_connection_status)
        
        # Switch para Start Connection
        switch_layout = QHBoxLayout()
        switch_label = QLabel("Connect:")
        switch_label.setFont(QFont("Arial", 10))
        self.spw_connection_switch = ToggleSwitch()
        self.spw_connection_switch.toggled.connect(self.on_spw_connection_toggle)
        switch_layout.addWidget(switch_label)
        switch_layout.addStretch()
        switch_layout.addWidget(self.spw_connection_switch)
        connection_layout.addLayout(switch_layout)
        
        connection_layout.addStretch()
        
        top_layout.addWidget(connection_frame, 1)  # Ocupar 1/3 do espaço
        
        # Widget container para o layout
        top_widget = QWidget()
        top_widget.setLayout(top_layout)
        
        return top_widget
    
    def create_spw_bottom_section(self):
        """Criar seção inferior da tab SPW"""
        # Layout horizontal para Data Transmit e botões
        bottom_layout = QHBoxLayout()
        
        # Seção Data Transmit
        transmit_frame = QFrame()
        transmit_frame.setFrameStyle(QFrame.Box)
        transmit_layout = QVBoxLayout(transmit_frame)
        transmit_layout.setContentsMargins(20, 20, 20, 20)
        transmit_layout.setSpacing(15)
        
        # Título Data Transmit
        transmit_title = QLabel("Data Transmit")
        transmit_title.setFont(QFont("Arial", 14, QFont.Bold))
        transmit_layout.addWidget(transmit_title)
        
        # Área de dados para transmitir
        self.spw_transmit_text = QTextEdit()
        self.spw_transmit_text.setMinimumHeight(200)
        self.spw_transmit_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #cccccc;
                border-radius: 8px;
                padding: 10px;
                font-family: monospace;
                font-size: 11px;
            }
        """)
        self.spw_transmit_text.setPlaceholderText("Enter data to transmit...")
        transmit_layout.addWidget(self.spw_transmit_text)
        
        bottom_layout.addWidget(transmit_frame, 2)  # Ocupar 2/3 do espaço
        
        # Seção de botões
        buttons_frame = QFrame()
        buttons_frame.setFrameStyle(QFrame.Box)
        buttons_layout = QVBoxLayout(buttons_frame)
        buttons_layout.setContentsMargins(20, 20, 20, 20)
        buttons_layout.setSpacing(15)
        
        # Criar botões com ícones
        button_configs = [
            ("Transmit", "▶", self.on_spw_transmit_clicked),
            ("Clear Receiver", "×", self.on_spw_clear_receiver_clicked),
            ("Clear Transmit", "×", self.on_spw_clear_transmit_clicked),
            ("Save Logs", "💾", self.on_spw_save_logs_clicked)
        ]
        
        for button_text, icon_text, callback in button_configs:
            btn = QPushButton(button_text)
            btn.setFixedSize(160, 40)
            
            # Criar ícone
            if icon_text == "💾":
                icon = self.create_text_icon("S", 16, Qt.white)  # S para Save
            else:
                icon = self.create_text_icon(icon_text, 16, Qt.white)
            
            btn.setIcon(icon)
            btn.setIconSize(QSize(16, 16))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #333333;
                    color: white;
                    border: none;
                    border-radius: 20px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #555555;
                }
            """)
            btn.clicked.connect(callback)
            
            # Centralizar o botão
            btn_layout = QHBoxLayout()
            btn_layout.addStretch()
            btn_layout.addWidget(btn)
            btn_layout.addStretch()
            
            buttons_layout.addLayout(btn_layout)
        
        buttons_layout.addStretch()
        
        bottom_layout.addWidget(buttons_frame, 1)  # Ocupar 1/3 do espaço
        
        # Widget container para o layout
        bottom_widget = QWidget()
        bottom_widget.setLayout(bottom_layout)
        
        return bottom_widget

    def create_text_icon(self, text, size, color=Qt.white):
        """Cria um ícone a partir de texto"""
        from PySide6.QtGui import QPixmap, QPainter, QFont, QPen
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setFont(QFont("Arial", size-2, QFont.Bold))
        pen = QPen(color)
        pen.setWidth(0)  # Remove qualquer borda
        painter.setPen(pen)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.drawText(pixmap.rect(), Qt.AlignCenter, text)
        painter.end()
        
        return QIcon(pixmap)

    # Callbacks para SPW
    def on_spw_connection_toggle(self, checked):
        """Callback para quando o switch de conexão SPW é alterado"""
        if checked:
            # Conectar ao backend SPW
            try:
                # Obter configurações dos campos de entrada
                host = self.spw_host_input.text().strip() or "localhost"
                port_text = self.spw_port_input.text().strip() or "8888"
                
                try:
                    port = int(port_text)
                except ValueError:
                    self.spw_received_text.append("[ERROR] Invalid port number")
                    self.spw_connection_switch.setChecked(False)
                    return
                
                # Atualizar status
                self.spw_connection_status.setText("Connecting...")
                self.spw_connection_status.setStyleSheet("color: orange;")
                
                # Importar e inicializar o receiver
                from backend.reciever import SpaceWireReceiver
                self.spw_receiver = SpaceWireReceiver(host, port)
                self.spw_receiver.message_received.connect(self.on_spw_message_received)
                self.spw_receiver.start()
                
                self.spw_is_connected = True
                print(f"SPW Connection started - connecting to {host}:{port}")
                self.spw_received_text.append(f"[INFO] Connecting to {host}:{port}...")
                
                # Simulação de conexão bem-sucedida após um pequeno delay
                from PySide6.QtCore import QTimer
                self.spw_connection_timer = QTimer()
                self.spw_connection_timer.timeout.connect(self.check_spw_connection_status)
                self.spw_connection_timer.setSingleShot(True)
                self.spw_connection_timer.start(2000)  # 2 segundos
                
            except Exception as e:
                print(f"Error starting SPW connection: {e}")
                self.spw_received_text.append(f"[ERROR] Failed to start connection: {e}")
                self.spw_connection_switch.setChecked(False)
                self.spw_connection_status.setText("Disconnected")
                self.spw_connection_status.setStyleSheet("color: red;")
                self.spw_is_connected = False
        else:
            # Desconectar do backend SPW
            if hasattr(self, 'spw_receiver') and self.spw_receiver:
                self.spw_receiver.stop()
                self.spw_receiver = None
            
            self.spw_is_connected = False
            self.spw_connection_status.setText("Disconnected")
            self.spw_connection_status.setStyleSheet("color: red;")
            print("SPW Connection stopped")
            self.spw_received_text.append("[INFO] Connection stopped")
    
    def check_spw_connection_status(self):
        """Verifica e atualiza o status da conexão SPW"""
        if hasattr(self, 'spw_is_connected') and self.spw_is_connected and hasattr(self, 'spw_receiver') and self.spw_receiver:
            # Em uma implementação real, você verificaria se a conexão está ativa
            # Por agora, vamos simular uma conexão bem-sucedida
            self.spw_connection_status.setText("Connected")
            self.spw_connection_status.setStyleSheet("color: green;")
            self.spw_received_text.append("[INFO] Connection established successfully!")
        else:
            self.spw_connection_status.setText("Failed")
            self.spw_connection_status.setStyleSheet("color: red;")
    
    def on_spw_message_received(self, message):
        """Callback para quando uma mensagem é recebida do backend SPW"""
        if hasattr(self, 'spw_received_text'):
            self.spw_received_text.append(message)

    def on_spw_transmit_clicked(self):
        """Callback para o botão Transmit SPW"""
        if not hasattr(self, 'spw_transmit_text'):
            return
            
        data = self.spw_transmit_text.toPlainText()
        if data.strip():
            if hasattr(self, 'spw_is_connected') and self.spw_is_connected and hasattr(self, 'spw_receiver') and self.spw_receiver:
                try:
                    # Enviar dados através do backend SPW
                    self.spw_receiver.send_data(data)
                    print(f"Transmitting data via SPW: {data}")
                except Exception as e:
                    print(f"Error transmitting data: {e}")
                    self.spw_received_text.append(f"[ERROR] Failed to transmit: {e}")
            else:
                print("Not connected - cannot transmit")
                self.spw_received_text.append("[ERROR] Not connected - cannot transmit data")
        else:
            print("No data to transmit")
            self.spw_received_text.append("[WARNING] No data to transmit")
    
    def on_spw_clear_receiver_clicked(self):
        """Callback para o botão Clear Receiver SPW"""
        if hasattr(self, 'spw_received_text'):
            self.spw_received_text.clear()
            print("SPW Receiver cleared")
    
    def on_spw_clear_transmit_clicked(self):
        """Callback para o botão Clear Transmit SPW"""
        if hasattr(self, 'spw_transmit_text'):
            self.spw_transmit_text.clear()
            print("SPW Transmit area cleared")
    
    def on_spw_save_logs_clicked(self):
        """Callback para o botão Save Logs SPW"""
        if not hasattr(self, 'spw_received_text'):
            return
            
        received_data = self.spw_received_text.toPlainText()
        if received_data.strip():
            try:
                from PySide6.QtWidgets import QFileDialog
                import datetime
                
                # Gerar nome do arquivo com timestamp
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                default_filename = f"spw_logs_{timestamp}.txt"
                
                # Abrir diálogo para salvar arquivo
                filename, _ = QFileDialog.getSaveFileName(
                    self,
                    "Save SPW Logs",
                    default_filename,
                    "Text Files (*.txt);;All Files (*)"
                )
                
                if filename:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(f"SPW Communication Logs\n")
                        f.write(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write(f"Host: {self.spw_host_input.text()}\n")
                        f.write(f"Port: {self.spw_port_input.text()}\n")
                        f.write("-" * 50 + "\n\n")
                        f.write(received_data)
                    
                    print(f"Logs saved to: {filename}")
                    self.spw_received_text.append(f"[INFO] Logs saved to: {filename}")
                else:
                    print("Save cancelled")
            except Exception as e:
                print(f"Error saving logs: {e}")
                self.spw_received_text.append(f"[ERROR] Failed to save logs: {e}")
        else:
            print("No logs to save")
            self.spw_received_text.append("[WARNING] No logs to save")
    
    def closeEvent(self, event):
        """Cleanup when application is closing"""
        # Stop worker thread if running
        if self.emulation_worker and self.emulation_worker.isRunning():
            self.log_control_message("Stopping background emulation thread...")
            self.emulation_worker.terminate()
            if not self.emulation_worker.wait(3000):  # Wait up to 3 seconds
                self.emulation_worker.kill()  # Force kill if it doesn't stop
        
        # Stop SPW receiver if running
        if hasattr(self, 'spw_receiver') and self.spw_receiver:
            self.spw_receiver.stop()
        
        # Accept the close event
        event.accept()

def main():
    app = QApplication(sys.argv)
    
    # Configurar tema
    app.setStyle('Fusion')
    
    # Adiciona a splash screen
    try:
        # Tentar carregar a imagem QEMULA
        splash_pix = QPixmap("images/qemula.png")
        if splash_pix.isNull():
            # Fallback para o diretório raiz se não encontrar na pasta images
            splash_pix = QPixmap("qemula.png")
        
        if splash_pix.isNull():
            # Se ainda não encontrou, criar uma splash simples com texto
            splash_pix = QPixmap(400, 300)
            splash_pix.fill(QColor(25, 25, 112))  # Azul escuro como no logo
            
            painter = QPainter(splash_pix)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Desenhar o texto QEMULA
            font = QFont("Arial", 48, QFont.Bold)
            painter.setFont(font)
            painter.setPen(QColor(255, 255, 255))  # Branco
            painter.drawText(splash_pix.rect(), Qt.AlignCenter, "QEMULA")
            
            # Desenhar subtítulo
            font_small = QFont("Arial", 14)
            painter.setFont(font_small)
            painter.setPen(QColor(200, 200, 255))  # Azul claro
            text_rect = splash_pix.rect()
            text_rect.setTop(text_rect.center().y() + 40)
            painter.drawText(text_rect, Qt.AlignCenter, "QEMU Emulation Manager")
            
            painter.end()
        
        splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
        splash.setWindowFlag(Qt.FramelessWindowHint)  # Remove a borda da janela
        splash.show()
        
        # Simula o carregamento com mensagens informativas
        loading_messages = [
            "Initializing QEMU interface...",
            "Loading Docker integration...", 
            "Setting up SpaceWire protocol...",
            "Configuring UART communication...",
            "Finalizing application..."
        ]
        
        for i, message in enumerate(loading_messages):
            progress = (i + 1) * 20
            splash.showMessage(f"{message}\nLoading... {progress}%", 
                             Qt.AlignBottom | Qt.AlignCenter, Qt.white)
            app.processEvents()  # Processa eventos para atualizar a splash
            time.sleep(0.5)  # Simula o tempo de carregamento
        
    except Exception as e:
        print(f"Error creating splash screen: {e}")
        splash = None
    
    # Inicializa a janela principal
    window = QemulaMainApp()
    
    if splash:
        splash.finish(window)  # Fecha a splash screen quando a janela principal é exibida
    
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
