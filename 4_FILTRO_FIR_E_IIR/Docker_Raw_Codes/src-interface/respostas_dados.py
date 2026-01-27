import socket
import struct
from fastcrc import crc16
import leitor_dados as ld

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
        "Get Current State (Executed)": (0x1, "State Data"),  
        "Get Current State (Failed)": (0x0, "-"),  
        "Inject ELF (Executed)": (0x1, "-"),  
        "Inject ELF (Failed)": (0x0, "-"),  
        "Inject AHBROM (Executed)": (0x1, "-"),  
        "Inject AHBROM (Failed)": (0x0, "-"),  
        "Config RAM (Executed)": (0x1, "-"),  
        "Config RAM (Failed)": (0x0, "-"),  
        "Config Debug (Executed)": (0x1, "-"),  
        "Config Debug (Failed)": (0x0, "-"),  
        "Set OSABI (Executed)": (0x1, "-"),  
        "Set OSABI (Failed)": (0x0, "-"),  
        "Start Emulation (Executed)": (0x1, "-"),  
        "Start Emulation (Failed)": (0x0, "-"),  
        "Pause Emulation (Executed)": (0x1, "-"),  
        "Pause Emulation (Failed)": (0x0, "-"),  
        "Unpause Emulation (Executed)": (0x1, "-"),  
        "Unpause Emulation (Failed)": (0x0, "-"),  
        "Dump Memory (Executed)": (0x1, "Memory Data"),  
        "Dump Memory (Failed)": (0x0, "-"),  
        "Read I/O (Executed)": (0x1, "I/O Value"),  
        "Read I/O (Failed)": (0x0, "-"),  
        "Write I/O (Executed)": (0x1, "-"),  
        "Write I/O (Failed)": (0x0, "-"),  
        "Quit Emulation (Executed)": (0x1, "-"),   
        "Quit Emulation (Failed)": (0x0, "-"),
        "Configure Breakpoint (Executed)": (0x1, "-"),  
        "Configure Breakpoint (Failed)": (0x0, "-"),  
        "Delete Breakpoint (Executed)": (0x1, "-"),  
        "Delete Breakpoint (Failed)": (0x0, "-"),  
        "Continue Execution (Executed)": (0x1, "-"),  
        "Continue Execution (Failed)": (0x0, "-"),  
        "Finish Execution (Executed)": (0x1, "-"),  
        "Finish Execution (Failed)": (0x0, "-"),  
        "Next Line (Executed)": (0x1, "-"),  
        "Next Line (Failed)": (0x0, "-"),  
        "Step Into (Executed)": (0x1, "-"),  
        "Step Into (Failed)": (0x0, "-"),  
        "Verify Variable (Executed)": (0x1, "Variable Value"),  
        "Verify Variable (Failed)": (0x0, "-"),  
        "Send GDB Command (Executed)": (0x1, "GDB Response"),  
        "Send GDB Command (Failed)": (0x0, "-"),  
        "Load Address (Executed)": (0x1, "-"),  
        "Load Address (Failed)": (0x0, "-")
    }

    COMMANDS = {
        (0x0, 0x00): "Get Current State",
        (0x0, 0x01): "Inject ELF",
        (0x0, 0x02): "Inject AHBROM",
        (0x0, 0x03): "Config RAM",
        (0x0, 0x04): "Config Debug",
        (0x0, 0x05): "Set OSABI",
        (0x0, 0x06): "Start Emulation",
        (0x1, 0x07): "Pause Emulation",
        (0x1, 0x08): "Unpause Emulation",
        (0x1, 0x09): "Dump Memory",
        (0x1, 0x0B): "Read I/O",
        (0x1, 0x0C): "Write I/O",
        (0x1, 0x0D): "Quit Emulation",
        (0x1, 0x0E): "Configure Breakpoint",
        (0x1, 0x0F): "Delete Breakpoint",
        (0x1, 0x10): "Continue Execution",
        (0x1, 0x11): "Finish Execution",
        (0x1, 0x12): "Next Line",
        (0x1, 0x13): "Step Into",
        (0x1, 0x14): "Verify Variable",
        (0x1, 0x15): "Send GDB Command",
        (0x0, 0x16): "Load Address"
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
    
    def identify_command(self, command):
        """
        Identifica o comando baseado na resposta do QEMU e verifica sua execução.

        Parâmetros:
        -----------
        command : str
            O comando recebido que deve ser identificado.

        Retorna:
        --------
        tuple
            O resultado do comando da tabela de resposta ou o próximo comando a ser enviado.
        """
        commands = list(self.RESPONSE_TABLE_CLIENT.keys())
        self.answer_qemu = self.answer_status()
        
        if command+self.answer_qemu in commands:
            if self.answer_qemu == " (Executed)":
                print(f"Command {command} executed successfully")
                return self.RESPONSE_TABLE_CLIENT[command+self.answer_qemu]
            
            elif self.answer_qemu == " (Failed)":
                print(f"Command {command} failed to execute")
                return self.RESPONSE_TABLE_CLIENT[command+self.answer_qemu]
        else:
            command_index = commands.index(command) if command in commands else -1
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
            body_content = result['answer_body']

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

        packet_body = body_content
        body_size = len(packet_body)

        packet_header = struct.pack("!IBI", answer_id, answer_status, body_size)
        packet_crc = packet_header + packet_body
        packet_crc = struct.pack("!H", self.calculate_crc(packet_crc))
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
        
        
    def failed_recieve(self):
        """
        Retorna uma mensagem de erro caso a recepção do pacote falhe.

        Retorna:
        --------
        list
            Uma lista contendo o status de erro e o ID do comando.
        """
        self.command_id = self.read_client.get_last_command_id()

        # Converte o command_id para 4 bytes em big-endian
        command_id_bytes = self.command_id.to_bytes(4, byteorder='big')

        # Define o tipo de erro como 0x07
        error_type = 0x05.to_bytes(1, byteorder='big')

        # Define o body content como 4 bytes de 0x00
        body_content = (0x00).to_bytes(4, byteorder='big')

        # Concatena todos os bytes para formar a mensagem parcial
        partial_message = command_id_bytes + error_type + body_content

        # Calcula o CRC da mensagem parcial
        crc = self.calculate_crc(partial_message)

        # Converte o CRC para 2 bytes em big-endian
        crc_bytes = crc.to_bytes(2, byteorder='big')

        # Concatena a mensagem parcial com o CRC para formar a mensagem final
        message = partial_message + crc_bytes

        return message
