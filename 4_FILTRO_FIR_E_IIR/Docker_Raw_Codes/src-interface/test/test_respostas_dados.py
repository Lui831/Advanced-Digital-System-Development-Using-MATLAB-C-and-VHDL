import socket
import struct
from fastcrc import crc16
import leitor_dados as ld
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class sender_client:
    """
    Classe responsável por gerenciar a comunicação de comandos e respostas entre o cliente e um emulador.
    Implementa a construção de pacotes, cálculo de CRC e a identificação de comandos e respostas.

    Atributos:
    ----------
    STATE_CONFIG : int
        Estado da máquina para configuração (valor 0x0).
    STATE_RUN : int
        Estado da máquina em execução (valor 0x1).
    STATE_PAUSE : int
        Estado da máquina pausada (valor 0x2).
    STATE_STOP : int
        Estado da máquina parada (valor 0x3).
    RESPONSE_TABLE_CLIENT : dict
        Tabela de respostas mapeando comandos para seus respectivos estados e respostas.
    COMMANDS : dict
        Dicionário de comandos que o cliente pode enviar.
    packet : bytes
        Pacote atual que será enviado ou recebido.
    """

    # Estados da máquina
    STATE_CONFIG = 0x0
    STATE_RUN = 0x1
    STATE_PAUSE = 0x2
    STATE_STOP = 0x3

    RESPONSE_TABLE_CLIENT = {
        "Verification of state (Executed)": (0x1, "-"),  
        "Verification of state (Failed)": (0x0, "-"),  
        "Inject ELF (Executed)": (0x1, "-"),  
        "Inject ELF (Failed)": (0x0, "-"),  
        "Config RAM (Executed)": (0x1, "-"),  
        "Config RAM (Failed)": (0x0, "-"),  
        "Start Emulation (Executed)": (0x1, "-"),  
        "Start Emulation (Failed)": (0x0, "-"),  
        "Pause Machine (Executed)": (0x1, "-"),  
        "Pause Machine (Failed)": (0x0, "-"),  
        "Unpause Machine (Executed)": (0x1, "-"),  
        "Unpause Machine (Failed)": (0x0, "-"),  
        "Dump Memory (Executed)": (0x1, "-"),  
        "Dump Memory (Failed)": (0x0, "-"),  
        "Load Memory (Executed)": (0x1, "Mem DATA"),  
        "Load Memory (Failed)": (0x0, "-"),  
        "Read I/O (Executed)": (0x1, "I/O Value"),  
        "Read I/O (Failed)": (0x0, "-"),  
        "Write I/O (Executed)": (0x1, "-"),  
        "Write I/O (Failed)": (0x0, "-"),  
        "Quit Emulation (Executed)": (0x1, "-"),   
        "Quit Emulation (Failed)": (0x0, "-")   
    }

    COMMANDS = {
        (0x0, 0x01): "Inject ELF",
        (0x0, 0x02): "Config RAM",
        (0x0, 0x03): "Config Debug",
        (0x0, 0x04): "Start Emulation",
        (0x1, 0x05): "Pause Machine",
        (0x1, 0x06): "Unpause Machine",
        (0x1, 0x07): "Dump Memory",
        (0x1, 0x08): "Load Memory",
        (0x1, 0x09): "Read I/O",
        (0x1, 0x0A): "Write I/O",
        (0x1, 0x0B): "Quit Emulation"
    }

    def __init__(self):
        """
        Inicializa o objeto sender_client sem pacotes.
        """
        self.packet = None
        self.read_client = ld.reciever_client()

    def calculate_crc(self, baByteArray, u16Crc=0xFFFF):
        """
        Calcula o CRC16-CCITT de um array de bytes usando um polinômio de verificação.

        Parâmetros:
        -----------
        baByteArray : list
            Array de bytes que será calculado o CRC.
        u16Crc : int, opcional
            Valor inicial do CRC (padrão é 0xFFFF).

        Retorna:
        --------
        int
            Valor CRC calculado.
        """
        packed_data = struct.pack(f'{len(baByteArray)}B', *baByteArray)
        return crc16.xmodem(packed_data, initial=u16Crc)

    def answer_status(self, qemu_resp):
        """
        Verifica o status da resposta do QEMU.

        Parâmetros:
        -----------
        qemu_resp : int
            Código de resposta do QEMU.

        Retorna:
        --------
        int
            0 se a execução falhou, 1 se foi executada com sucesso, -1 para respostas desconhecidas.
        """
        if qemu_resp == 0x00:
            return 0
        elif qemu_resp == 0x01:
            return 1
        else:
            return -1
    
    def identify_command(self, command, qemu_resp):
        """
        Identifica o comando baseado na resposta do QEMU e verifica sua execução.

        Parâmetros:
        -----------
        command : str
            O comando recebido que deve ser identificado.
        qemu_resp : int
            Código de resposta do QEMU.

        Retorna:
        --------
        tuple
            O resultado do comando da tabela de resposta ou o próximo comando a ser enviado.
        """
        commands = list(self.RESPONSE_TABLE_CLIENT.keys())
        self.answer_qemu = self.answer_status(qemu_resp)
        
        if command + " (Executed)" in commands and self.answer_qemu == 1:
            print(f"Command {command} executed successfully")
            return self.RESPONSE_TABLE_CLIENT[command + " (Executed)"]
            
        elif command + " (Failed)" in commands and self.answer_qemu == 0:
            print(f"Command {command} failed to execute")
            return self.RESPONSE_TABLE_CLIENT[command + " (Failed)"]
        else:
            command_index = commands.index(command + " (Executed)") if command + " (Executed)" in commands else -1
            next_command_index = command_index + 1 if command_index + 1 < len(commands) else 0
            return commands[next_command_index]

    def construct_packet(self, result):
        """
        Constrói um pacote de resposta com base no resultado.

        Parâmetros:
        -----------
        result : dict
            Um dicionário contendo informações sobre o comando e o conteúdo da resposta.

        Gera:
        ------
        bytes
            Pacote construído com CRC.
        """

        if isinstance(result, dict):
            answer_id = result['command_id']
            command = result['command']
            answer_status = result['answer_status']
            body_content = result['body_content']

            if body_content is not None:
                body_content = bytes(body_content)
            else:
                body_content = b""

        elif isinstance(result, list):
            # Constrói um pacote de erro em bytes "Invalid packet"
            answer_status = result[0]
            answer_id = result[1]
            body_content = b""
            
        packet_body = body_content
        body_size = len(packet_body)

        packet_header = struct.pack("!IBI", answer_id, answer_status, body_size)
        packet_crc = packet_header + packet_body
        crc_value = self.calculate_crc(packet_crc)
        packet_crc = struct.pack("!H", crc_value)
        self.packet = packet_header + packet_body + packet_crc

    def get_packet(self):
        """
        Retorna o pacote construído.

        Retorna:
        --------
        bytes
            O pacote atual construído.
        """
        return self.packet
        
    def failed_recieve(self, command_id):
        """
        Retorna uma mensagem de erro caso a recepção do pacote falhe.

        Retorna:
        --------
        list
            Uma lista contendo o status de erro e o ID do comando.
        """
        self.command_id = command_id
        self.command_id = self.read_client.get_last_command_id()

        # Converte o command_id para 4 bytes em big-endian
        command_id_bytes = self.command_id.to_bytes(4, byteorder='big')

        # Define o tipo de erro como 0x07
        error_type = 0x05.to_bytes(1, byteorder='big')

        # Define o body content como 4 bytes de 0x00
        body_syze = (0x00).to_bytes(4, byteorder='big')

        # Define o body content como 4 bytes de 0x00
        body_content = (0x00).to_bytes(4, byteorder='big')

        # Concatena todos os bytes para formar a mensagem parcial
        partial_message = command_id_bytes + error_type + body_syze + body_content

        # Calcula o CRC da mensagem parcial
        crc = self.calculate_crc(partial_message)

        # Converte o CRC para 2 bytes em big-endian
        crc_bytes = crc.to_bytes(2, byteorder='big')

        # Concatena a mensagem parcial com o CRC para formar a mensagem final
        message = partial_message + crc_bytes

        return message
    
