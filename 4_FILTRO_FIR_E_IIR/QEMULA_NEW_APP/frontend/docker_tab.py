import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QTextEdit, 
                             QFrame, QLineEdit, QSplitter, QListWidget, QTabWidget,
                             QListWidgetItem, QCheckBox, QScrollArea, QSlider)
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QFont, QPalette, QColor, QIcon, QPainter, QPen, QBrush

# Importar o backend para gerenciamento Docker
from backend.docker import DockerManager

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

class QemulaDockerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QEMULA APP - Interface Podman")
        self.setGeometry(100, 100, 1400, 800)
        
        # Inicializar gerenciador Docker/Podman backend
        self.docker_manager = DockerManager()  # Agora sempre funciona (modo demo se necessário)
        self.images_data = []  # Armazenar dados das imagens
        
        # Flag para controlar se é a primeira inicialização
        self.is_initializing = True
        
        self.setup_ui()
        self.apply_styles()
        
        # Marcar como inicialização completa
        self.is_initializing = False
    
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
            ("Docker", True),  # Item ativo
            ("Control", False),
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

        # Conteúdo principal - dividido em duas colunas
        content_layout = QHBoxLayout()
        
        # Coluna esquerda - Images in the machine
        left_column = self.create_images_section()
        content_layout.addWidget(left_column, 1)
        
        # Coluna direita - System logs
        right_column = self.create_logs_section()
        content_layout.addWidget(right_column, 1)
        
        layout.addLayout(content_layout)
        
        # Carregar imagens após todos os widgets serem criados
        self.load_images()

        return main_widget
    
    def create_header(self):
        from PySide6.QtGui import QPixmap
        header = QFrame()
        layout = QHBoxLayout(header)
        
        # Título da interface
        title = QLabel("Interface Podman")
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
    
    def create_images_section(self):
        # Frame principal para a seção de imagens
        images_frame = QFrame()
        images_frame.setFrameStyle(QFrame.Box)
        layout = QVBoxLayout(images_frame)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Título da seção
        title = QLabel("Images in the machine")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title)
        
        # Barra de pesquisa
        search_layout = QHBoxLayout()
        
        # Ícone de menu (três linhas)
        menu_icon = QLabel("☰")
        menu_icon.setFont(QFont("Arial", 14))
        menu_icon.setFixedSize(30, 30)
        menu_icon.setAlignment(Qt.AlignCenter)
        search_layout.addWidget(menu_icon)
        
        # Campo de pesquisa
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search your image")
        self.search_input.setFixedHeight(35)
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 5px 10px;
                font-size: 12px;
            }
        """)
        self.search_input.textChanged.connect(self.filter_images)
        search_layout.addWidget(self.search_input)
        
        # Ícone de pesquisa
        search_icon = QLabel("🔍")
        search_icon.setFont(QFont("Arial", 14))
        search_icon.setFixedSize(30, 30)
        search_icon.setAlignment(Qt.AlignCenter)
        search_layout.addWidget(search_icon)
        
        layout.addLayout(search_layout)
        
        # Lista de imagens
        self.images_list_widget = self.create_images_list()
        layout.addWidget(self.images_list_widget)
        
        # Botão para atualizar lista
        refresh_button = QPushButton("🔄 Refresh Images")
        refresh_button.setFixedHeight(35)
        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        refresh_button.clicked.connect(self.load_images)
        layout.addWidget(refresh_button)
        
        # Campo para especificar o arquivo docker-compose.yml
        compose_layout = QHBoxLayout()
        compose_label = QLabel("Docker Compose File:")
        compose_label.setFont(QFont("Arial", 10))
        compose_layout.addWidget(compose_label)
        
        self.compose_file_input = QLineEdit()
        self.compose_file_input.setPlaceholderText("docker-compose.yml")
        self.compose_file_input.setText("docker-compose.yml")  # Valor padrão
        self.compose_file_input.setFixedHeight(30)
        self.compose_file_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 5px 10px;
                font-size: 11px;
            }
        """)
        compose_layout.addWidget(self.compose_file_input)
        
        browse_button = QPushButton("📁")
        browse_button.setFixedSize(30, 30)
        browse_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        browse_button.clicked.connect(self.browse_compose_file)
        compose_layout.addWidget(browse_button)
        
        layout.addLayout(compose_layout)
        
        # Toggle switch para "Start the container select"
        toggle_layout = QHBoxLayout()
        
        toggle_label = QLabel("Start the container select")
        toggle_label.setFont(QFont("Arial", 12))
        toggle_layout.addWidget(toggle_label)
        
        toggle_layout.addStretch()
        
        # Usar o switch personalizado
        self.toggle_switch = ToggleSwitch()
        self.toggle_switch.toggled.connect(self.on_toggle_changed)
        toggle_layout.addWidget(self.toggle_switch)
        
        layout.addLayout(toggle_layout)
        
        return images_frame
    
    def on_toggle_changed(self, checked):
        """Callback para quando o switch é alterado"""
        # Evitar auto-start durante a inicialização da aplicação
        if hasattr(self, 'is_initializing') and self.is_initializing:
            return
        
        if checked:
            self.add_log("Container auto-start enabled")
            
            # Verificar se já existem containers rodando antes de tentar fazer compose up
            try:
                compose_file_path = self.get_compose_file_path()
                self.add_log(f"Checking existing containers for: {compose_file_path}")
                
                # Primeiro, verificar se há containers em execução
                check_result = self.docker_manager.check_compose_containers(compose_file_path)
                
                if check_result and "running" in check_result:
                    self.add_log("⚠️ Containers already running, performing cleanup first...")
                    self.add_log("Stopping existing containers...")
                    
                    # Fazer compose down primeiro
                    down_result = self.docker_manager.docker_compose_down(compose_file_path)
                    if "success" in down_result:
                        self.add_log("✅ Existing containers stopped successfully")
                        if down_result['success'].strip():
                            self.add_log(f"Output: {down_result['success']}")
                    elif "error" in down_result:
                        self.add_log(f"⚠️ Warning during container cleanup: {down_result['error']}")
                    
                    # Pequena pausa para garantir que os containers foram parados
                    from PySide6.QtCore import QTimer
                    QTimer.singleShot(1000, lambda: self._start_compose_up(compose_file_path))
                    return
                
            except Exception as e:
                self.add_log(f"⚠️ Warning checking existing containers: {str(e)}")
            
            # Se não há containers rodando, proceder normalmente
            self._start_compose_up(compose_file_path)
        else:
            self.add_log("Container auto-start disabled")
            self.add_log("Stopping docker-compose down...")
            
            # Executar docker_compose_down
            try:
                compose_file_path = self.get_compose_file_path()
                self.add_log(f"Using compose file: {compose_file_path}")
                
                result = self.docker_manager.docker_compose_down(compose_file_path)
                
                if "success" in result:
                    self.add_log("✅ Docker compose down executed successfully")
                    if result['success'].strip():
                        self.add_log(f"Output: {result['success']}")
                elif "error" in result:
                    self.add_log(f"❌ Error executing docker compose down: {result['error']}")
                
            except Exception as e:
                self.add_log(f"❌ Exception executing docker compose down: {str(e)}")
        
        status = "enabled" if checked else "disabled"
        print(f"Container start is {status}")
    
    def _start_compose_up(self, compose_file_path):
        """Método auxiliar para iniciar compose up"""
        # Verificar se o arquivo compose existe
        import os
        if not os.path.exists(compose_file_path):
            self.add_log(f"❌ Docker compose file not found: {compose_file_path}")
            self.add_log("Please select a valid docker-compose.yml file first")
            self.toggle_switch.setChecked(False)
            return
        
        self.add_log("Starting docker-compose up...")
        self.add_log(f"Using compose file: {compose_file_path}")
        
        try:
            result = self.docker_manager.docker_compose_up(compose_file_path)
            
            if "success" in result:
                self.add_log("✅ Docker compose up executed successfully")
                if result['success'].strip():
                    self.add_log(f"Output: {result['success']}")
            elif "error" in result:
                error_msg = result['error']
                self.add_log(f"❌ Error executing docker compose up: {error_msg}")
                
                # Se ainda houver erro de nome já em uso, tentar cleanup mais agressivo
                if "already in use" in error_msg.lower():
                    self.add_log("🔄 Container name conflict detected, attempting forced cleanup...")
                    self._handle_container_conflict(compose_file_path)
                else:
                    # Desmarcar o switch em caso de erro não relacionado a conflito
                    self.toggle_switch.setChecked(False)
                    return
            
        except Exception as e:
            self.add_log(f"❌ Exception executing docker compose up: {str(e)}")
            # Desmarcar o switch em caso de erro
            self.toggle_switch.setChecked(False)
            return
        
        # Aqui você pode adicionar lógica para iniciar containers selecionados
        selected_images = self.get_selected_images()
        if selected_images:
            self.add_log(f"Auto-start enabled for {len(selected_images)} images")
            for img in selected_images:
                repo = img.get('repository', 'Unknown')
                tag = img.get('tag', 'latest')
                self.add_log(f"  - {repo}:{tag}")
        else:
            self.add_log("No images selected for auto-start")
    
    def _handle_container_conflict(self, compose_file_path):
        """Lidar com conflitos de nomes de containers"""
        self.add_log("Performing forced container cleanup...")
        
        try:
            # Tentar compose down com force
            down_result = self.docker_manager.docker_compose_down_force(compose_file_path)
            if "success" in down_result:
                self.add_log("✅ Forced cleanup completed successfully")
                
                # Tentar compose up novamente após cleanup
                from PySide6.QtCore import QTimer
                QTimer.singleShot(2000, lambda: self._start_compose_up(compose_file_path))
            else:
                self.add_log("❌ Forced cleanup failed")
                self.toggle_switch.setChecked(False)
                
        except Exception as e:
            self.add_log(f"❌ Exception during forced cleanup: {str(e)}")
            self.toggle_switch.setChecked(False)
    
    def get_selected_images(self):
        """Obter lista de imagens selecionadas"""
        # Esta é uma implementação simplificada
        # Em uma implementação real, você manteria track dos checkboxes selecionados
        return self.images_data  # Por agora, retorna todas as imagens
    
    def create_images_list(self):
        # Criar uma lista com checkboxes
        scroll_area = QScrollArea()
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setSpacing(3)
        self.scroll_layout.setContentsMargins(5, 5, 5, 5)
        
        # NÃO carregar imagens aqui - será feito depois que logs_text for criado
        
        # Adicionar espaço no final para evitar cortes
        self.scroll_layout.addStretch()
        
        self.scroll_widget.setLayout(self.scroll_layout)
        scroll_area.setWidget(self.scroll_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(400)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: white;
            }
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a0a0a0;
            }
        """)
        
        return scroll_area
    
    def load_images(self):
        """Carregar imagens do backend Podman"""
        try:
            # Limpar lista atual
            self.clear_images_list()
            
            # Obter imagens do backend
            images_result = self.docker_manager.list_images()
            
            # Armazenar dados das imagens
            self.images_data = images_result if isinstance(images_result, list) else []
            
            # Atualizar a interface
            self.update_images_display()
            
            # Log informativo
            engine = getattr(self.docker_manager, 'container_engine', 'unknown')
            if engine == "demo":
                self.add_log(f"Loaded {len(self.images_data)} example images (demo mode)")
            else:
                self.add_log(f"Loaded {len(self.images_data)} images from {engine}")
            
        except Exception as e:
            self.add_error_message(f"Exception loading images: {str(e)}")
            self.add_log(f"Error loading images: {str(e)}")
    
    def clear_images_list(self):
        """Limpar todos os itens da lista de imagens"""
        while self.scroll_layout.count() > 1:  # Manter o stretch no final
            child = self.scroll_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def update_images_display(self, filter_text=""):
        """Atualizar a exibição das imagens com filtro opcional"""
        self.clear_images_list()
        
        if not self.images_data:
            self.add_info_message("No images found")
            return
        
        # Filtrar imagens se necessário
        filtered_images = self.images_data
        if filter_text:
            filtered_images = [
                img for img in self.images_data 
                if filter_text.lower() in img.get('repository', '').lower() or 
                   filter_text.lower() in img.get('tag', '').lower()
            ]
        
        # Criar itens para cada imagem
        for image in filtered_images:
            self.create_image_item(image)
    
    def create_image_item(self, image_data):
        """Criar um item da lista para uma imagem"""
        item_layout = QHBoxLayout()
        item_layout.setContentsMargins(10, 5, 10, 5)
        
        # Layout vertical para informações da imagem
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        
        # Nome da imagem (repository:tag)
        repo = image_data.get('repository', 'Unknown')
        tag = image_data.get('tag', 'latest')
        image_name = f"{repo}:{tag}" if repo != '<none>' else f"<none>:{tag}"
        
        name_label = QLabel(image_name)
        name_label.setFont(QFont("Arial", 11, QFont.Bold))
        info_layout.addWidget(name_label)
        
        # Informações adicionais (ID e tamanho)
        image_id = image_data.get('id', 'Unknown')[:12]  # Mostrar apenas os primeiros 12 caracteres
        size = image_data.get('size', 'Unknown')
        details_label = QLabel(f"ID: {image_id} | Size: {size}")
        details_label.setFont(QFont("Arial", 9))
        details_label.setStyleSheet("color: #666666;")
        info_layout.addWidget(details_label)
        
        item_layout.addLayout(info_layout)
        item_layout.addStretch()
        
        # Checkbox
        checkbox = QCheckBox()
        checkbox.setChecked(True)
        checkbox.setFixedSize(20, 20)
        checkbox.setStyleSheet("""
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 2px;
            }
            QCheckBox::indicator:checked {
                background-color: #333333;
                border: 1px solid #333333;
            }
            QCheckBox::indicator:unchecked {
                background-color: white;
                border: 1px solid #cccccc;
            }
        """)
        # Conectar checkbox à imagem
        checkbox.toggled.connect(lambda checked, img=image_data: self.on_image_selected(img, checked))
        item_layout.addWidget(checkbox)
        
        # Widget para conter o layout do item
        item_widget = QWidget()
        item_widget.setLayout(item_layout)
        item_widget.setFixedHeight(50)  # Altura maior para acomodar duas linhas
        item_widget.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                margin: 1px;
            }
            QWidget:hover {
                background-color: #e9ecef;
            }
        """)
        
        # Inserir antes do stretch
        self.scroll_layout.insertWidget(self.scroll_layout.count() - 1, item_widget)
    
    def add_error_message(self, message):
        """Adicionar mensagem de erro à lista"""
        error_label = QLabel(f"❌ {message}")
        error_label.setFont(QFont("Arial", 11))
        error_label.setStyleSheet("color: #dc3545; padding: 10px;")
        error_label.setAlignment(Qt.AlignCenter)
        self.scroll_layout.insertWidget(self.scroll_layout.count() - 1, error_label)
    
    def add_info_message(self, message):
        """Adicionar mensagem informativa à lista"""
        info_label = QLabel(f"ℹ️ {message}")
        info_label.setFont(QFont("Arial", 11))
        info_label.setStyleSheet("color: #6c757d; padding: 10px;")
        info_label.setAlignment(Qt.AlignCenter)
        self.scroll_layout.insertWidget(self.scroll_layout.count() - 1, info_label)
    
    def filter_images(self, text):
        """Filtrar imagens baseado no texto de pesquisa"""
        self.update_images_display(text)
    
    def on_image_selected(self, image_data, checked):
        """Callback quando uma imagem é selecionada/desmarcada"""
        repo = image_data.get('repository', 'Unknown')
        tag = image_data.get('tag', 'latest')
        status = "selected" if checked else "deselected"
        print(f"Image {repo}:{tag} {status}")
        # Aqui você pode implementar lógica adicional para imagens selecionadas
    
    def browse_compose_file(self):
        """Abrir dialog para selecionar arquivo docker-compose.yml"""
        from PySide6.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Docker Compose File",
            "",
            "YAML files (*.yml *.yaml);;All files (*.*)"
        )
        
        if file_path:
            self.compose_file_input.setText(file_path)
            self.add_log(f"Docker compose file selected: {file_path}")
    
    def get_compose_file_path(self):
        """Obter o caminho do arquivo docker-compose especificado"""
        return self.compose_file_input.text().strip() or "docker-compose.yml"
    
    def create_logs_section(self):
        # Frame principal para a seção de logs
        logs_frame = QFrame()
        logs_frame.setFrameStyle(QFrame.Box)
        layout = QVBoxLayout(logs_frame)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Título da seção
        title = QLabel("Systems Logs")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title)
        
        # Área de logs
        self.logs_text = QTextEdit()
        self.logs_text.setReadOnly(True)
        self.logs_text.setStyleSheet("""
            QTextEdit {
                background-color: #2d3748;
                color: #e2e8f0;
                border: 1px solid #4a5568;
                border-radius: 8px;
                padding: 10px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
            }
        """)
        self.logs_text.setPlaceholderText("System logs will appear here...")
        
        # Adicionar log inicial
        self.add_log("System initialized")
        engine = getattr(self.docker_manager, 'container_engine', 'unknown')
        if engine == "demo":
            self.add_log("Running in demo mode - example data will be shown")
        else:
            self.add_log(f"{engine.title()} backend connected successfully")
        
        layout.addWidget(self.logs_text)
        
        # Botão para limpar logs
        clear_logs_button = QPushButton("🗑️ Clear Logs")
        clear_logs_button.setFixedHeight(30)
        clear_logs_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        clear_logs_button.clicked.connect(self.clear_logs)
        layout.addWidget(clear_logs_button)
        
        return logs_frame
    
    def add_log(self, message):
        """Adicionar uma mensagem ao log"""
        # Verificar se logs_text existe (proteção contra inicialização prematura)
        if not hasattr(self, 'logs_text') or self.logs_text is None:
            print(f"[LOG] {message}")  # Fallback para console
            return
            
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.logs_text.append(f"[{timestamp}] {message}")
    
    def clear_logs(self):
        """Limpar todos os logs"""
        self.logs_text.clear()
        self.add_log("Logs cleared")
    
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
    
    window = QemulaDockerApp()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
