from PySide6.QtCore import QObject, Signal
import socket
import threading
import time

class SpaceWireReceiver(QObject):
    message_received = Signal(str)
    connection_established = Signal()
    connection_failed = Signal(str)

    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.running = False
        self.socket = None
        self.buffer = ""  # Buffer para acumular dados recebidos
        self.connected = False

    def start(self):
        self.running = True
        threading.Thread(target=self._run, daemon=True).start()

    def stop(self):
        self.running = False
        self.connected = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None

    def _run(self):
        while self.running:
            try:
                # Criar socket TCP
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5.0)  # Timeout de 5 segundos para conexão
                self.socket = sock
                
                self.message_received.emit("[INFO] Trying to connect...")
                
                # Tentar conectar
                sock.connect((self.host, self.port))
                self.connected = True
                self.connection_established.emit()
                self.message_received.emit(f"[INFO] Connected to {self.host}:{self.port}")
                
                # Loop de recepção de dados
                sock.settimeout(1.0)  # Timeout menor para recv
                while self.running and self.connected:
                    try:
                        # Recebe dados como string
                        data = sock.recv(1024)
                        if data:
                            # Decodifica os dados recebidos
                            decoded_data = data.decode('utf-8', errors='ignore')
                            self.buffer += decoded_data
                            
                            # Processa linhas completas
                            while '\n' in self.buffer:
                                line, self.buffer = self.buffer.split('\n', 1)
                                if line.strip():  # Só emite se a linha não estiver vazia
                                    clean_line = line.rstrip('\r')
                                    self.message_received.emit(f"[RX] {clean_line}")
                            
                            # Se não há quebras de linha mas há dados, emite após um pequeno delay
                            if self.buffer and '\n' not in self.buffer:
                                time.sleep(0.1)  # Pequeno delay para acumular mais dados
                                if self.buffer and len(self.buffer) > 50:  # Se buffer cresceu muito
                                    clean_buffer = self.buffer.rstrip('\r\n')
                                    self.message_received.emit(f"[RX] {clean_buffer}")
                                    self.buffer = ""
                        else:
                            # Conexão foi fechada pelo servidor
                            break
                            
                    except socket.timeout:
                        # Timeout normal, continua o loop
                        continue
                    except (socket.error, Exception) as e:
                        self.message_received.emit(f"[ERROR] Receive error: {str(e)}")
                        break
                        
            except socket.timeout:
                self.connection_failed.emit("Connection timeout")
                self.message_received.emit("[ERROR] Connection timeout")
            except socket.error as e:
                error_msg = f"Socket error: {str(e)}"
                self.connection_failed.emit(error_msg)
                self.message_received.emit(f"[ERROR] {error_msg}")
            except Exception as e:
                error_msg = f"Unexpected error: {str(e)}"
                self.connection_failed.emit(error_msg)
                self.message_received.emit(f"[ERROR] {error_msg}")
            finally:
                # Limpar recursos
                self.connected = False
                if self.socket:
                    try:
                        self.socket.close()
                    except:
                        pass
                    self.socket = None
                self.buffer = ""  # Limpa o buffer
                
                # Se ainda está rodando, tentar reconectar
                if self.running:
                    self.message_received.emit("[INFO] Reconnecting in 5 seconds...")
                    for i in range(50):  # 5 segundos = 50 * 0.1s
                        if not self.running:
                            break
                        time.sleep(0.1)

    def send_data(self, data):
        """
        Sends data to the connected server as string.
        :param data: A string containing the data to send.
        """
        if self.socket and self.running and self.connected:
            try:
                # Adicionar quebra de linha se não houver
                if not data.endswith('\n'):
                    data += '\n'
                    
                # Envia a string como bytes usando UTF-8
                self.socket.sendall(data.encode('utf-8'))
                self.message_received.emit(f"[TX] {data.rstrip()}")
                return True
            except (socket.error, Exception) as e:
                self.message_received.emit(f"[ERROR] Failed to send data: {str(e)}")
                self.connected = False
                return False
        else:
            self.message_received.emit("[ERROR] Not connected to the server.")
            return False