class test_sender_client(unittest.TestCase):

    def setUp(self):
        self.sender_client = sender_client()

        self.test_cases_crc = [
            (b'\x00\x00\x00\x00\x00\x00\x00\x01', 0x211F),
            (b'\x12\x34\x56\x78\x9A\xBC\xDE\xF0', 0x0524),
            (b'\xAA\xBB\xCC\xDD\xEE\xFF\x00\x11', 0xD778),
            (b'\x11\x22\x33\x44\x55\x66\x77\x88', 0x5DB5),
            (b'\x00\x00\x00\x00\x00\x00\x00\x00', 0x313E),
            (b'\x01\x01\x01\x01\x01\x01\x01\x01', 0x43E9),
            (b'\x02\x02\x02\x02\x02\x02\x02\x02', 0xD490),
            (b'\x03\x03\x03\x03\x03\x03\x03\x03', 0xA647),
            (b'\x04\x04\x04\x04\x04\x04\x04\x04', 0xEA43),
            (b'\x05\x05\x05\x05\x05\x05\x05\x05', 0x9894)
        ]

        self.test_cases_identify_command = [
            ("Inject ELF", 0x01, (0x1, "-")),
            ("Config RAM", 0x01, (0x1, "-")),
            ("Start Emulation", 0x01, (0x1, "-")),
            ("Pause Machine", 0x01, (0x1, "-")),
            ("Unpause Machine", 0x01, (0x1, "-")),
            ("Dump Memory", 0x01, (0x1, "-")),
            ("Load Memory", 0x01, (0x1, "Mem DATA")),
            ("Read I/O", 0x01, (0x1, "I/O Value")),
            ("Write I/O", 0x01, (0x1, "-")),
            ("Quit Emulation", 0x01, (0x1, "-"))
        ]

        self.test_cases_construct_packet = [
            ({"command_id": 1, "command": "Inject ELF", "answer_status": 1, "body_content": b'\x01\x02\x03\x04'}, b'\x00\x00\x00\x01\x01\x00\x00\x00\x04\x01\x02\x03\x04(o'),
            ({"command_id": 2, "command": "Config RAM", "answer_status": 0, "body_content": b'\x05\x06\x07\x08'}, b'\x00\x00\x00\x02\x00\x00\x00\x00\x04\x05\x06\x07\x08i\xfa'),
            ({"command_id": 3, "command": "Start Emulation", "answer_status": 1, "body_content": b'\x09\x0A\x0B\x0C'}, b'\x00\x00\x00\x03\x01\x00\x00\x00\x04\t\n\x0b\x0c\xd2&'),
            ({"command_id": 4, "command": "Pause Machine", "answer_status": 0, "body_content": b'\x0D\x0E\x0F\x10'}, b'\x00\x00\x00\x04\x00\x00\x00\x00\x04\r\x0e\x0f\x10,\xb7'),
            ({"command_id": 5, "command": "Unpause Machine", "answer_status": 1, "body_content": b'\x11\x12\x13\x14'}, b'\x00\x00\x00\x05\x01\x00\x00\x00\x04\x11\x12\x13\x14\xcc\xdc')
        ]

        self.test_cases_failed_recieve = [(0x01, b'\x00\x00\x00\x00\x05\x00\x00\x00\x00\x00\x00\x00\x00_\xc0'),
                                            (0x02, b'\x00\x00\x00\x00\x05\x00\x00\x00\x00\x00\x00\x00\x00_\xc0'),
                                            (0x03, b'\x00\x00\x00\x00\x05\x00\x00\x00\x00\x00\x00\x00\x00_\xc0'),
                                            (0x04, b'\x00\x00\x00\x00\x05\x00\x00\x00\x00\x00\x00\x00\x00_\xc0'),
                                            (0x05, b'\x00\x00\x00\x00\x05\x00\x00\x00\x00\x00\x00\x00\x00_\xc0'),
        ]

    def test_calculate_crc_2(self):
        for packet, expected_crc in self.test_cases_crc:
            with self.subTest(packet=packet, expected_crc=expected_crc):
                calculated_crc = self.sender_client.calculate_crc(packet)
                self.assertEqual(calculated_crc, expected_crc, f"Expected {expected_crc}, but got {calculated_crc}")

    def test_identify_command(self):
        for command, qemu_resp, expected_result in self.test_cases_identify_command:
            with self.subTest(command=command, qemu_resp=qemu_resp, expected_result=expected_result):
                result = self.sender_client.identify_command(command, qemu_resp)
                self.assertEqual(result, expected_result, f"Expected {expected_result}, but got {result}")

    def test_construct_packet(self):
        for result, expected_packet in self.test_cases_construct_packet:
            with self.subTest(result=result, expected_packet=expected_packet):
                self.sender_client.construct_packet(result)
                packet = self.sender_client.get_packet()
                self.assertEqual(packet, expected_packet, f"Expected {expected_packet}, but got {packet}")

    def test_failed_recieve(self):
        for command_id, expected_message in self.test_cases_failed_recieve:
            with self.subTest(command_id=command_id, expected_message=expected_message):
                message = self.sender_client.failed_recieve(command_id)
                self.assertEqual(message, expected_message, f"Expected {expected_message}, but got {message}")
