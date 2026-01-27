import socket
import struct
from fastcrc import crc16  # Biblioteca para cálculo de CRC
import client_qemu as cq
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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
        (0x1, 0x16): self.client_qemu.write_IO
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
    
    # Funções getter para cada variável do dicionário de retorno

    # Não  é necessário testar essas funções, pois são apenas getters

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


# Teste da classe e funções do leitor_dados
class test_reciever_client(unittest.TestCase):

    def setUp(self):
        self.reciever_client = reciever_client()
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
        self.test_cases_validate = [
            (b'\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x01\xBD\x80', b'\x08', True),
            (b'\x00\x00\x00\x01\x00\x00\x03\x00\x00\x00\x01\x82\x2A', b'\x01', True),
            (b'\x00\x00\x00\x02\x00\x00\x05\x00\x00\x00\x00\x78\xFE', b'', True),
            (b'\x00\x00\x00\x03\x01\x00\x0D\x00\x00\x00\x01\x95\x2C', b'\x33', True),
            (b'\x00\x00\x00\x04\x01\x00\x10\x00\x00\x00\x06\xC9\xAF', b'\x69\x6E\x66\x6F\x20\x62', True),
            (b'\x00\x00\x00\x05\x01\x00\x0F\x00\x00\x00\x00\x41\x29', b'', True),
            (b'\x00\x00\x00\x06\x01\x00\x0E\x00\x00\x00\x01\x2C\x00', b'\x33', True),
            (b'\x00\x00\x00\x07\x01\x00\x0F\x00\x00\x00\x00\xCE\x8F', b'', True),
            (b'\x00\x00\x00\x08\x01\x00\x0C\x00\x00\x00\x00\xF9\x9F', b'', True),
            (b'\x00\x00\x00\x09\x00\x00\x03\x00\x00\x00\x01\xAB\xD5', b'\x01', True)
        ]

        self.test_cases_process_packet = [
            (b'\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x01\xBD\x80', b'\x08', {
                "command_id": 0,
                "machine_state": 0,
                "command_type": 2,
                "body_size": 1,
                "body_content": b'\x08',
                "received_crc": 0xBD80,
                "calculated_crc": 0xBD80,
                "command": self.reciever_client.client_qemu.inject_ahbrom,
                "answer_status": 1,  # Supondo que o status de resposta seja 0
                "answer_body": None,  # Supondo que o corpo da resposta seja vazio
                "valid": True
            }),
            (b'\x00\x00\x00\x01\x00\x00\x03\x00\x00\x00\x01\x82\x2A', b'\x01', {
                "command_id": 1,
                "machine_state": 0,
                "command_type": 3,
                "body_size": 1,
                "body_content": b'\x01',
                "received_crc": 0x822A,
                "calculated_crc": 0x822A,
                "command": self.reciever_client.client_qemu.config_ram,
                "answer_status": 4,  # Supondo que o status de resposta seja 0
                "answer_body": None,  # Supondo que o corpo da resposta seja vazio
                "valid": True
            }),
            (b'\x00\x00\x00\x02\x00\x00\x05\x00\x00\x00\x00\x78\xFE', b'', {
                "command_id": 2,
                "machine_state": 0,
                "command_type": 5,
                "body_size": 0,
                "body_content": b'',
                "received_crc": 0x78FE,
                "calculated_crc": 0x78FE,
                "command": self.reciever_client.client_qemu.set_osabi,
                "answer_status": 4,  # Supondo que o status de resposta seja 0
                "answer_body": None,  # Supondo que o corpo da resposta seja vazio
                "valid": True
            }),
            (b'\x00\x00\x00\x03\x01\x00\x0D\x00\x00\x00\x01\x95\x2C', b'\x33', {
                "command_id": 3,
                "machine_state": 1,
                "command_type": 13,
                "body_size": 1,
                "body_content": b'\x33',
                "received_crc": 0x952C,
                "calculated_crc": 0x952C,
                "command": self.reciever_client.client_qemu.quit_emulation,
                "answer_status": 6,  # Supondo que o status de resposta seja 0
                "answer_body": None,  # Supondo que o corpo da resposta seja vazio
                "valid": True
            }),
            (b'\x00\x00\x00\x04\x01\x00\x10\x00\x00\x00\x06\xC9\xAF', b'\x69\x6E\x66\x6F\x20\x62', {
                "command_id": 4,
                "machine_state": 1,
                "command_type": 16,
                "body_size": 6,
                "body_content": b'\x69\x6E\x66\x6F\x20\x62',
                "received_crc": 0xC9AF,
                "calculated_crc": 0xC9AF,
                "command": self.reciever_client.client_qemu.continue_execution,
                "answer_status": 6,  # Supondo que o status de resposta seja 0
                "answer_body": None,  # Supondo que o corpo da resposta seja vazio
                "valid": True
            }),
            (b'\x00\x00\x00\x05\x01\x00\x0F\x00\x00\x00\x00\x41\x29', b'', {
                "command_id": 5,
                "machine_state": 1,
                "command_type": 15,
                "body_size": 0,
                "body_content": b'',
                "received_crc": 0x4129,
                "calculated_crc": 0x4129,
                "command": self.reciever_client.client_qemu.delete_breakpoint,
                "answer_status": 6,  # Supondo que o status de resposta seja 0
                "answer_body": None,  # Supondo que o corpo da resposta seja vazio
                "valid": True
            }),
            (b'\x00\x00\x00\x06\x01\x00\x0E\x00\x00\x00\x01\x2C\x00', b'\x33', {
                "command_id": 6,
                "machine_state": 1,
                "command_type": 14,
                "body_size": 1,
                "body_content": b'\x33',
                "received_crc": 0x2C00,
                "calculated_crc": 0x2C00,
                "command": self.reciever_client.client_qemu.configure_breakpoint,
                "answer_status": 6,  # Supondo que o status de resposta seja 0
                "answer_body": None,  # Supondo que o corpo da resposta seja vazio
                "valid": True
            }),
            (b'\x00\x00\x00\x07\x01\x00\x0F\x00\x00\x00\x00\xCE\x8F', b'', {
                "command_id": 7,
                "machine_state": 1,
                "command_type": 15,
                "body_size": 0,
                "body_content": b'',
                "received_crc": 0xCE8F,
                "calculated_crc": 0xCE8F,
                "command": self.reciever_client.client_qemu.delete_breakpoint,
                "answer_status": 6,  # Supondo que o status de resposta seja 0
                "answer_body": None,  # Supondo que o corpo da resposta seja vazio
                "valid": True
            }),
            (b'\x00\x00\x00\x08\x01\x00\x0C\x00\x00\x00\x00\xF9\x9F', b'', {
                "command_id": 8,
                "machine_state": 1,
                "command_type": 12,
                "body_size": 0,
                "body_content": b'',
                "received_crc": 0xF99F,
                "calculated_crc": 0xF99F,
                "command": self.reciever_client.client_qemu.write_IO,
                "answer_status": 6,  # Supondo que o status de resposta seja 0
                "answer_body": None,  # Supondo que o corpo da resposta seja vazio
                "valid": True
            }),
            (b'\x00\x00\x00\x09\x00\x00\x03\x00\x00\x00\x01\xAB\xD5', b'\x01', {
                "command_id": 9,
                "machine_state": 0,
                "command_type": 3,
                "body_size": 1,
                "body_content": b'\x01',
                "received_crc": 0xABD5,
                "calculated_crc": 0xABD5,
                "command": self.reciever_client.client_qemu.config_ram,
                "answer_status": 4,  # Supondo que o status de resposta seja 0
                "answer_body": None,  # Supondo que o corpo da resposta seja vazio
                "valid": True
            })
        ]

    def test_calculate_crc_1(self):
        for packet, expected_crc in self.test_cases_crc:
            with self.subTest(packet=packet, expected_crc=expected_crc):
                calculated_crc = self.reciever_client.calculate_crc(packet)
                self.assertEqual(calculated_crc, expected_crc, f"Expected {expected_crc}, but got {calculated_crc}")

    def test_validate_packet(self):
        for packet, body_content, expected_answer in self.test_cases_validate:
            with self.subTest(packet=packet, expected_answer=expected_answer):
                is_valid, result = self.reciever_client.validate_packet(packet, body_content)
                if not is_valid:
                    print(f"Packet: {packet}, Body Content: {body_content}, Result: {result}")
                self.assertTrue(is_valid, "Packet is invalid")

    def test_process_packet(self):

            for packet, body_content, expected_result in self.test_cases_process_packet:
                with self.subTest(packet=packet, expected_result=expected_result):
                    result = self.reciever_client.process_packet(packet, body_content)
                    self.assertEqual(result, expected_result, f"Expected {expected_result}, but got {result}")

