import socket
import struct
from fastcrc import crc16  # Biblioteca para cálculo de CRC
import client_qemu as cq

class reciever_client:

    def __init__(self):
        self.command_id = None
        self.machine_state = None
        self.command_type = None
        self.body_size = None
        self.received_crc = None
        self.calculated_crc = None
        self.command = None
        self.result = None
        self.client_qemu = cq.QemuEmulator()

        self.list_command_id = set()

        self.QEMU_ERROR = 0x00
        self.CRC_ERROR = 0x02
        self.INVALID_COMMAND = 0x03
        self.INVALID_BODY_CONTENT = 0x04
        self.TIME_OUT = 0x05
        self.INVALID_MACHINE_STATE = 0x06
        self.INVALID_COMMAND_ID = 0x07
        self.INVALID_LEN = 0x08
        self.NO_CONFIG_RAM = 0x09
        self.NO_CONFIG_ELF = 0x0A
        self.NO_CONFIG_DEBUG = 0x0B
        self.NO_BREAK_POINT = 0x0C
        self.PASS_LIMIT_MEM_HOST = 0x0D
        self.NOT_RECOGNIZED_COMMAND_DGB = 0x0E
        self.NO_EXIST_LINE = 0x0F
        self.NO_EXIST_VAR = 0x10
        self.NO_EXIST_ADDR = 0x11
        self.INVALID_OPTION_DEBUG = 0x12
             

        self.command_list = []

        self.COMMANDS = {
        (0x0, 0x0): self.client_qemu.get_current_state,
        (0x0, 0x01): self.client_qemu.inject_elf,
        (0x0, 0x02): self.client_qemu.inject_ahbrom,
        (0x0, 0x03): self.client_qemu.config_ram,
        (0x0, 0x04): self.client_qemu.config_debug,
        (0x0, 0x05): self.client_qemu.set_osabi,
        (0x0, 0x06): self.client_qemu.start_emulation,
        (0x1, 0x07): self.client_qemu.pause_emulation,
        (0x1, 0x08): self.client_qemu.unpause_emulation,
        (0x1, 0x09): self.client_qemu.dump_memory,
        (0x1, 0x0B): self.client_qemu.read_IO,
        (0x1, 0x0C): self.client_qemu.write_IO,
        (0x1, 0x0D): self.client_qemu.quit_emulation,
        (0x1, 0x0E): self.client_qemu.configure_breakpoint,
        (0x1, 0x0F): self.client_qemu.delete_breakpoint,
        (0x1, 0x10): self.client_qemu.continue_execution,
        (0x1, 0x11): self.client_qemu.finish_execution,
        (0x1, 0x12): self.client_qemu.next_line,
        (0x1, 0x13): self.client_qemu.step_into,
        (0x1, 0x14): self.client_qemu.verify_variable,
        (0x1, 0x15): self.client_qemu.send_gdb_command,
        (0x0, 0x16): self.client_qemu.load_addr
        }


    def calculate_crc(self, baByteArray, u16Crc=0xFFFF):
        # Empacotar o byte array usando struct
        packed_data = struct.pack(f'{len(baByteArray)}B', *baByteArray)
        
        # CRC16-CCITT polynomial
        return crc16.xmodem(packed_data, initial=u16Crc)
        
    def validate_packet(self, packet, body_content):
        header_format = "!IBH"  # 4B COMMAND_ID, 1B MACHINE_STATE, 2B COMMAND_TYPE
        body_header_format = "!I"  # 4B BODY_SIZE
        crc_format = "!H"  # 2B PKG_CRC

        header_size = struct.calcsize(header_format)
        body_header_size = struct.calcsize(body_header_format)
        crc_size = struct.calcsize(crc_format)

        # Verificando se o tamanho do pacote recebido é válido
        if len(packet) < header_size + body_header_size + crc_size:
            return False, self.INVALID_LEN

        # Parse do header
        self.command_id, self.machine_state, self.command_type = struct.unpack(header_format, packet[:header_size])
        
        if self.command_id in self.list_command_id:
            return False, self.INVALID_COMMAND_ID
        else:
            self.list_command_id.add(self.command_id)


        # Parse do body size
        self.body_size = struct.unpack(body_header_format, packet[header_size:header_size + body_header_size])[0]

        # Parse do body content e CRC
        self.received_crc = struct.unpack(crc_format, packet[header_size + body_header_size:])[0]

        # Calculando o CRC para validação
        self.body_content = body_content
        self.calculated_crc = self.calculate_crc(packet[:-crc_size])
        self.calculated_crc = self.calculate_crc(body_content, u16Crc=self.calculated_crc)

        if self.calculated_crc != self.received_crc:
            return False, self.CRC_ERROR
        
        # Verificando se o pacote é válido
        command_key = (self.machine_state, self.command_type)

        command = self.COMMANDS.get(command_key, False)

        #inverte o machine state e verifica se o comando é válido
        if command == False:
            command_key = (self.machine_state ^ 0x1, self.command_type)
            command = self.COMMANDS.get(command_key, False)


            if command == False:
                return False, self.INVALID_COMMAND

            return False, self.INVALID_MACHINE_STATE

        return True, {
            "command_id": self.command_id,
            "machine_state": self.machine_state,
            "command_type": self.command_type,
            "body_size": self.body_size,
            "body_content": self.body_content,
            "received_crc": self.received_crc,
            "calculated_crc": self.calculated_crc
        }

    def process_packet(self, packet, body_content):
        # Validar o pacote recebido
        is_valid, self.result = self.validate_packet(packet, body_content)

        if not is_valid:
            return [self.result, self.command_id] # Retorna a mensagem de erro se houver falha na validação

        # Identificação do comando
        command_key = (self.machine_state, self.command_type)
        self.command = self.COMMANDS.get(command_key, False)
        self.answer = self.command(self.body_content) if callable(self.command) else self.command
        self.answer = list(self.answer)

        # Guarda o comando na lista de comandos
        self.command_type_list(self.command_list)
        
        return {
            "command_id": self.result["command_id"],
            "machine_state": self.machine_state,
            "command_type": self.command_type,
            "body_size": self.result["body_size"],
            "body_content": self.result["body_content"],
            "received_crc": self.result["received_crc"],
            "calculated_crc": self.result["calculated_crc"],
            "command": self.command,
            "answer_status": self.answer[0],
            "answer_body": self.answer[1],
            "valid" : is_valid
        }
    
    # Função para montar uma lista de comandos rodados
    def command_type_list(self, command_list):
        # verifica se o pacote é válido
        if self.result:
            # append somente o command_type na lista
            command_list.append(self.result["command_type"])
    
    # Funções getter para cada variável do dicionário de retorno
    def get_command_id(self):
        return self.result["command_id"]

    def get_machine_state(self):
        return self.machine_state

    def get_command_type(self):
        return self.command_type

    def get_body_size(self):
        return self.result["body_size"]

    def get_body_content(self):
        return self.result["body_content"]

    def get_received_crc(self):
        return self.result["received_crc"]

    def get_calculated_crc(self):
        return self.result["calculated_crc"]

    def get_command(self):
        return self.command
        
    def get_last_command_id(self):
        # Converte o set em uma lista
        list_command_id = list(self.list_command_id)
        
        # Verifica se a lista não está vazia
        if list_command_id:
            # Obtém o último elemento da lista
            last_command_id = list_command_id[-1]
            return last_command_id + 1
        else:
            return 0  # Retorna None se a lista estiver vazia
    
    # Função para retornar a lista de comandos
    def get_command_list(self):
        return self.command_list


# Teste da classe e funções do leitor_dados
class test_reciever_client:
    def __init__(self):
        self.reciever_client = reciever_client()
        self.packet = b'\x00\x00\x00\x00\x00\x00\x00\x01'
    
    def test_calculate_crc(self):
        assert self.reciever_client.calculate_crc(b'123456789') == 0x29B1