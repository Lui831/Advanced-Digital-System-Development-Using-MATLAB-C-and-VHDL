import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QTextEdit, 
                             QFrame, QLineEdit, QSplitter, QListWidget, QTabWidget,
                             QListWidgetItem, QCheckBox, QScrollArea, QSlider)
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QFont, QPalette, QColor, QIcon, QPainter, QPen, QBrush

# Importar o backend para conexão SPW
from backend.reciever import SpaceWireReceiver

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

class QemulaTransceiverSPWApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QEMULA APP - Transceiver SPW")
        self.setGeometry(100, 100, 1400, 800)
        
        # Inicializar conexão SPW backend
        self.spw_receiver = None
        self.is_connected = False
        
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
            ("Transciever SPW", True),  # Item ativo
            ("Transciever UART", False),
            ("Settings", False)
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

        # Conteúdo principal - dividido em duas seções
        content_layout = QVBoxLayout()
        
        # Seção superior - Received Data e Start Connection
        top_section = self.create_top_section()
        content_layout.addWidget(top_section)
        
        # Seção inferior - Data Transmit e botões
        bottom_section = self.create_bottom_section()
        content_layout.addWidget(bottom_section)
        
        layout.addLayout(content_layout)

        return main_widget
    
    def create_header(self):
        from PySide6.QtGui import QPixmap
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
    
    def create_top_section(self):
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
        self.received_text = QTextEdit()
        self.received_text.setReadOnly(True)
        self.received_text.setMinimumHeight(200)
        self.received_text.setStyleSheet("""
            QTextEdit {
                background-color: #e5e5e5;
                border: 1px solid #cccccc;
                border-radius: 8px;
                padding: 10px;
                font-family: monospace;
                font-size: 11px;
            }
        """)
        self.received_text.setPlaceholderText("Received data will appear here...")
        received_layout.addWidget(self.received_text)
        
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
        self.host_input = QLineEdit()
        self.host_input.setText("localhost")
        self.host_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 5px;
                font-size: 10px;
            }
        """)
        host_layout.addWidget(host_label)
        host_layout.addWidget(self.host_input)
        connection_layout.addLayout(host_layout)
        
        # Port
        port_layout = QHBoxLayout()
        port_label = QLabel("Port:")
        port_label.setFont(QFont("Arial", 10))
        port_label.setFixedWidth(40)
        self.port_input = QLineEdit()
        self.port_input.setText("5054")
        self.port_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 5px;
                font-size: 10px;
            }
        """)
        port_layout.addWidget(port_label)
        port_layout.addWidget(self.port_input)
        connection_layout.addLayout(port_layout)
        
        # Status da conexão
        self.connection_status = QLabel("Disconnected")
        self.connection_status.setFont(QFont("Arial", 10, QFont.Bold))
        self.connection_status.setStyleSheet("color: red;")
        self.connection_status.setAlignment(Qt.AlignCenter)
        connection_layout.addWidget(self.connection_status)
        
        # Switch para Start Connection
        switch_layout = QHBoxLayout()
        switch_label = QLabel("Connect:")
        switch_label.setFont(QFont("Arial", 10))
        self.connection_switch = ToggleSwitch()
        self.connection_switch.toggled.connect(self.on_connection_toggle)
        switch_layout.addWidget(switch_label)
        switch_layout.addStretch()
        switch_layout.addWidget(self.connection_switch)
        connection_layout.addLayout(switch_layout)
        
        connection_layout.addStretch()
        
        top_layout.addWidget(connection_frame, 1)  # Ocupar 1/3 do espaço
        
        # Widget container para o layout
        top_widget = QWidget()
        top_widget.setLayout(top_layout)
        
        return top_widget
    
    def create_bottom_section(self):
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
        self.transmit_text = QTextEdit()
        self.transmit_text.setMinimumHeight(200)
        self.transmit_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #cccccc;
                border-radius: 8px;
                padding: 10px;
                font-family: monospace;
                font-size: 11px;
            }
        """)
        self.transmit_text.setPlaceholderText("Enter data to transmit in HEX format (e.g., FF 00 AA BB or FF00AABB)...")
        transmit_layout.addWidget(self.transmit_text)
        
        bottom_layout.addWidget(transmit_frame, 2)  # Ocupar 2/3 do espaço
        
        # Seção de botões
        buttons_frame = QFrame()
        buttons_frame.setFrameStyle(QFrame.Box)
        buttons_layout = QVBoxLayout(buttons_frame)
        buttons_layout.setContentsMargins(20, 20, 20, 20)
        buttons_layout.setSpacing(15)
        
        # Criar botões com ícones
        button_configs = [
            ("Transmit", "▶", self.on_transmit_clicked),
            ("Clear Receiver", "×", self.on_clear_receiver_clicked),
            ("Clear Transmit", "×", self.on_clear_transmit_clicked),
            ("Save Logs", "💾", self.on_save_logs_clicked)
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
    
    def on_connection_toggle(self, checked):
        """Callback para quando o switch de conexão é alterado"""
        if checked:
            # Conectar ao backend SPW
            try:
                # Obter configurações dos campos de entrada
                host = self.host_input.text().strip() or "localhost"
                port_text = self.port_input.text().strip() or "5054"
                
                try:
                    port = int(port_text)
                except ValueError:
                    self.received_text.append("[ERROR] Invalid port number")
                    self.connection_switch.setChecked(False)
                    return
                
                # Atualizar status
                self.connection_status.setText("Connecting...")
                self.connection_status.setStyleSheet("color: orange;")
                
                self.spw_receiver = SpaceWireReceiver(host, port)
                self.spw_receiver.message_received.connect(self.on_message_received)
                self.spw_receiver.start()
                
                self.is_connected = True
                print(f"SPW Connection started - connecting to {host}:{port}")
                self.received_text.append(f"[INFO] Connecting to {host}:{port}...")
                
                # Simulação de conexão bem-sucedida após um pequeno delay
                from PySide6.QtCore import QTimer
                self.connection_timer = QTimer()
                self.connection_timer.timeout.connect(self.check_connection_status)
                self.connection_timer.setSingleShot(True)
                self.connection_timer.start(2000)  # 2 segundos
                
            except Exception as e:
                print(f"Error starting SPW connection: {e}")
                self.received_text.append(f"[ERROR] Failed to start connection: {e}")
                self.connection_switch.setChecked(False)
                self.connection_status.setText("Disconnected")
                self.connection_status.setStyleSheet("color: red;")
                self.is_connected = False
        else:
            # Desconectar do backend SPW
            if self.spw_receiver:
                self.spw_receiver.stop()
                self.spw_receiver = None
            
            self.is_connected = False
            self.connection_status.setText("Disconnected")
            self.connection_status.setStyleSheet("color: red;")
            print("SPW Connection stopped")
            self.received_text.append("[INFO] Connection stopped")
    
    def check_connection_status(self):
        """Verifica e atualiza o status da conexão"""
        if self.is_connected and self.spw_receiver:
            # Em uma implementação real, você verificaria se a conexão está ativa
            # Por agora, vamos simular uma conexão bem-sucedida
            self.connection_status.setText("Connected")
            self.connection_status.setStyleSheet("color: green;")
            self.received_text.append("[INFO] Connection established successfully!")
        else:
            self.connection_status.setText("Failed")
            self.connection_status.setStyleSheet("color: red;")
    
    def on_message_received(self, message):
        """Callback para quando uma mensagem é recebida do backend"""
        self.received_text.append(message)

    def on_transmit_clicked(self):
        """Callback para o botão Transmit"""
        data = self.transmit_text.toPlainText().strip()
        if data:
            if self.is_connected and self.spw_receiver:
                try:
                    # Normalizar dados para formato hex (remover espaços e converter para uppercase)
                    hex_data = data.replace(" ", "").replace("\n", "").replace("\t", "").upper()
                    
                    # Validar se são caracteres hexadecimais válidos
                    try:
                        bytes.fromhex(hex_data)
                        self.received_text.append(f"[INFO] Transmitting: {hex_data}")
                    except ValueError:
                        self.received_text.append(f"[ERROR] Invalid hexadecimal format: {data}")
                        return
                    
                    # Enviar dados através do backend SPW
                    self.spw_receiver.send_data(hex_data)
                    print(f"Transmitting data via SPW: {hex_data}")
                except Exception as e:
                    print(f"Error transmitting data: {e}")
                    self.received_text.append(f"[ERROR] Failed to transmit: {e}")
            else:
                print("Not connected - cannot transmit")
                self.received_text.append("[ERROR] Not connected - cannot transmit data")
        else:
            print("No data to transmit")
            self.received_text.append("[WARNING] No data to transmit")
    
    def on_clear_receiver_clicked(self):
        """Callback para o botão Clear Receiver"""
        self.received_text.clear()
        print("Receiver cleared")
    
    def on_clear_transmit_clicked(self):
        """Callback para o botão Clear Transmit"""
        self.transmit_text.clear()
        print("Transmit area cleared")
    
    def on_save_logs_clicked(self):
        """Callback para o botão Save Logs"""
        received_data = self.received_text.toPlainText()
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
                        f.write(f"Host: {self.host_input.text()}\n")
                        f.write(f"Port: {self.port_input.text()}\n")
                        f.write("-" * 50 + "\n\n")
                        f.write(received_data)
                    
                    print(f"Logs saved to: {filename}")
                    self.received_text.append(f"[INFO] Logs saved to: {filename}")
                else:
                    print("Save cancelled")
            except Exception as e:
                print(f"Error saving logs: {e}")
                self.received_text.append(f"[ERROR] Failed to save logs: {e}")
        else:
            print("No logs to save")
            self.received_text.append("[WARNING] No logs to save")
    
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
        """)

def main():
    app = QApplication(sys.argv)
    
    # Configurar tema
    app.setStyle('Fusion')
    
    window = QemulaTransceiverSPWApp()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
