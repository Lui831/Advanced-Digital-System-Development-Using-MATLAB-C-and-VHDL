# Esse código deve comunicar com uma interface de controle de baixo nivel na porta TCP/IP 4545
# O código deve ser capaz de enviar e receber pacotes de dados e repassar para o cliente na 4322 normalmente

import socket
import threading
import time

class LowLevelInterface:
    """
    Classe para gerenciar a comunicação com a interface de controle de baixo nível na porta TCP/IP 4545.
    Envia e recebe pacotes de dados e repassa para o cliente na porta 4322.
    """

    def __init__(self, low_level_host="localhost", low_level_port=4545):
        """
        Inicializa a classe com os endereços e portas do servidor de baixo nível e do cliente.

        :param low_level_host: Endereço do servidor de baixo nível (default: localhost).
        :param low_level_port: Porta do servidor de baixo nível (default: 4545).
        :param client_host: Endereço do cliente (default: localhost).
        :param client_port: Porta do cliente (default: 4322).
        """
        self.low_level_host = low_level_host
        self.low_level_port = low_level_port

        self.low_level_socket = None
        self.running = True

        # Lock para proteger o envio de dados
        self.lock = threading.Lock()

        # Inicia as threads de comunicação
        self.start_threads()
        # Conecta ao servidor de baixo nível
        self.connect_low_level()

    def connect_low_level(self):
        """
        Conecta ao servidor de baixo nível na porta 4545.
        """
        while True:
            try:
                self.low_level_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.low_level_socket.connect((self.low_level_host, self.low_level_port))
                print(f"Conectado ao servidor de baixo nível em {self.low_level_host}:{self.low_level_port}")
                break
            except (ConnectionRefusedError, socket.error):
                print("Falha ao conectar ao servidor de baixo nível. Tentando novamente em 5 segundos...")
                time.sleep(5)

    def start_threads(self):
        """
        Inicia as threads para gerenciar a comunicação com o servidor de baixo nível e o cliente.
        """
        threading.Thread(target=self.handle_low_level_communication, daemon=True).start()

    def handle_low_level_communication(self):
        """
        Gerencia a comunicação com o servidor de baixo nível.
        """
        self.connect_low_level()
        while self.running:
            try:
                data = self.low_level_socket.recv(1024)
                if data:
                    print(f"Recebido do servidor de baixo nível: {data}")
                    self.send_to_client(data)
            except (socket.error, ConnectionResetError):
                print("Conexão com o servidor de baixo nível perdida. Reconectando...")
                self.connect_low_level()

    def send_to_low_level(self, data):
        """
        Envia dados para o servidor de baixo nível.

        :param data: Dados a serem enviados.
        """
        with self.lock:
            try:
                self.low_level_socket.sendall(data)
                print(f"Enviado para o servidor de baixo nível: {data}")
            except (socket.error, ConnectionResetError):
                print("Erro ao enviar dados para o servidor de baixo nível. Reconectando...")
                self.connect_low_level()

    def stop(self):
        """
        Para a execução da interface e fecha as conexões.
        """
        self.running = False
        if self.low_level_socket:
            self.low_level_socket.close()
        if self.client_socket:
            self.client_socket.close()
        print("Interface de baixo nível encerrada.")


# Exemplo de uso
if __name__ == "__main__":
    interface = LowLevelInterface()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        interface.stop()