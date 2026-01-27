import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QTextEdit, 
                             QFrame, QLineEdit, QSplitter, QListWidget, QTabWidget,
                             QListWidgetItem, QCheckBox, QScrollArea, QSlider,
                             QComboBox, QSpinBox, QGroupBox, QGridLayout)
from PySide6.QtCore import Qt, QSize, Signal, QPropertyAnimation, QRect
from PySide6.QtGui import QFont, QPalette, QColor, QIcon, QPainter, QPen, QBrush

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

class AccordionItem(QWidget):
    """Widget de item accordion expansível"""
    
    def __init__(self, title, content, parent=None):
        super().__init__(parent)
        self.is_expanded = False
        self.content_widget = None
        self.setup_ui(title, content)
        
    def setup_ui(self, title, content):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header do accordion
        self.header = QPushButton(title)
        self.header.setFixedHeight(50)
        self.header.setStyleSheet("""
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
        self.header.clicked.connect(self.toggle_content)
        layout.addWidget(self.header)
        
        # Conteúdo do accordion
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border: 1px solid #e0e0e0;
                border-top: none;
                border-radius: 0 0 8px 8px;
                padding: 15px;
            }
        """)
        
        content_layout = QVBoxLayout(self.content_widget)
        content_label = QLabel(content)
        content_label.setWordWrap(True)
        content_label.setFont(QFont("Arial", 11))
        content_layout.addWidget(content_label)
        
        self.content_widget.setVisible(False)
        layout.addWidget(self.content_widget)
        
        self.update_header_icon()
        
    def toggle_content(self):
        self.is_expanded = not self.is_expanded
        self.content_widget.setVisible(self.is_expanded)
        self.update_header_icon()
        
    def update_header_icon(self):
        icon = "▲" if self.is_expanded else "▼"
        current_text = self.header.text()
        # Remove o ícone anterior se existir
        if current_text.endswith(" ▲") or current_text.endswith(" ▼"):
            current_text = current_text[:-2]
        self.header.setText(f"{current_text} {icon}")

class QemulaSettingsApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QEMULA APP - Settings")
        self.setGeometry(100, 100, 1400, 800)
        self.setup_ui()
        self.apply_styles()
    
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
            ("Settings", True)  # Item ativo
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
                        border-radius: 8px;
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
                        border-radius: 8px;
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

        # Scroll area para o conteúdo
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(20)
        
        # Seções de configuração
        general_section = self.create_general_settings()
        scroll_layout.addWidget(general_section)
        
        connection_section = self.create_connection_settings()
        scroll_layout.addWidget(connection_section)
        
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
    
    def create_header(self):
        from PySide6.QtGui import QPixmap
        header = QFrame()
        layout = QHBoxLayout(header)
        
        # Título da interface
        title = QLabel("Interface Settings")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Status QEMULA run
        status_label = QLabel("QEMULA run")
        status_label.setFont(QFont("Arial", 12))
        layout.addWidget(status_label)
        
        # Pause icon (simulado com texto)
        pause_icon = QLabel("⏸️")
        pause_icon.setFont(QFont("Arial", 16))
        layout.addWidget(pause_icon)
        
        layout.addStretch()
        
        # Social icons (replace emojis with images)
        icons_layout = QHBoxLayout()
        icon_files = [
            "images/docker.png",
            "images/email.png",
            "images/github.png",
            "images/podman.png"
        ]
        # URLs de documentação
        doc_urls = [
            "https://docs.docker.com/",
            "https://www.rfc-editor.org/rfc/rfc5322",  # Email RFC
            "https://docs.github.com/pt",
            "https://podman.io/getting-started/"
        ]
        from PySide6.QtWidgets import QPushButton
        from PySide6.QtGui import QDesktopServices
        from PySide6.QtCore import QUrl
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
                # Fallback se a imagem não existir
                btn.setText("🔗")
                btn.setFont(QFont("Arial", 24))
            btn.setFixedSize(52, 52)
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
    
    def create_help_section(self):
        # Seção de ajuda com accordions
        group = QGroupBox("Help ℹ️")
        group.setFont(QFont("Arial", 14, QFont.Bold))
        layout = QVBoxLayout(group)
        layout.setSpacing(10)
        
        # Itens de ajuda
        help_items = [
            ("Getting Started", "Welcome to QEMULA! This application provides a comprehensive interface for QEMU emulation, Docker container management, and hardware communication via SPW and UART protocols. Start by configuring your emulation environment in the Control tab."),
            ("Docker Integration", "The Docker tab allows you to manage container images and start containers for your emulation environment. Use the search functionality to find specific images and toggle the container start switch to enable automatic container startup."),
            ("SPW Communication", "Space Wire (SPW) is a spacecraft communication network protocol. Use the Transceiver SPW tab to establish connections, send and receive data packets, and monitor communication logs."),
            ("UART Communication", "Universal Asynchronous Receiver-Transmitter (UART) provides serial communication. Configure baud rates, data bits, and parity settings in the connection settings above."),
            ("Debugging Features", "The Debug tab provides comprehensive debugging tools including breakpoint management, variable inspection, step execution, and GDB command interface for advanced debugging scenarios.")
        ]
        
        for title, content in help_items:
            accordion_item = AccordionItem(title, content)
            layout.addWidget(accordion_item)
        
        return group
    
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

def main():
    app = QApplication(sys.argv)
    
    # Configurar tema
    app.setStyle('Fusion')
    
    window = QemulaSettingsApp()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()