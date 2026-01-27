import threading
import time
import leitor_dados as ld
import respostas_dados as rd
import socket
from collections import deque
from client_qemu import QemuEmulator as QE
import time
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class Interface:
    """
    Classe responsável pela interface de comunicação, recebimento de pacotes e processamento de dados
    entre um cliente e um servidor através de sockets. Implementa mecanismos de fila e threads para leitura
    e escrita de dados de maneira concorrente.

    Atributos:
    ----------
    fifo : deque
        Fila baseada em RAM para armazenar pacotes temporariamente.
    read_client : reciever_client
        Cliente responsável por processar pacotes recebidos.
    write_client : sender_client
        Cliente responsável por construir pacotes de resposta.
    FIFO_file : str
        Nome do arquivo FIFO utilizado como buffer baseado em disco.
    conn : socket.socket
        Objeto de conexão do socket.
    lock_socket : threading.Lock
        Lock para proteger o acesso ao socket em ambiente multithread.
    lock_fifo : threading.Lock
        Lock para proteger o acesso à fila de pacotes.
    thread1 : threading.Thread
        Thread responsável pela recepção dos pacotes.
    thread2 : threading.Thread
        Thread responsável pela leitura e processamento dos pacotes da fila.
    """

    def __init__(self, host, port):
        """
        Inicializa o objeto Interface, configurando a fila, o socket, os locks e as threads.

        Parâmetros:
        -----------
        host : str
            Endereço IP do host no qual o servidor será iniciado.
        port : int
            Porta na qual o servidor escutará as conexões.
        """
        # Inicializa a fila baseada em RAM
        self.fifo = deque()
        self.read_client = ld.reciever_client()
        self.write_client = rd.sender_client()
        self.client_qemu = QE()
        self.qemula_addr = (host, port)

        # Inicializa a fila baseada em arquivo
        self.FIFO_file = "FIFO"
        open(self.FIFO_file, "wb").close()

        # Inicializa o socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        s.bind((host, port))
        s.listen(1)
        print(f"Listening on {self.qemula_addr[0]}:{self.qemula_addr[1]}...")
        self.conn, addr = s.accept()
        self.conn.setblocking(0)
        print(f"Connected by {addr}")

        # Inicializa o lock do socket
        self.lock_socket = threading.Lock()

        # Inicializa o lock da fila
        self.lock_fifo = threading.Lock()

        # Inicializa as threads
        self.thread1 = threading.Thread(target=self.receiver)
        self.thread1.start()

        self.thread2 = threading.Thread(target=self.reader)
        self.thread2.start()

    # Internal function for socket restart
    def __restart_socket(self):

        # Closes the connection
        self.conn.close()

        # Inicializa o socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(self.qemula_addr)
        s.listen(1)
        print(f"Listening on {self.qemula_addr[0]}:{self.qemula_addr[1]}...")
        self.conn, addr = s.accept()
        self.conn.setblocking(0)
        print(f"Connected by {addr}")

        # Receives all the remaining packets
        self.conn.recv(self.conn.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF))


    def reader(self):
        """
        Thread responsável por ler pacotes da fila RAM, processá-los usando o cliente leitor e enviar
        as respostas de volta através do socket.
        """
        while True:

            if not len(self.fifo) == 0:

                with self.lock_fifo:

                    # Obtém o próximo pacote da fila quando o QEMU esta no estado 0x00 (config)
                    packet = self.fifo.popleft()
                    body_size = int.from_bytes(packet[7:11], byteorder='big')
                    fifo = open(self.FIFO_file, "rb+")
                    body_content = fifo.read(body_size)
                    fifo.seek(0)
                    fifo.truncate()
                    fifo.close()
                
                # Processa o pacote
                result = self.read_client.process_packet(packet, body_content)
                #print(result, "\n")
                # Constrói o pacote de resposta
                self.write_client.construct_packet(result)
                packet = self.write_client.get_packet()
                #print(f"Packet sent: {bytearray(packet)}")
 
                # Trava a utilização do socket
                with self.lock_socket:

                    while True:
                        try:
                            self.conn.sendall(packet)
                            break
                        except:
                            continue

    # Inicializa a thread de recebimento de dados
    def receiver(self):

        # Obtem o buffer size
        buffer_size = self.conn.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)

        # Estipula um fator de redução do buffer_size em 2x (pode ser verificada uma possibilidade de otimização do size), para segurança
        buffer_size = buffer_size // 2

        # Realiza o recebimento
        while True:

            time.sleep(0.001)

            # Trava o socket de controle
            with self.lock_socket:

                # Try except para evitar erros de leitura quando o buffer está vazio
                try:

                    # Recebe o header do pacote
                    pkg_header = self.conn.recv(7)

                    # Recebe o body_size do pacote
                    pkg_body_size = self.conn.recv(4)

                    if len(pkg_header) == 0 and len(pkg_body_size) == 0:

                        # Restart the socket
                        self.__restart_socket()
                        
                except ConnectionResetError or ConnectionAbortedError:

                    # Restart the socket
                    self.__restart_socket()

                except:

                    continue

            # Desconstroi o pkg_body_size em BODY_SIZE
            BODY_SIZE = int.from_bytes(pkg_body_size, byteorder='big')

            # Mostra o número de bytes lidos até então
            bytes_read = 0

            # Recebe o body do pacote, armazenando-o na FIFO
            with self.lock_socket and self.lock_fifo:

                fifo = open(self.FIFO_file, "ab")

                timeout_detected = False

                while bytes_read < BODY_SIZE and not timeout_detected:

                    # Caso o número de bytes a serem lidos seja menor que o buffer_size
                    if BODY_SIZE - bytes_read < buffer_size:

                        # Inicializa o timer de timeout
                        start_timer  = time.time()

                        while time.time() - start_timer < 10:
                            try:

                                # Recebe o restante do body
                                body = self.conn.recv(BODY_SIZE - bytes_read)

                                # Atualiza o timer de timeout
                                start_timer = time.time()

                                break
                            except:
                                time.sleep(0.01)
                                continue
 
                        # deve retornar uma resposta de time out da entrada de dados
                        if time.time() - start_timer >= 10:

                            # Trava o socket de controle e o arquivo FIFO
                            with self.lock_socket:

                                try:
                                    timeout_detected = True
                                    break
                                except:
                                    continue

                        # Escreve o restante do body no arquivo FIFO
                        fifo.write(body)

                        # Atualiza o número de bytes lidos
                        bytes_read += len(body)

                    # Caso contrário
                    else:

                        # Inicializa o timer de timeout
                        start_timer  = time.time()

                        # Recebe buffer_size bytes do body
                        while time.time() - start_timer < 10:
                            try:

                                # Recebe o restante do body
                                body = self.conn.recv(buffer_size)

                                # Atualiza o timer de timeout
                                start_timer = time.time()

                                break
                            except:
                                time.sleep(0.01)
                                continue
 
                        # deve retornar uma resposta de time out da entrada de dados
                        if time.time() - start_timer >= 10:

                            # Trava o socket de controle e o arquivo FIFO
                            with self.lock_socket:

                                try:
                                    timeout_detected = True
                                    break
                                except:
                                    continue

                        # Escreve buffer_size bytes do body no arquivo FIFO
                        fifo.write(body)

                        # Atualiza o número de bytes lidos
                        bytes_read += len(body)

                
                # Caso o timeout não tenha sido detectado
                if not timeout_detected:

                    # Recebe o crc do pacote
                    while True:
                        try:
                            pkg_crc = self.conn.recv(2)
                            break
                        except:
                            continue

                    # Guarda o command_id, machine_state, command_type, body_size e crc na FIFO da RAM
                    self.fifo.append(pkg_header + pkg_body_size + pkg_crc)

                    # Fecha o arquivo FIFO
                    fifo.close()

                # Caso o timeout tenha sido detectado
                else:

                    # Deleta os últimos bytes_read bytes do arquivo FIFO
                    fifo.close()
                    fifo = open(self.FIFO_file, "rb+")
                    fifo.seek(0, 2)
                    fifo.truncate(fifo.tell() - bytes_read)
                    fifo.close()

                    # Gera a resposta de timeout
                    failed_packet = self.write_client.failed_recieve()

                    # Envia a resposta de timeout
                    self.conn.sendall(failed_packet)



                        
############################################################################################################################################
# Função main

if __name__ == "__main__":
    host = "0.0.0.0"
    port = 4322
    interface = Interface(host, port)