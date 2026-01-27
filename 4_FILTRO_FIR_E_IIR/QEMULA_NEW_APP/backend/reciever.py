from PySide6.QtCore import QObject, Signal
import socket
import struct
import threading
import time

def decode_word(word_16bit):
    id_field = (word_16bit >> 8) & 0xFF
    channel_id = (id_field >> 4) & 0x0F
    packet_id = id_field & 0x0F
    data = word_16bit & 0xFF
    return channel_id, packet_id, data

class SpaceWireReceiver(QObject):
    message_received = Signal(str)

    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.running = False
        self.current_packet = []  # Lista para armazenar os dados do pacote atual
        self.socket = None

    def start(self):
        self.running = True
        threading.Thread(target=self._run, daemon=True).start()

    def stop(self):
        self.running = False
        if self.socket:
            self.socket.close()

    def _run(self):
        while self.running:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    self.socket = sock
                    sock.settimeout(5)  # Timeout de 5 segundos
                    self.message_received.emit("[Trying to connect...]")
                    sock.connect((self.host, self.port))
                    self.message_received.emit("[Connected]")
                    
                    while self.running:
                        try:
                            data = sock.recv(1024)  # Receber até 1024 bytes
                            if len(data) == 0:
                                self.message_received.emit("[Connection closed by server]")
                                break
                            
                            # Processar como dados binários SPW em formato hexadecimal limpo
                            if len(data) >= 2:
                                # Processar em chunks de 2 bytes
                                for i in range(0, len(data), 2):
                                    if i + 1 < len(data):
                                        word_16bit = int.from_bytes(data[i:i+2], byteorder='big')
                                        channel_id, packet_id, packet_data = decode_word(word_16bit)
                                        
                                        # Adiciona o dado ao pacote atual
                                        if packet_id == 0x0:  # Data packet
                                            self.current_packet.append(f"{packet_data:02X}")
                                        elif packet_id == 0x1:  # EOP/EEP
                                            # Adiciona EEP ao final do pacote e exibe a linha completa
                                            if packet_data == 0x00:
                                                self.current_packet.append("EOP")
                                            else:
                                                self.current_packet.append(f"EEP")
                                                
                                            packet_line = " ".join(self.current_packet)
                                            self.message_received.emit(f"[Channel {channel_id}] {packet_line}")
                                            self.current_packet = []  # Limpa o pacote para o próximo
                                        else:
                                            # Para outros tipos de pacote, adicionar dados em hex
                                            self.current_packet.append(f"{packet_data:02X}")
                            else:
                                # Para dados menores que 2 bytes, adicionar ao pacote atual
                                for byte in data:
                                    self.current_packet.append(f"{byte:02X}")
                        
                        except socket.timeout:
                            continue  # Timeout é normal, continuar
                        except Exception as e:
                            self.message_received.emit(f"[Error processing data] {str(e)}")
                            continue
                        
            except (socket.error, Exception) as e:
                self.message_received.emit(f"[Error] {str(e)}")
                self.message_received.emit("[Reconnecting in 5 seconds...]")
                self.socket = None
                self.current_packet = []  # Limpa o pacote em caso de erro
                threading.Event().wait(5)

    def send_data(self, data):
        """
        Sends data to the connected server.
        :param data: A bytes object containing the data to send.
        """
        if self.socket and self.running:
            try:
                self.socket.sendall(hex_string_to_bytes(data))
                self.message_received.emit(f"[Data sent] {data}")
            except (socket.error, Exception) as e:
                self.message_received.emit(f"[Error sending data] {str(e)}")
        else:
            self.message_received.emit("[Error] Not connected to the server.")

def hex_string_to_bytes(hex_string):
    # Remove espaços e converte para bytes
    try:
        return bytes.fromhex(hex_string)
    except ValueError as e:
        print(f"Erro de conversão: {e}")
        return None