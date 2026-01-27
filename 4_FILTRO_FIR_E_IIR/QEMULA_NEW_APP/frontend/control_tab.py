import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QTextEdit, 
                             QFrame, QLineEdit, QSplitter, QListWidget, QTabWidget,
                             QMessageBox, QFileDialog)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QPalette, QColor, QIcon

# Adicionar o diretório pai ao path para importar o backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar o backend para controle de protocolo
from backend.protocol_interface import ProtocolInterface

class QemulaApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QEMULA APP - Control Page (Emulation)")
        self.setGeometry(100, 100, 1400, 800)
        
        # Inicializar interface de protocolo backend
        self.protocol = ProtocolInterface()
        
        # Armazenar referências dos elementos UI para acesso posterior
        self.logs_text = None
        self.addr_input = None
        self.val_input = None
        self.var_input = None
        self.delete_bp_input = None
        self.config_bp_input = None
        self.gdb_input = None
        self.ram_value_input = None
        
        self.setup_ui()
        self.apply_styles()
        
        # Log inicial para confirmar inicialização
        self.log_message("QEMULA APP iniciado - Backend conectado")
        self.log_message("Aguardando conexão com o servidor QEMU...")
        
        # Verificar se o backend está conectado
        if self.protocol.is_connected():
            self.log_message("Backend conectado com sucesso!")
        else:
            self.log_message("Backend aguardando conexão com o servidor...")
    
    def log_message(self, message):
        """Adiciona uma mensagem aos logs do sistema"""
        if self.logs_text:
            self.logs_text.append(f"[{QApplication.instance().timestamp() if hasattr(QApplication.instance(), 'timestamp') else 'INFO'}] {message}")
    
    def show_message(self, title, message):
        """Mostra uma mensagem para o usuário"""
        msg_box = QMessageBox()
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec()
    
    def handle_protocol_response(self, response, action_name):
        """Processa a resposta do protocolo e mostra ao usuário"""
        if "error" in response:
            self.log_message(f"Erro em {action_name}: {response['error']}")
            self.show_message("Erro", f"Erro ao executar {action_name}:\n{response['error']}")
        else:
            self.log_message(f"{action_name} executado: {response.get('return', 'Sucesso')}")
            if response.get('body') and response['body'] != '-':
                self.log_message(f"Dados retornados: {response['body']}")
    
    # Métodos para botões de emulação
    def on_start_emulation(self):
        """Inicia a emulação"""
        self.log_message("Iniciando emulação...")
        response = self.protocol.send_start_emulation()
        self.handle_protocol_response(response, "Start Emulation")
    
    def on_pause_emulation(self):
        """Pausa a emulação"""
        self.log_message("Pausando emulação...")
        response = self.protocol.send_pause_machine()
        self.handle_protocol_response(response, "Pause Emulation")
    
    def on_unpause_emulation(self):
        """Despausa a emulação"""
        self.log_message("Despausando emulação...")
        response = self.protocol.send_unpause_machine()
        self.handle_protocol_response(response, "Unpause Emulation")
    
    def on_stop_emulation(self):
        """Para a emulação"""
        self.log_message("Parando emulação...")
        response = self.protocol.send_quit_emulation()
        self.handle_protocol_response(response, "Stop Emulation")
    
    def on_read_io(self):
        """Lê I/O do endereço especificado"""
        if not self.addr_input or not self.addr_input.text().strip():
            self.show_message("Erro", "Por favor, insira um endereço válido para leitura.")
            return
        
        try:
            addr_text = self.addr_input.text().strip()
            if addr_text.lower().startswith('0x'):
                addr = int(addr_text, 16)
            else:
                addr = int(addr_text, 16)
            
            self.log_message(f"Lendo I/O do endereço 0x{addr:08X}...")
            response = self.protocol.send_read_io(addr)
            self.handle_protocol_response(response, "Read I/O")
        except ValueError:
            self.show_message("Erro", "Endereço inválido. Use formato hexadecimal (ex: 0x1000 ou 1000).")
    
    def on_write_io(self):
        """Escreve I/O no endereço especificado"""
        if not self.val_input or not self.val_input.text().strip():
            self.show_message("Erro", "Por favor, insira endereço e valor para escrita (formato: ADDR/VAL).")
            return
        
        try:
            input_text = self.val_input.text().strip()
            if '/' not in input_text:
                self.show_message("Erro", "Use o formato ADDR/VAL (ex: 1000/FF ou 0x1000/0xFF).")
                return
            
            addr_text, val_text = input_text.split('/', 1)
            
            if addr_text.lower().startswith('0x'):
                addr = int(addr_text, 16)
            else:
                addr = int(addr_text, 16)
                
            if val_text.lower().startswith('0x'):
                value = int(val_text, 16)
            else:
                value = int(val_text, 16)
            
            self.log_message(f"Escrevendo I/O: endereço 0x{addr:08X}, valor 0x{value:08X}...")
            response = self.protocol.send_write_io(addr, value)
            self.handle_protocol_response(response, "Write I/O")
        except ValueError:
            self.show_message("Erro", "Formato inválido. Use ADDR/VAL em hexadecimal (ex: 1000/FF).")
    
    # Métodos para botões de debug
    def on_step_into(self):
        """Executa step into"""
        self.log_message("Executando step into...")
        response = self.protocol.send_step_into()
        self.handle_protocol_response(response, "Step Into")
    
    def on_configure_debug(self):
        """Configura o debug (modo 1 por padrão)"""
        self.log_message("Configurando debug...")
        response = self.protocol.send_config_debug(1)  # Modo 1 por padrão
        self.handle_protocol_response(response, "Configure Debug")
    
    def on_verify_variable(self):
        """Verifica uma variável"""
        if not self.var_input or not self.var_input.text().strip():
            self.show_message("Erro", "Por favor, insira o nome da variável.")
            return
        
        var_name = self.var_input.text().strip()
        self.log_message(f"Verificando variável: {var_name}...")
        response = self.protocol.send_verify_variable(var_name)
        self.handle_protocol_response(response, "Verify Variable")
    
    def on_delete_breakpoint(self):
        """Deleta um breakpoint"""
        if not self.delete_bp_input or not self.delete_bp_input.text().strip():
            self.show_message("Erro", "Por favor, insira o número da linha do breakpoint.")
            return
        
        try:
            line = int(self.delete_bp_input.text().strip())
            self.log_message(f"Deletando breakpoint na linha {line}...")
            response = self.protocol.send_delete_breakpoint(line)
            self.handle_protocol_response(response, "Delete Breakpoint")
        except ValueError:
            self.show_message("Erro", "Número de linha inválido.")
    
    def on_configure_breakpoint(self):
        """Configura um breakpoint"""
        if not self.config_bp_input or not self.config_bp_input.text().strip():
            self.show_message("Erro", "Por favor, insira o número da linha do breakpoint.")
            return
        
        try:
            line = int(self.config_bp_input.text().strip())
            self.log_message(f"Configurando breakpoint na linha {line}...")
            response = self.protocol.send_config_breakpoint(line)
            self.handle_protocol_response(response, "Configure Breakpoint")
        except ValueError:
            self.show_message("Erro", "Número de linha inválido.")
    
    def on_continue_emulation(self):
        """Continua a emulação"""
        self.log_message("Continuando emulação...")
        response = self.protocol.send_continue_emulation()
        self.handle_protocol_response(response, "Continue Emulation")
    
    def on_next_line(self):
        """Executa próxima linha"""
        self.log_message("Executando próxima linha...")
        response = self.protocol.send_next_line()
        self.handle_protocol_response(response, "Next Line")
    
    def on_finish_execution(self):
        """Finaliza execução"""
        self.log_message("Finalizando execução...")
        response = self.protocol.send_finish_execution()
        self.handle_protocol_response(response, "Finish Execution")
    
    def on_command_gdb(self):
        """Envia comando GDB"""
        if not self.gdb_input or not self.gdb_input.text().strip():
            self.show_message("Erro", "Por favor, insira um comando GDB.")
            return
        
        command = self.gdb_input.text().strip()
        self.log_message(f"Enviando comando GDB: {command}...")
        response = self.protocol.send_gdb_command(command)
        self.handle_protocol_response(response, "GDB Command")
    
    # Métodos para botões de settings
    def on_verify_state(self):
        """Verifica o estado da máquina"""
        self.log_message("Verificando estado da máquina...")
        response = self.protocol.send_verify_state()
        self.handle_protocol_response(response, "Verify State")
        if response.get('machine_state'):
            self.log_message(f"Estado da máquina: {response['machine_state']}")
    
    def on_inject_elf(self):
        """Injeta arquivo ELF"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Selecionar arquivo ELF", "", "ELF files (*.elf);;All files (*.*)")
        if file_path:
            try:
                with open(file_path, 'rb') as f:
                    elf_data = f.read()
                
                self.log_message(f"Injetando arquivo ELF: {file_path}...")
                response = self.protocol.send_inject_elf(elf_data)
                self.handle_protocol_response(response, "Inject ELF")
            except Exception as e:
                self.show_message("Erro", f"Erro ao ler arquivo ELF: {str(e)}")
    
    def on_inject_ahbrom(self):
        """Injeta arquivo AHBROM"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Selecionar arquivo AHBROM", "", "ROM files (*.rom *.bin);;All files (*.*)")
        if file_path:
            try:
                with open(file_path, 'rb') as f:
                    ahb_data = f.read()
                
                self.log_message(f"Injetando arquivo AHBROM: {file_path}...")
                response = self.protocol.send_inject_ahbrom(ahb_data)
                self.handle_protocol_response(response, "Inject AHBROM")
            except Exception as e:
                self.show_message("Erro", f"Erro ao ler arquivo AHBROM: {str(e)}")
    
    def on_configure_ram(self):
        """Configura RAM"""
        if not self.ram_value_input or not self.ram_value_input.text().strip():
            self.show_message("Erro", "Por favor, insira o tamanho da RAM em bytes.")
            return
        
        try:
            ram_size = int(self.ram_value_input.text().strip())
            if ram_size <= 0:
                self.show_message("Erro", "Tamanho da RAM deve ser maior que zero.")
                return
            
            self.log_message(f"Configurando RAM: {ram_size} bytes...")
            response = self.protocol.send_config_ram(ram_size)
            self.handle_protocol_response(response, "Configure RAM")
        except ValueError:
            self.show_message("Erro", "Tamanho da RAM inválido. Use apenas números.")
    
    def on_configure_os_abi(self):
        """Configura OS ABI (linux por padrão)"""
        self.log_message("Configurando OS ABI para linux...")
        response = self.protocol.send_set_os_abi("linux")
        self.handle_protocol_response(response, "Configure OS ABI")
    
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
            ("Control", True),  # Item ativo
            ("Transciever SPW", False),
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

        # Tabs (agora com os botões de controle dentro)
        tabs = self.create_tabs()
        layout.addWidget(tabs)

        # System logs
        logs_area = self.create_logs_area()
        layout.addWidget(logs_area)

        return main_widget
    
    def create_header(self):
        from PySide6.QtGui import QPixmap
        header = QFrame()
        layout = QHBoxLayout(header)
        
        # Título da interface
        title = QLabel("Control Interface")
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
            pixmap = QPixmap(icon_path)
            pixmap = pixmap.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            btn.setIcon(QIcon(pixmap))
            btn.setIconSize(QSize(48, 48))
            btn.setFixedSize(52, 52)
            btn.clicked.connect(lambda checked, link=url: QDesktopServices.openUrl(QUrl(link)))
            icons_layout.addWidget(btn)
        layout.addLayout(icons_layout)
        
        return header
    
    def create_tabs(self):
        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.North)
        
        # Tab Emulation com os botões de controle
        emulation_tab = QWidget()
        emulation_layout = QVBoxLayout(emulation_tab)
        emulation_layout.setSpacing(20)
        emulation_layout.setContentsMargins(20, 20, 20, 20)
        
        # Primeira linha de botões - 2 nos cantos, 1 centralizado
        first_row = QHBoxLayout()
        
        # Pause Emulation (esquerda)
        pause_btn = QPushButton("Pause Emulation")
        pause_btn.setFixedSize(180, 40)
        # Adicionar ícone de pause usando símbolo simples em branco
        pause_icon = self.create_text_icon("||", 16, Qt.white)
        pause_btn.setIcon(pause_icon)
        pause_btn.setIconSize(QSize(16, 16))
        pause_btn.setStyleSheet("""
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
        pause_btn.clicked.connect(self.on_pause_emulation)
        first_row.addWidget(pause_btn)
        
        first_row.addStretch()  # Espaço flexível
        
        # Read I/O (centro)
        read_btn = QPushButton("Read I/O")
        read_btn.setFixedSize(140, 40)
        # Adicionar ícone de leitura
        read_icon = self.create_text_icon("R", 16)
        read_btn.setIcon(read_icon)
        read_btn.setIconSize(QSize(16, 16))
        read_btn.setStyleSheet("""
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
        read_btn.clicked.connect(self.on_read_io)
        first_row.addWidget(read_btn)
        
        first_row.addStretch()  # Espaço flexível
        
        # Unpause Emulation (direita)
        unpause_btn = QPushButton("Unpause Emulation")
        unpause_btn.setFixedSize(180, 40)
        # Adicionar ícone de play
        unpause_icon = self.create_text_icon("▶", 16)
        unpause_btn.setIcon(unpause_icon)
        unpause_btn.setIconSize(QSize(16, 16))
        unpause_btn.setStyleSheet("""
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
        unpause_btn.clicked.connect(self.on_unpause_emulation)
        first_row.addWidget(unpause_btn)
        
        emulation_layout.addLayout(first_row)
        
        # Linha com a primeira caixa de texto (acima do Write I/O)
        inputs_row1 = QHBoxLayout()
        
        # Espaço vazio equivalente ao botão da esquerda
        left_spacer1 = QWidget()
        left_spacer1.setFixedSize(180, 1)
        inputs_row1.addWidget(left_spacer1)
        
        inputs_row1.addStretch()  # Espaço flexível
        
        # Input para Read I/O (abaixo do Read I/O)
        addr_input = QLineEdit()
        addr_input.setPlaceholderText("Escreva o ADDR em hex:")
        addr_input.setFixedSize(140, 30)
        self.addr_input = addr_input  # Armazenar referência
        inputs_row1.addWidget(addr_input)
        
        inputs_row1.addStretch()  # Espaço flexível
        
        # Espaço vazio equivalente ao botão da direita
        right_spacer1 = QWidget()
        right_spacer1.setFixedSize(180, 1)
        inputs_row1.addWidget(right_spacer1)
        
        emulation_layout.addLayout(inputs_row1)
        
        # Segunda linha de botões
        second_row = QHBoxLayout()
        
        # Stop Emulation (esquerda)
        stop_btn = QPushButton("Stop Emulation")
        stop_btn.setFixedSize(180, 40)
        # Adicionar ícone de stop usando símbolo simples em branco
        stop_icon = self.create_text_icon("■", 16, Qt.white)
        stop_btn.setIcon(stop_icon)
        stop_btn.setIconSize(QSize(16, 16))
        stop_btn.setStyleSheet("""
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
        stop_btn.clicked.connect(self.on_stop_emulation)
        second_row.addWidget(stop_btn)
        
        second_row.addStretch()  # Espaço flexível
        
        # Write I/O (centro)
        write_btn = QPushButton("Write I/O")
        write_btn.setFixedSize(140, 40)
        # Adicionar ícone de escrita
        write_icon = self.create_text_icon("W", 16)
        write_btn.setIcon(write_icon)
        write_btn.setIconSize(QSize(16, 16))
        write_btn.setStyleSheet("""
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
        write_btn.clicked.connect(self.on_write_io)
        second_row.addWidget(write_btn)
        
        second_row.addStretch()  # Espaço flexível
        
        # Start Emulation (direita)
        start_btn = QPushButton("Start Emulation")
        start_btn.setFixedSize(180, 40)
        # Adicionar ícone de start
        start_icon = self.create_text_icon("▶", 16)
        start_btn.setIcon(start_icon)
        start_btn.setIconSize(QSize(16, 16))
        start_btn.setStyleSheet("""
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
        start_btn.clicked.connect(self.on_start_emulation)
        second_row.addWidget(start_btn)
        
        emulation_layout.addLayout(second_row)
        
        # Linha com a segunda caixa de texto (abaixo do Write I/O)
        inputs_row2 = QHBoxLayout()
        
        # Espaço vazio equivalente ao botão da esquerda
        left_spacer2 = QWidget()
        left_spacer2.setFixedSize(180, 1)
        inputs_row2.addWidget(left_spacer2)
        
        inputs_row2.addStretch()  # Espaço flexível
        
        # Input para Write I/O (abaixo do Write I/O)
        val_input = QLineEdit()
        val_input.setPlaceholderText("Escreva o ADDR/VAL em hex:")
        val_input.setFixedSize(140, 30)
        self.val_input = val_input  # Armazenar referência
        inputs_row2.addWidget(val_input)
        
        inputs_row2.addStretch()  # Espaço flexível
        
        # Espaço vazio equivalente ao botão da direita
        right_spacer2 = QWidget()
        right_spacer2.setFixedSize(180, 1)
        inputs_row2.addWidget(right_spacer2)
        
        emulation_layout.addLayout(inputs_row2)
        
        emulation_layout.addStretch()  # Adicionar espaço flexível no final
        
        # Criar ícones para as tabs usando as imagens
        from PySide6.QtGui import QPixmap
        emulation_pixmap = QPixmap("images/emulation.png")
        emulation_pixmap = emulation_pixmap.scaled(16, 16, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        emulation_icon = QIcon(emulation_pixmap)
        
        debug_pixmap = QPixmap("images/debug.png")
        debug_pixmap = debug_pixmap.scaled(16, 16, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        debug_icon = QIcon(debug_pixmap)
        
        settings_pixmap = QPixmap("images/settings.png")
        settings_pixmap = settings_pixmap.scaled(16, 16, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        settings_icon = QIcon(settings_pixmap)
        
        tabs.addTab(emulation_tab, emulation_icon, "Emulation")
        
        # Tab Debug com os botões de controle
        debug_tab = QWidget()
        debug_layout = QVBoxLayout(debug_tab)
        debug_layout.setSpacing(20)
        debug_layout.setContentsMargins(20, 20, 20, 20)
        
        # Primeira linha de botões - debug específicos com colunas centralizadas
        debug_first_row = QHBoxLayout()
        
        # Coluna esquerda
        left_col = QHBoxLayout()
        left_col.addStretch()
        step_into_btn = QPushButton("Step Into")
        step_into_btn.setFixedSize(140, 40)
        step_into_icon = self.create_text_icon("↓", 16, Qt.white)
        step_into_btn.setIcon(step_into_icon)
        step_into_btn.setIconSize(QSize(16, 16))
        step_into_btn.setStyleSheet("""
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
        step_into_btn.clicked.connect(self.on_step_into)
        left_col.addWidget(step_into_btn)
        left_col.addStretch()
        
        # Coluna central
        center_col = QHBoxLayout()
        center_col.addStretch()
        config_debug_btn = QPushButton("Configure Debug")
        config_debug_btn.setFixedSize(160, 40)
        config_debug_icon = self.create_text_icon("⚙", 16, Qt.white)
        config_debug_btn.setIcon(config_debug_icon)
        config_debug_btn.setIconSize(QSize(16, 16))
        config_debug_btn.setStyleSheet("""
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
        config_debug_btn.clicked.connect(self.on_configure_debug)
        center_col.addWidget(config_debug_btn)
        center_col.addStretch()
        
        # Coluna direita
        right_col = QHBoxLayout()
        right_col.addStretch()
        verify_var_btn = QPushButton("Verify Variable")
        verify_var_btn.setFixedSize(160, 40)
        verify_var_icon = self.create_text_icon("?", 16, Qt.white)
        verify_var_btn.setIcon(verify_var_icon)
        verify_var_btn.setIconSize(QSize(16, 16))
        verify_var_btn.setStyleSheet("""
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
        verify_var_btn.clicked.connect(self.on_verify_variable)
        right_col.addWidget(verify_var_btn)
        right_col.addStretch()
        
        # Adicionar as colunas ao layout principal
        debug_first_row.addLayout(left_col, 1)
        debug_first_row.addLayout(center_col, 1)
        debug_first_row.addLayout(right_col, 1)
        
        debug_layout.addLayout(debug_first_row)
        
        # Linha com input para Verify Variable - centralizados em colunas
        debug_input_row1 = QHBoxLayout()
        
        # Coluna esquerda vazia
        left_input_col1 = QHBoxLayout()
        left_input_col1.addStretch()
        left_spacer_debug1 = QWidget()
        left_spacer_debug1.setFixedSize(140, 1)
        left_input_col1.addWidget(left_spacer_debug1)
        left_input_col1.addStretch()
        
        # Coluna central vazia
        center_input_col1 = QHBoxLayout()
        center_input_col1.addStretch()
        center_spacer_debug1 = QWidget()
        center_spacer_debug1.setFixedSize(160, 1)
        center_input_col1.addWidget(center_spacer_debug1)
        center_input_col1.addStretch()
        
        # Coluna direita com input
        right_input_col1 = QHBoxLayout()
        right_input_col1.addStretch()
        var_input = QLineEdit()
        var_input.setPlaceholderText("Chose a variable to check")
        var_input.setFixedSize(160, 30)
        self.var_input = var_input  # Armazenar referência
        right_input_col1.addWidget(var_input)
        right_input_col1.addStretch()
        
        # Adicionar as colunas ao layout principal
        debug_input_row1.addLayout(left_input_col1, 1)
        debug_input_row1.addLayout(center_input_col1, 1)
        debug_input_row1.addLayout(right_input_col1, 1)
        
        debug_layout.addLayout(debug_input_row1)
        
        # Segunda linha de botões - centralizados em colunas
        debug_second_row = QHBoxLayout()
        
        # Coluna esquerda
        left_col2 = QHBoxLayout()
        left_col2.addStretch()
        delete_bp_btn = QPushButton("Delete Breakpoint")
        delete_bp_btn.setFixedSize(140, 40)
        delete_bp_icon = self.create_text_icon("×", 16, Qt.white)
        delete_bp_btn.setIcon(delete_bp_icon)
        delete_bp_btn.setIconSize(QSize(16, 16))
        delete_bp_btn.setStyleSheet("""
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
        delete_bp_btn.clicked.connect(self.on_delete_breakpoint)
        left_col2.addWidget(delete_bp_btn)
        left_col2.addStretch()
        
        # Coluna central com botões numerados
        center_col2 = QHBoxLayout()
        center_col2.addStretch()
        numbers_layout = QHBoxLayout()
        numbers_layout.setSpacing(10)
        
        for i in range(1, 4):
            num_btn = QPushButton(str(i))
            num_btn.setFixedSize(40, 40)
            num_btn.setStyleSheet("""
                QPushButton {
                    background-color: #333333;
                    color: white;
                    border: none;
                    border-radius: 20px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #555555;
                }
            """)
            numbers_layout.addWidget(num_btn)
        
        numbers_widget = QWidget()
        numbers_widget.setLayout(numbers_layout)
        center_col2.addWidget(numbers_widget)
        center_col2.addStretch()
        
        # Coluna direita
        right_col2 = QHBoxLayout()
        right_col2.addStretch()
        config_bp_btn = QPushButton("Configure Breakpoint")
        config_bp_btn.setFixedSize(160, 40)
        config_bp_icon = self.create_text_icon("●", 16, Qt.white)
        config_bp_btn.setIcon(config_bp_icon)
        config_bp_btn.setIconSize(QSize(16, 16))
        config_bp_btn.setStyleSheet("""
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
        config_bp_btn.clicked.connect(self.on_configure_breakpoint)
        right_col2.addWidget(config_bp_btn)
        right_col2.addStretch()
        
        # Adicionar as colunas ao layout principal
        debug_second_row.addLayout(left_col2, 1)
        debug_second_row.addLayout(center_col2, 1)
        debug_second_row.addLayout(right_col2, 1)
        
        debug_layout.addLayout(debug_second_row)
        
        # Linha com inputs para breakpoints - centralizados em colunas
        debug_input_row2 = QHBoxLayout()
        
        # Coluna esquerda com input
        left_input_col2 = QHBoxLayout()
        left_input_col2.addStretch()
        delete_bp_input = QLineEdit()
        delete_bp_input.setPlaceholderText("Set a line to put the breakpoint")
        delete_bp_input.setFixedSize(140, 30)
        self.delete_bp_input = delete_bp_input  # Armazenar referência
        left_input_col2.addWidget(delete_bp_input)
        left_input_col2.addStretch()
        
        # Coluna central vazia
        center_input_col2 = QHBoxLayout()
        center_input_col2.addStretch()
        numbers_spacer = QWidget()
        numbers_spacer.setFixedSize(140, 1)
        center_input_col2.addWidget(numbers_spacer)
        center_input_col2.addStretch()
        
        # Coluna direita com input
        right_input_col2 = QHBoxLayout()
        right_input_col2.addStretch()
        config_bp_input = QLineEdit()
        config_bp_input.setPlaceholderText("Set a line to put the breakpoint")
        config_bp_input.setFixedSize(160, 30)
        self.config_bp_input = config_bp_input  # Armazenar referência
        right_input_col2.addWidget(config_bp_input)
        right_input_col2.addStretch()
        
        # Adicionar as colunas ao layout principal
        debug_input_row2.addLayout(left_input_col2, 1)
        debug_input_row2.addLayout(center_input_col2, 1)
        debug_input_row2.addLayout(right_input_col2, 1)
        
        debug_layout.addLayout(debug_input_row2)
        
        # Terceira linha de botões - centralizados em colunas
        debug_third_row = QHBoxLayout()
        
        # Coluna esquerda
        left_col3 = QHBoxLayout()
        left_col3.addStretch()
        continue_btn = QPushButton("Continue Emulation")
        continue_btn.setFixedSize(180, 40)
        continue_icon = self.create_text_icon("▶", 16, Qt.white)
        continue_btn.setIcon(continue_icon)
        continue_btn.setIconSize(QSize(16, 16))
        continue_btn.setStyleSheet("""
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
        continue_btn.clicked.connect(self.on_continue_emulation)
        left_col3.addWidget(continue_btn)
        left_col3.addStretch()
        
        # Coluna central
        center_col3 = QHBoxLayout()
        center_col3.addStretch()
        next_line_btn = QPushButton("Next Line")
        next_line_btn.setFixedSize(120, 40)
        next_line_icon = self.create_text_icon("→", 16, Qt.white)
        next_line_btn.setIcon(next_line_icon)
        next_line_btn.setIconSize(QSize(16, 16))
        next_line_btn.setStyleSheet("""
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
        next_line_btn.clicked.connect(self.on_next_line)
        center_col3.addWidget(next_line_btn)
        center_col3.addStretch()
        
        # Coluna direita
        right_col3 = QHBoxLayout()
        right_col3.addStretch()
        finish_exec_btn = QPushButton("Finish Execution")
        finish_exec_btn.setFixedSize(160, 40)
        finish_exec_icon = self.create_text_icon("■", 16, Qt.white)
        finish_exec_btn.setIcon(finish_exec_icon)
        finish_exec_btn.setIconSize(QSize(16, 16))
        finish_exec_btn.setStyleSheet("""
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
        finish_exec_btn.clicked.connect(self.on_finish_execution)
        right_col3.addWidget(finish_exec_btn)
        right_col3.addStretch()
        
        # Adicionar as colunas ao layout principal
        debug_third_row.addLayout(left_col3, 1)
        debug_third_row.addLayout(center_col3, 1)
        debug_third_row.addLayout(right_col3, 1)
        
        debug_layout.addLayout(debug_third_row)
        
        # Quarta linha com Command GDB - centralizado
        debug_fourth_row = QHBoxLayout()
        
        # Coluna esquerda vazia
        left_col4 = QHBoxLayout()
        left_col4.addStretch()
        
        # Coluna central com Command GDB
        center_col4 = QHBoxLayout()
        center_col4.addStretch()
        command_gdb_btn = QPushButton("Command GDB")
        command_gdb_btn.setFixedSize(160, 40)
        command_gdb_icon = self.create_text_icon("$", 16, Qt.white)
        command_gdb_btn.setIcon(command_gdb_icon)
        command_gdb_btn.setIconSize(QSize(16, 16))
        command_gdb_btn.setStyleSheet("""
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
        command_gdb_btn.clicked.connect(self.on_command_gdb)
        center_col4.addWidget(command_gdb_btn)
        center_col4.addStretch()
        
        # Coluna direita vazia
        right_col4 = QHBoxLayout()
        right_col4.addStretch()
        
        # Adicionar as colunas ao layout principal
        debug_fourth_row.addLayout(left_col4, 1)
        debug_fourth_row.addLayout(center_col4, 1)
        debug_fourth_row.addLayout(right_col4, 1)
        
        debug_layout.addLayout(debug_fourth_row)
        
        # Input para Command GDB - centralizado
        debug_input_row3 = QHBoxLayout()
        
        # Coluna esquerda vazia
        left_input_col3 = QHBoxLayout()
        left_input_col3.addStretch()
        
        # Coluna central com input
        center_input_col3 = QHBoxLayout()
        center_input_col3.addStretch()
        gdb_input = QLineEdit()
        gdb_input.setPlaceholderText("Put your command to send")
        gdb_input.setFixedSize(160, 30)
        self.gdb_input = gdb_input  # Armazenar referência
        center_input_col3.addWidget(gdb_input)
        center_input_col3.addStretch()
        
        # Coluna direita vazia
        right_input_col3 = QHBoxLayout()
        right_input_col3.addStretch()
        
        # Adicionar as colunas ao layout principal
        debug_input_row3.addLayout(left_input_col3, 1)
        debug_input_row3.addLayout(center_input_col3, 1)
        debug_input_row3.addLayout(right_input_col3, 1)
        
        debug_layout.addLayout(debug_input_row3)
        
        debug_layout.addStretch()  # Adicionar espaço flexível no final
        
        tabs.addTab(debug_tab, debug_icon, "Debug")
        
        # Tab Settings com os botões de controle
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)
        settings_layout.setSpacing(20)
        settings_layout.setContentsMargins(20, 20, 20, 20)
        
        # Primeira linha de botões - settings específicos
        settings_first_row = QHBoxLayout()
        
        # Coluna esquerda
        settings_left_col1 = QHBoxLayout()
        settings_left_col1.addStretch()
        verify_state_btn = QPushButton("Verify State")
        verify_state_btn.setFixedSize(140, 40)
        verify_state_icon = self.create_text_icon("✓", 16, Qt.white)
        verify_state_btn.setIcon(verify_state_icon)
        verify_state_btn.setIconSize(QSize(16, 16))
        verify_state_btn.setStyleSheet("""
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
        verify_state_btn.clicked.connect(self.on_verify_state)
        settings_left_col1.addWidget(verify_state_btn)
        settings_left_col1.addStretch()
        
        # Coluna central
        settings_center_col1 = QHBoxLayout()
        settings_center_col1.addStretch()
        configure_debug_btn = QPushButton("Configure Debug")
        configure_debug_btn.setFixedSize(160, 40)
        configure_debug_icon = self.create_text_icon("⚙", 16, Qt.white)
        configure_debug_btn.setIcon(configure_debug_icon)
        configure_debug_btn.setIconSize(QSize(16, 16))
        configure_debug_btn.setStyleSheet("""
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
        configure_debug_btn.clicked.connect(self.on_configure_debug)
        settings_center_col1.addWidget(configure_debug_btn)
        settings_center_col1.addStretch()
        
        # Coluna direita
        settings_right_col1 = QHBoxLayout()
        settings_right_col1.addStretch()
        inject_ahbrom_btn = QPushButton("Inject AHBROM")
        inject_ahbrom_btn.setFixedSize(160, 40)
        inject_ahbrom_icon = self.create_text_icon("↑", 16, Qt.white)
        inject_ahbrom_btn.setIcon(inject_ahbrom_icon)
        inject_ahbrom_btn.setIconSize(QSize(16, 16))
        inject_ahbrom_btn.setStyleSheet("""
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
        inject_ahbrom_btn.clicked.connect(self.on_inject_ahbrom)
        settings_right_col1.addWidget(inject_ahbrom_btn)
        settings_right_col1.addStretch()
        
        # Adicionar as colunas ao layout principal
        settings_first_row.addLayout(settings_left_col1, 1)
        settings_first_row.addLayout(settings_center_col1, 1)
        settings_first_row.addLayout(settings_right_col1, 1)
        
        settings_layout.addLayout(settings_first_row)
        
        # Segunda linha de botões
        settings_second_row = QHBoxLayout()
        
        # Coluna esquerda
        settings_left_col2 = QHBoxLayout()
        settings_left_col2.addStretch()
        inject_elf_btn = QPushButton("Inject Elf")
        inject_elf_btn.setFixedSize(140, 40)
        inject_elf_icon = self.create_text_icon("↓", 16, Qt.white)
        inject_elf_btn.setIcon(inject_elf_icon)
        inject_elf_btn.setIconSize(QSize(16, 16))
        inject_elf_btn.setStyleSheet("""
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
        inject_elf_btn.clicked.connect(self.on_inject_elf)
        settings_left_col2.addWidget(inject_elf_btn)
        settings_left_col2.addStretch()
        
        # Coluna central com botões numerados
        settings_center_col2 = QHBoxLayout()
        settings_center_col2.addStretch()
        settings_numbers_layout = QHBoxLayout()
        settings_numbers_layout.setSpacing(10)
        
        for i in range(1, 4):
            settings_num_btn = QPushButton(str(i))
            settings_num_btn.setFixedSize(40, 40)
            settings_num_btn.setStyleSheet("""
                QPushButton {
                    background-color: #333333;
                    color: white;
                    border: none;
                    border-radius: 20px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #555555;
                }
            """)
            settings_numbers_layout.addWidget(settings_num_btn)
        
        settings_numbers_widget = QWidget()
        settings_numbers_widget.setLayout(settings_numbers_layout)
        settings_center_col2.addWidget(settings_numbers_widget)
        settings_center_col2.addStretch()
        
        # Coluna direita
        settings_right_col2 = QHBoxLayout()
        settings_right_col2.addStretch()
        configure_os_abi_btn = QPushButton("Configure OS ABI")
        configure_os_abi_btn.setFixedSize(160, 40)
        configure_os_abi_icon = self.create_text_icon("C", 16, Qt.white)
        configure_os_abi_btn.setIcon(configure_os_abi_icon)
        configure_os_abi_btn.setIconSize(QSize(16, 16))
        configure_os_abi_btn.setStyleSheet("""
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
        configure_os_abi_btn.clicked.connect(self.on_configure_os_abi)
        settings_right_col2.addWidget(configure_os_abi_btn)
        settings_right_col2.addStretch()
        
        # Adicionar as colunas ao layout principal
        settings_second_row.addLayout(settings_left_col2, 1)
        settings_second_row.addLayout(settings_center_col2, 1)
        settings_second_row.addLayout(settings_right_col2, 1)
        
        settings_layout.addLayout(settings_second_row)
        
        # Terceira linha com Configure RAM centralizado
        settings_third_row = QHBoxLayout()
        
        # Coluna esquerda vazia
        settings_left_col3 = QHBoxLayout()
        settings_left_col3.addStretch()
        
        # Coluna central com Configure RAM
        settings_center_col3 = QHBoxLayout()
        settings_center_col3.addStretch()
        configure_ram_btn = QPushButton("Configure RAM")
        configure_ram_btn.setFixedSize(160, 40)
        configure_ram_icon = self.create_text_icon("M", 16, Qt.white)
        configure_ram_btn.setIcon(configure_ram_icon)
        configure_ram_btn.setIconSize(QSize(16, 16))
        configure_ram_btn.setStyleSheet("""
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
        configure_ram_btn.clicked.connect(self.on_configure_ram)
        settings_center_col3.addWidget(configure_ram_btn)
        settings_center_col3.addStretch()
        
        # Coluna direita vazia
        settings_right_col3 = QHBoxLayout()
        settings_right_col3.addStretch()
        
        # Adicionar as colunas ao layout principal
        settings_third_row.addLayout(settings_left_col3, 1)
        settings_third_row.addLayout(settings_center_col3, 1)
        settings_third_row.addLayout(settings_right_col3, 1)
        
        settings_layout.addLayout(settings_third_row)
        
        # Input para Configure RAM - centralizado
        settings_input_row = QHBoxLayout()
        
        # Coluna esquerda vazia
        settings_left_input_col = QHBoxLayout()
        settings_left_input_col.addStretch()
        
        # Coluna central com input
        settings_center_input_col = QHBoxLayout()
        settings_center_input_col.addStretch()
        ram_value_input = QLineEdit()
        ram_value_input.setPlaceholderText("Put the RAM value")
        ram_value_input.setFixedSize(160, 30)
        self.ram_value_input = ram_value_input  # Armazenar referência
        settings_center_input_col.addWidget(ram_value_input)
        settings_center_input_col.addStretch()
        
        # Coluna direita vazia
        settings_right_input_col = QHBoxLayout()
        settings_right_input_col.addStretch()
        
        # Adicionar as colunas ao layout principal
        settings_input_row.addLayout(settings_left_input_col, 1)
        settings_input_row.addLayout(settings_center_input_col, 1)
        settings_input_row.addLayout(settings_right_input_col, 1)
        
        settings_layout.addLayout(settings_input_row)
        
        settings_layout.addStretch()  # Adicionar espaço flexível no final
        
        tabs.addTab(settings_tab, settings_icon, "Settings")
        
        tabs.setCurrentIndex(0)  # Emulation ativo
        
        return tabs
    
    def create_control_area(self):
        control_frame = QFrame()
        layout = QVBoxLayout(control_frame)
        layout.setSpacing(20)
        
        # Primeira linha de botões - alinhados
        first_row = QHBoxLayout()
        first_row.setSpacing(80)  # Espaçamento uniforme entre botões
        
        # Pause Emulation
        pause_btn = QPushButton("Pause Emulation")
        pause_btn.setFixedSize(180, 40)
        pause_btn.setStyleSheet("""
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
        first_row.addWidget(pause_btn)
        
        # Unpause Emulation
        unpause_btn = QPushButton("Unpause Emulation")
        unpause_btn.setFixedSize(180, 40)
        unpause_btn.setStyleSheet("""
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
        first_row.addWidget(unpause_btn)
        
        # Read I/O
        read_btn = QPushButton("Read I/O")
        read_btn.setFixedSize(140, 40)
        read_btn.setStyleSheet("""
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
        first_row.addWidget(read_btn)
        
        first_row.addStretch()
        layout.addLayout(first_row)
        
        # Segunda linha de botões - alinhados
        second_row = QHBoxLayout()
        second_row.setSpacing(80)  # Mesmo espaçamento da primeira linha
        
        # Stop Emulation
        stop_btn = QPushButton("Stop Emulation")
        stop_btn.setFixedSize(180, 40)
        stop_btn.setStyleSheet("""
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
        second_row.addWidget(stop_btn)
        
        # Start Emulation
        start_btn = QPushButton("Start Emulation")
        start_btn.setFixedSize(180, 40)
        start_btn.setStyleSheet("""
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
        second_row.addWidget(start_btn)
        
        # Write I/O
        write_btn = QPushButton("Write I/O")
        write_btn.setFixedSize(140, 40)
        write_btn.setStyleSheet("""
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
        second_row.addWidget(write_btn)
        
        second_row.addStretch()
        layout.addLayout(second_row)
        
        # Terceira linha com as caixas de texto alinhadas aos botões
        inputs_row = QHBoxLayout()
        inputs_row.setSpacing(80)  # Mesmo espaçamento dos botões
        
        # Espaço vazio para alinhar com pause/stop
        inputs_row.addWidget(QWidget())
        inputs_row.addWidget(QWidget())
        
        # Container para as caixas de texto
        inputs_container = QVBoxLayout()
        inputs_container.setSpacing(10)
        
        # Input para Read I/O
        addr_input = QLineEdit()
        addr_input.setPlaceholderText("Escreva o ADDR em hex:")
        addr_input.setFixedSize(140, 30)
        inputs_container.addWidget(addr_input)
        
        # Input para Write I/O
        val_input = QLineEdit()
        val_input.setPlaceholderText("Escreva o ADDR/VAL em hex:")
        val_input.setFixedSize(140, 30)
        inputs_container.addWidget(val_input)
        
        # Widget para conter os inputs
        inputs_widget = QWidget()
        inputs_widget.setLayout(inputs_container)
        inputs_row.addWidget(inputs_widget)
        
        inputs_row.addStretch()
        layout.addLayout(inputs_row)
        
        return control_frame
    
    def create_logs_area(self):
        logs_frame = QFrame()
        layout = QVBoxLayout(logs_frame)
        
        # Título
        title = QLabel("Systems Logs:")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title)
        
        # Área de logs
        logs_text = QTextEdit()
        logs_text.setMinimumHeight(200)
        logs_text.setReadOnly(True)  # Torna a caixa de texto somente leitura
        logs_text.setStyleSheet("""
            QTextEdit {
                background-color: #e5e5e5;
                border: 1px solid #cccccc;
                border-radius: 8px;
                padding: 10px;
                font-family: monospace;
                font-size: 10px;
            }
        """)
        logs_text.setPlaceholderText("System logs will appear here...")
        self.logs_text = logs_text  # Armazenar referência
        layout.addWidget(logs_text)
        
        return logs_frame
    
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
        """)

def main():
    app = QApplication(sys.argv)
    
    # Configurar tema
    app.setStyle('Fusion')
    
    window = QemulaApp()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()