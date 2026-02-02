##################################################################################################################################################################################
# main2.py
# Description: the main testing code for user related tests.
# Authors: Luiz H. A. Santos, Felipe F. da Costa, Jackson T. Veiga.
# Date: 27/11/2024
# Version: 1.0
##################################################################################################################################################################################

##################################################################################################################################################################################
# Libraries

import os
import socket
import time
from fastcrc import crc16
import csv

##################################################################################################################################################################################

##################################################################################################################################################################################
# Constants

## Docker TCP/IP Constants -----------------------------------------

# Docker container port
DOCKER_PORT = 4322

# Docker container host
DOCKER_HOST = "localhost"

# Docker container socket type
DOCKER_SOCKET_TYPE = socket.SOCK_STREAM

# Docker container socket family
DOCKER_SOCKET_FAMILY = socket.AF_INET


## Test Constants ---------------------------------------------------

# Output log file name
LOG_FILE_NAME = "./log.txt"

# Test timeout
TEST_TIMEOUT = 30

##################################################################################################################################################################################

##################################################################################################################################################################################
# Test Class

class Protocol_Test:

    # Constructor - Initializes the log file and reads the .csv file
    def __init__(self):

        # Inicializa a definição do dicionário de funções
        self.test_functions = {

            1: self.__send_verify_state_command,
            3: self.__send_inject_elf_command,
            4: self.__send_inject_ahbrom_command,
            5: self.__send_config_ram_command,
            6: self.__send_config_debug_command,
            7: self.__send_set_os_abi_for_debug_command,
            8: self.__send_start_emulation_command,
            9: self.__send_pause_machine_command,
            10: self.__send_unpause_machine_command,
            11: self.__send_dump_memory_command,
            12: self.__send_quit_emulation_command,
            13: self.__send_configure_breakpoint_command,
            14: self.__send_delete_breakpoint_command,
            15: self.__send_continue_emulation_command,
            16: self.__send_finish_execution_command,
            17: self.__send_next_line_command,
            18: self.__send_step_into_command,
            19: self.__send_verify_variable_command,
            20: self.__send_gdb_command,
            21: self.__send_random_command,
            2: self.__restart_connection,
            22: self.__send_read_io_command,
            23: self.__send_write_io_command,
            24: self.__send_inject_config_command,
            25: self.__send_err_inject_command

        }

        # Initializes the log file
        self.log_file = open(LOG_FILE_NAME, "w")

        # Initialize the command_id counter
        self.command_id = 0

        # Connects the client socket to the server
        try:
            self.client_socket = socket.socket(DOCKER_SOCKET_FAMILY, DOCKER_SOCKET_TYPE)
            self.client_socket.connect((DOCKER_HOST, DOCKER_PORT))
            
        except Exception as e:
            print(f"Error: {e}")
            self.log_file.write(f"Error: {e}\n")
            return

        # Sets the timeout for the socket
        self.client_socket.settimeout(TEST_TIMEOUT)

        # Initializes the test, running the test thread
        self.__run_test()

    def start_client():
        while True:
            try:
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.connect(('127.0.0.1', 12345))  # IP e porta do servidor
                print("[CONECTADO] Conectado ao servidor.")
                
                while True:
                    response = client.recv(1024).decode('utf-8')
                    print(f"[SERVIDOR] {response}")
            
            except (ConnectionRefusedError, OSError):
                print("[ERRO] Conexão perdida. Tentando reconectar em 5 segundos...")
                time.sleep(5)
                continue

    # Destructor - Closes the log file and the socket
    def __del__(self):

        # Closes the log file
        self.log_file.close()

        # Closes the socket
        self.client_socket.close()


    # Function that processes bytes in strings to bytes ("0a 0b 0c cc aa" -> b'\x0a\x0b\x0c\xcc\xaa')
    def __process_bytes(self, string):

        # Splits the string into a list of bytes
        string = string.split(" ")

        # Converts the list of bytes into a byte object
        return bytes([int(byte, 16) for byte in string])
    

    # Function that processes bytes in strings of bytes to strings ("b'\x0a\x0b\x0c\xcc\xaa'" -> "0a 0b 0c cc aa")
    def __process_string(self, byte_string):

        # Converts the byte object into a list of bytes
        byte_string = [f"{byte:02x}" for byte in byte_string]

        # Converts the list of bytes into a string
        return " ".join(byte_string)


    # Formats the command to be sent to the server
    def __format_command(self, command_id, command_machine_state, command_type, command_body_content):

        # Transforms the command_id int into 4 bytes
        command_id = command_id.to_bytes(4, byteorder="big")

        # Transforms the command_machine_state int into 1 byte
        command_machine_state = command_machine_state.to_bytes(1, byteorder="big")

        # Transforms the command_type int into 2 bytes
        command_type = command_type.to_bytes(2, byteorder="big")

        # Obtains the length of the command_body_content and transforms it into 4 bytes
        command_body_length = len(command_body_content)
        command_body_length = command_body_length.to_bytes(4, byteorder="big")

        # Join the command_id, command_machine_state, command_type, command_body_length and command_body_content
        command_without_CRC = command_id + command_machine_state + command_type + command_body_length + command_body_content

        # Obtains the CRC16-CITT of the command_without_CRC, append it
        command_CRC = crc16.xmodem(command_without_CRC, initial=0xFFFF).to_bytes(2, byteorder="big")

        # Returns the whole command
        return command_without_CRC + command_CRC


    def __deformat_response(self, command):

        # Splits the command into its parts
        response_id = int.from_bytes(command[0:4], byteorder="big")
        response_status = int.from_bytes(command[4:5], byteorder="big")
        response_body_length = int.from_bytes(command[5:9], byteorder="big")
        response_body_content = command[9:-2]
        response_CRC = int.from_bytes(command[-2:], byteorder="big")

        # Returns the parts
        return {"response_id": response_id, "response_status": response_status, "response_body_length": response_body_length, "response_body_content": response_body_content, "response_CRC": response_CRC}
    

    # Function that interprets the answer status
    def __interpret_status(self, status):

        if status == 0:
            return "QEMU_ERROR"
        elif status == 1:
            return "SUCCESS"  
        elif status == 2:
            return "CRC_ERROR"
        elif status == 3:
            return "INVALID_COMMAND"
        elif status == 4:
            return "INVALID_BODY_CONTENT"
        elif status == 5:
            return "TIME_OUT"
        elif status == 6:
            return "INVALID_MACHINE_STATE"
        elif status == 7:
            return "INVALID_COMMAND_ID"
        elif status == 8:
            return "INVALID_LEN"
        else:
            return "UNKNOWN_STATUS"


    # Function that sends the verify state command to the server
    def __send_verify_state_command(self):

        # Cria o comando a ser enviado
        command = self.__format_command(self.command_id, 0x0, 0x0, b"")
        self.command_id += 1

        # Envia o comando
        self.client_socket.send(command)

        # Recebe a resposta
        response = self.client_socket.recv(1024)

        # Processa a resposta
        response = self.__deformat_response(response)

        # Transforma o body content em inteiro
        response["response_body_content"] = int.from_bytes(response["response_body_content"], byteorder="big")

        # Interpreta o status
        response["response_status"] = self.__interpret_status(response["response_status"])
        
        # Printa o resultado
        print(f"Response ID: {response['response_id']}")
        self.log_file.write(f"Response ID: {response['response_id']}\n")

        print(f"Response Status: {response['response_status']}")
        self.log_file.write(f"Response Status: {response['response_status']}\n")

        print(f"Response Body Length: {response['response_body_length']}")
        self.log_file.write(f"Response Body Length: {response['response_body_length']}\n")

        print(f"Response Body Content: {response['response_body_content']}")
        self.log_file.write(f"Response Body Content: {response['response_body_content']}\n")

        # Interpreta particularmente a resposta do comando
        if response["response_body_content"] == 0:
            print("Response Interpretation: The machine is in CONFIG state.")
            self.log_file.write("Response Interpretation: The machine is paused.\n")
        
        elif response["response_body_content"] == 1:
            print("Response Interpretation: The machine is in RUN state.")
            self.log_file.write("Response Interpretation: The machine is running.\n")


    # Function that sends the inject .ELF command to the server
    def __send_inject_elf_command(self):

        # Pergunta o nome do arquivo .ELF
        elf_file = input("Enter the name of the .ELF file: ")

        # Abre o arquivo .ELF
        with open(elf_file, "rb") as f:
            elf_content = f.read()

        # Cria o comando a ser enviado
        comando = self.__format_command(self.command_id, 0x0, 0x1, elf_content)
        self.command_id += 1

        # Envia o comando para o servidor
        self.client_socket.send(comando)

        # Recebe a resposta
        response = self.client_socket.recv(1024)

        # Processa a resposta
        response = self.__deformat_response(response)

        # Interpreta o status
        response["response_status"] = self.__interpret_status(response["response_status"])

        # Printa o resultado
        print(f"Response ID: {response['response_id']}")
        self.log_file.write(f"Response ID: {response['response_id']}\n")

        print(f"Response Status: {response['response_status']}")
        self.log_file.write(f"Response Status: {response['response_status']}\n")

        print(f"Response Body Length: {response['response_body_length']}")
        self.log_file.write(f"Response Body Length: {response['response_body_length']}\n")

        print(f"Response Body Content: {response['response_body_content']}")
        self.log_file.write(f"Response Body Content: {response['response_body_content']}\n")


    # Function that sends the inject ahbrom file command to the server
    def __send_inject_ahbrom_command(self):

        # Pergunta o nome do arquivo .ELF
        ahbrom_file = input("Enter the name of the AHBROM file: ")

        # Abre o arquivo .ELF
        with open(ahbrom_file, "rb") as f:
            ahbrom_content = f.read()

        # Cria o comando a ser enviado
        command = self.__format_command(self.command_id, 0x0, 0x2, ahbrom_content)
        self.command_id += 1

        # Envia o comando
        self.client_socket.send(command)

        # Recebe a resposta
        response = self.client_socket.recv(1024)

        # Processa a resposta
        response = self.__deformat_response(response)

        # Interpreta o status
        response["response_status"] = self.__interpret_status(response["response_status"])

        # Printa o resultado
        print(f"Response ID: {response['response_id']}")
        self.log_file.write(f"Response ID: {response['response_id']}\n")

        print(f"Response Status: {response['response_status']}")
        self.log_file.write(f"Response Status: {response['response_status']}\n")

        print(f"Response Body Length: {response['response_body_length']}")
        self.log_file.write(f"Response Body Length: {response['response_body_length']}\n")

        print(f"Response Body Content: {response['response_body_content']}")
        self.log_file.write(f"Response Body Content: {response['response_body_content']}\n")


    #Function that sends the config to the server
    def __send_inject_config_command(self):

        # Pergunta o nome do arquivo config
        elf_file = input("Enter the name of the .cfg file: ")

        # Abre o arquivo .ELF
        with open(elf_file, "rb") as f:
            elf_content = f.read()

        # Cria o comando a ser enviado
        comando = self.__format_command(self.command_id, 0x0, 0x3, elf_content)
        self.command_id += 1

        # Envia o comando para o servidor
        self.client_socket.send(comando)

        # Recebe a resposta
        response = self.client_socket.recv(1024)

        # Processa a resposta
        response = self.__deformat_response(response)

        # Interpreta o status
        response["response_status"] = self.__interpret_status(response["response_status"])

        # Printa o resultado
        print(f"Response ID: {response['response_id']}")
        self.log_file.write(f"Response ID: {response['response_id']}\n")

        print(f"Response Status: {response['response_status']}")
        self.log_file.write(f"Response Status: {response['response_status']}\n")

        print(f"Response Body Length: {response['response_body_length']}")
        self.log_file.write(f"Response Body Length: {response['response_body_length']}\n")

        print(f"Response Body Content: {response['response_body_content']}")
        self.log_file.write(f"Response Body Content: {response['response_body_content']}\n")


    # Function that sends the config ram command to the server
    def __send_config_ram_command(self):

        # Pergunta o tamanho da RAM
        ram_size = int(input("Enter the size of the RAM: "))

        # Cria o comando a ser enviado
        command = self.__format_command(self.command_id, 0x0, 0x3, ram_size.to_bytes(4, byteorder="big"))
        self.command_id += 1

        # Envia o comando
        self.client_socket.send(command)

        # Recebe a resposta
        response = self.client_socket.recv(1024)

        # Processa a resposta
        response = self.__deformat_response(response)

        # Interpreta o status
        response["response_status"] = self.__interpret_status(response["response_status"])

        # Printa o resultado
        print(f"Response ID: {response['response_id']}")
        self.log_file.write(f"Response ID: {response['response_id']}\n")

        print(f"Response Status: {response['response_status']}")
        self.log_file.write(f"Response Status: {response['response_status']}\n")

        print(f"Response Body Length: {response['response_body_length']}")
        self.log_file.write(f"Response Body Length: {response['response_body_length']}\n")

        print(f"Response Body Content: {response['response_body_content']}")
        self.log_file.write(f"Response Body Content: {response['response_body_content']}\n")


    # Function that sends the config debug command to the server
    def __send_config_debug_command(self):

        # Pergunta se vai querer o modo de debug ou não
        debug_mode = int(input("Enter 0 for no debug mode | 1 for debug mode with discrete interface | 2 for debug mode with implicit interface: "))

        # Cria o comando a ser enviado
        command = self.__format_command(self.command_id, 0x0, 0x4, debug_mode.to_bytes(1, byteorder="big"))
        self.command_id += 1

        # Envia o comando
        self.client_socket.send(command)

        # Recebe a resposta
        response = self.client_socket.recv(1024)

        # Processa a resposta
        response = self.__deformat_response(response)

        # Interpreta o status
        response["response_status"] = self.__interpret_status(response["response_status"])

        # Printa o resultado
        print(f"Response ID: {response['response_id']}")
        self.log_file.write(f"Response ID: {response['response_id']}\n")

        print(f"Response Status: {response['response_status']}")
        self.log_file.write(f"Response Status: {response['response_status']}\n")

        print(f"Response Body Length: {response['response_body_length']}")
        self.log_file.write(f"Response Body Length: {response['response_body_length']}\n")

        print(f"Response Body Content: {response['response_body_content']}")
        self.log_file.write(f"Response Body Content: {response['response_body_content']}\n")


    # Function that sedns the set OS ABI for debug command to the server
    def __send_set_os_abi_for_debug_command(self):

        # Pergunta qual o OS ABI a ser utilizado
        os_abi = str(input("Enter the OS ABI to be used by GDB: "))

        # Codifica o OS ABI
        os_abi = os_abi.encode('utf-8')

        # Cria o comando a ser enviado
        command = self.__format_command(self.command_id, 0x0, 0x5, os_abi)
        self.command_id += 1

        # Envia o comando
        self.client_socket.send(command)

        # Recebe a resposta
        response = self.client_socket.recv(1024)

        # Deformata a resposta
        response = self.__deformat_response(response)

        # Interpreta o status
        response["response_status"] = self.__interpret_status(response["response_status"])

        # Printa o resultado
        print(f"Response ID: {response['response_id']}")
        self.log_file.write(f"Response ID: {response['response_id']}\n")

        print(f"Response Status: {response['response_status']}")
        self.log_file.write(f"Response Status: {response['response_status']}\n")

        print(f"Response Body Length: {response['response_body_length']}")
        self.log_file.write(f"Response Body Length: {response['response_body_length']}\n")

        print(f"Response Body Content: {response['response_body_content']}")
        self.log_file.write(f"Response Body Content: {response['response_body_content']}\n")


    # Function that sends the start emulation command to the server
    def __send_start_emulation_command(self):

        # Formata o comando a ser enviado
        command = self.__format_command(self.command_id, 0x0, 0x6, b"")
        self.command_id += 1

        # Envia o comando
        self.client_socket.send(command)

        # Recebe a resposta
        response = self.client_socket.recv(1024)

        # Processa a resposta
        response = self.__deformat_response(response)

        # Interpreta o status
        response["response_status"] = self.__interpret_status(response["response_status"])

        # Printa o resultado
        print(f"Response ID: {response['response_id']}")
        self.log_file.write(f"Response ID: {response['response_id']}\n")

        print(f"Response Status: {response['response_status']}")
        self.log_file.write(f"Response Status: {response['response_status']}\n")

        print(f"Response Body Length: {response['response_body_length']}")
        self.log_file.write(f"Response Body Length: {response['response_body_length']}\n")

        print(f"Response Body Content: {response['response_body_content']}")
        self.log_file.write(f"Response Body Content: {response['response_body_content']}\n")


    # Function that sends the pause machine command to the server
    def __send_pause_machine_command(self):

        # Formata o comando
        command = self.__format_command(self.command_id, 0x1, 0x7, b"")
        self.command_id += 1

        # Envia o comando
        self.client_socket.send(command)

        # Recebe a resposta
        response = self.client_socket.recv(1024)

        # Processa a resposta
        response = self.__deformat_response(response)

        # Interpreta o status
        response["response_status"] = self.__interpret_status(response["response_status"])

        # Printa o resultado
        print(f"Response ID: {response['response_id']}")
        self.log_file.write(f"Response ID: {response['response_id']}\n")

        print(f"Response Status: {response['response_status']}")
        self.log_file.write(f"Response Status: {response['response_status']}\n")

        print(f"Response Body Length: {response['response_body_length']}")
        self.log_file.write(f"Response Body Length: {response['response_body_length']}\n")

        print(f"Response Body Content: {response['response_body_content']}")
        self.log_file.write(f"Response Body Content: {response['response_body_content']}\n")


    # Function that sends the unpause machine command to the server
    def __send_unpause_machine_command(self):

        # Formata o comando
        command = self.__format_command(self.command_id, 0x1, 0x8, b"")
        self.command_id += 1

        # Envia o comando
        self.client_socket.send(command)

        # Recebe a resposta
        response = self.client_socket.recv(1024)

        # Processa a resposta
        response = self.__deformat_response(response)

        # Interpreta o status
        response["response_status"] = self.__interpret_status(response["response_status"])

        # Printa o resultado
        print(f"Response ID: {response['response_id']}")
        self.log_file.write(f"Response ID: {response['response_id']}\n")

        print(f"Response Status: {response['response_status']}")
        self.log_file.write(f"Response Status: {response['response_status']}\n")

        print(f"Response Body Length: {response['response_body_length']}")
        self.log_file.write(f"Response Body Length: {response['response_body_length']}\n")

        print(f"Response Body Content: {response['response_body_content']}")
        self.log_file.write(f"Response Body Content: {response['response_body_content']}\n")


    # Function that sends the dump memory command to the server
    def __send_dump_memory_command(self):

        # Pergunta o endereço de memória
        memory_address = int(input("Enter the memory address: "))

        # Pergunta o tamanho da memória
        memory_size = int(input("Enter the memory size: "))

        # Formata o comando
        command = self.__format_command(self.command_id, 0x1, 0x9, memory_address.to_bytes(4, byteorder="big") + memory_size.to_bytes(4, byteorder="big"))
        self.command_id += 1

        # Envia o comando
        self.client_socket.send(command)

        # Recebe a resposta
        response = self.client_socket.recv(1024)

        # Processa a resposta
        response = self.__deformat_response(response)

        # Interpreta o status
        response["response_status"] = self.__interpret_status(response["response_status"])

        # Printa o resultado
        print(f"Response ID: {response['response_id']}")
        self.log_file.write(f"Response ID: {response['response_id']}\n")

        print(f"Response Status: {response['response_status']}")
        self.log_file.write(f"Response Status: {response['response_status']}\n")

        print(f"Response Body Length: {response['response_body_length']}")
        self.log_file.write(f"Response Body Length: {response['response_body_length']}\n")

        print(f"Response Body Content: {self.__process_string(response['response_body_content'])}")
        self.log_file.write(f"Response Body Content: {self.__process_string(response['response_body_content'])}\n")


    # Function that sends the quit emulation command to the server
    def __send_quit_emulation_command(self):

        # Formata o comando
        command = self.__format_command(self.command_id, 0x1, 0x0D, b"")
        self.command_id += 1

        # Envia o comando
        self.client_socket.send(command)

        # Recebe a resposta
        response = self.client_socket.recv(1024)

        # Processa a resposta
        response = self.__deformat_response(response)

        # Interpreta o status
        response["response_status"] = self.__interpret_status(response["response_status"])

        # Printa o resultado
        print(f"Response ID: {response['response_id']}")
        self.log_file.write(f"Response ID: {response['response_id']}\n")

        print(f"Response Status: {response['response_status']}")
        self.log_file.write(f"Response Status: {response['response_status']}\n")

        print(f"Response Body Length: {response['response_body_length']}")
        self.log_file.write(f"Response Body Length: {response['response_body_length']}\n")

        print(f"Response Body Content: {response['response_body_content']}")
        self.log_file.write(f"Response Body Content: {response['response_body_content']}\n")


    # Function that sends the configure breakpoint command to the server
    def __send_configure_breakpoint_command(self):

        # Pergunta a linha que será aplicado o breakpoint
        breakpoint = int(input("Enter the line to apply a breakpoint: ")).to_bytes(4, byteorder='big')

        # Formata o comando
        command = self.__format_command(self.command_id, 0x1, 0x0E, breakpoint)
        self.command_id += 1

        # Envia o comando
        self.client_socket.send(command)

        # Recebe a resposta
        response = self.client_socket.recv(1024)

        # Processa a resposta
        response = self.__deformat_response(response)

        # Interpreta o status
        response["response_status"] = self.__interpret_status(response["response_status"])

        # Printa o resultado
        print(f"Response ID: {response['response_id']}")
        self.log_file.write(f"Response ID: {response['response_id']}\n")

        print(f"Response Status: {response['response_status']}")
        self.log_file.write(f"Response Status: {response['response_status']}\n")

        print(f"Response Body Length: {response['response_body_length']}")
        self.log_file.write(f"Response Body Length: {response['response_body_length']}\n")

        print(f"Response Body Content: {response['response_body_content']}")
        self.log_file.write(f"Response Body Content: {response['response_body_content']}\n")

        print("Response Interpretation: %s" % response['response_body_content'].decode('utf-8'))
        self.log_file.write("Response Interpretation: %s\n" % response['response_body_content'].decode('utf-8'))


    # Function that sends the delete breakpoint command to the server
    def __send_delete_breakpoint_command(self):

        # Pergunta o breakpoint a ser deletado para o usuário
        breakpoint = int(input("Enter the breakpoint line to be deleted: "))

        # Formata o comando
        command = self.__format_command(self.command_id, 0x1, 0x0F, breakpoint.to_bytes(4, byteorder='big'))
        self.command_id += 1

        # Envia o comando
        self.client_socket.send(command)

        # Recebe a resposta
        response = self.client_socket.recv(1024)

        # Processa a resposta
        response = self.__deformat_response(response)

        # Interpreta o status
        response["response_status"] = self.__interpret_status(response["response_status"])

        # Printa o resultado
        print(f"Response ID: {response['response_id']}")
        self.log_file.write(f"Response ID: {response['response_id']}\n")

        print(f"Response Status: {response['response_status']}")
        self.log_file.write(f"Response Status: {response['response_status']}\n")

        print(f"Response Body Length: {response['response_body_length']}")
        self.log_file.write(f"Response Body Length: {response['response_body_length']}\n")

        print(f"Response Body Content: {response['response_body_content']}")
        self.log_file.write(f"Response Body Content: {response['response_body_content']}\n")

        print("Response Interpretation: %s" % response['response_body_content'].decode('utf-8'))
        self.log_file.write("Response Interpretation: %s\n" % response['response_body_content'].decode('utf-8'))


    # Function that sends the continue emulation command to the server
    def __send_continue_emulation_command(self):

        # Formata o comando
        command = self.__format_command(self.command_id, 0x1, 0x10, b"")
        self.command_id += 1

        # Envia o comando
        self.client_socket.send(command)

        # Recebe a resposta
        response = self.client_socket.recv(1024)

        # Processa a resposta
        response = self.__deformat_response(response)

        # Interpreta o status
        response["response_status"] = self.__interpret_status(response["response_status"])

        # Printa o resultado
        print(f"Response ID: {response['response_id']}")
        self.log_file.write(f"Response ID: {response['response_id']}\n")

        print(f"Response Status: {response['response_status']}")
        self.log_file.write(f"Response Status: {response['response_status']}\n")

        print(f"Response Body Length: {response['response_body_length']}")
        self.log_file.write(f"Response Body Length: {response['response_body_length']}\n")

        print(f"Response Body Content: {response['response_body_content']}")
        self.log_file.write(f"Response Body Content: {response['response_body_content']}\n")

        print("Response Interpretation: %s" % response['response_body_content'].decode('utf-8'))
        self.log_file.write("Response Interpretation: %s\n" % response['response_body_content'].decode('utf-8'))

    
    # Function that sends the finish execution command
    def __send_finish_execution_command(self):

        # Formata o comando
        command = self.__format_command(self.command_id, 0x1, 0x11, b"")
        self.command_id += 1

        # Envia o comando
        self.client_socket.send(command)

        # Recebe a resposta
        response = self.client_socket.recv(1024)

        # Processa a resposta
        response = self.__deformat_response(response)

        # Interpreta o status
        response["response_status"] = self.__interpret_status(response["response_status"])

        # Printa o resultado
        print(f"Response ID: {response['response_id']}")
        self.log_file.write(f"Response ID: {response['response_id']}\n")

        print(f"Response Status: {response['response_status']}")
        self.log_file.write(f"Response Status: {response['response_status']}\n")

        print(f"Response Body Length: {response['response_body_length']}")
        self.log_file.write(f"Response Body Length: {response['response_body_length']}\n")

        print(f"Response Body Content: {response['response_body_content']}")
        self.log_file.write(f"Response Body Content: {response['response_body_content']}\n")

        print("Response Interpretation: %s" % response['response_body_content'].decode('utf-8'))
        self.log_file.write("Response Interpretation: %s\n" % response['response_body_content'].decode('utf-8'))


    # Function that sends the next line command
    def __send_next_line_command(self):

        # Formata o comando
        command = self.__format_command(self.command_id, 0x1, 0x12, b"")
        self.command_id += 1

        # Envia o comando

        self.client_socket.send(command)

        # Recebe a resposta
        response = self.client_socket.recv(1024)

        # Processa a resposta
        response = self.__deformat_response(response)

        # Interpreta o status
        response["response_status"] = self.__interpret_status(response["response_status"])

        # Printa o resultado
        print(f"Response ID: {response['response_id']}")
        self.log_file.write(f"Response ID: {response['response_id']}\n")

        print(f"Response Status: {response['response_status']}")
        self.log_file.write(f"Response Status: {response['response_status']}\n")

        print(f"Response Body Length: {response['response_body_length']}")
        self.log_file.write(f"Response Body Length: {response['response_body_length']}\n")

        print(f"Response Body Content: {response['response_body_content']}")
        self.log_file.write(f"Response Body Content: {response['response_body_content']}\n")

        print("Response Interpretation: %s" % response['response_body_content'].decode('utf-8'))
        self.log_file.write("Response Interpretation: %s\n" % response['response_body_content'].decode('utf-8'))


    # Function that sends the step into command
    def __send_step_into_command(self):

        # Formata o comando
        command = self.__format_command(self.command_id, 0x1, 0x13, b"")
        self.command_id += 1

        # Envia o comando
        self.client_socket.send(command)

        # Recebe a resposta
        response = self.client_socket.recv(1024)

        # Processa a resposta
        response = self.__deformat_response(response)

        # Interpreta o status
        response["response_status"] = self.__interpret_status(response["response_status"])

        # Printa o resultado
        print(f"Response ID: {response['response_id']}")
        self.log_file.write(f"Response ID: {response['response_id']}\n")

        print(f"Response Status: {response['response_status']}")
        self.log_file.write(f"Response Status: {response['response_status']}\n")

        print(f"Response Body Length: {response['response_body_length']}")
        self.log_file.write(f"Response Body Length: {response['response_body_length']}\n")

        print(f"Response Body Content: {response['response_body_content']}")
        self.log_file.write(f"Response Body Content: {response['response_body_content']}\n")

        print("Response Interpretation: %s" % response['response_body_content'].decode('utf-8'))
        self.log_file.write("Response Interpretation: %s\n" % response['response_body_content'].decode('utf-8'))


    # Function that sends the verify variable command
    def __send_verify_variable_command(self):

        # Pergunta o nome da variável
        variable_name = str(input("Enter the name of the variable: "))

        # Codifica o nome da variável
        variable_name = (variable_name).encode('utf-8')

        # Cria o comando a ser enviado
        command = self.__format_command(self.command_id, 0x1, 0x14, variable_name)
        self.command_id += 1

        # Envia o comando
        self.client_socket.send(command)

        # Recebe a resposta
        response = self.client_socket.recv(1024)

        # Processa a resposta
        response = self.__deformat_response(response)

        # Interpreta o status
        response["response_status"] = self.__interpret_status(response["response_status"])

        # Printa o resultado
        print(f"Response ID: {response['response_id']}")
        self.log_file.write(f"Response ID: {response['response_id']}\n")

        print(f"Response Status: {response['response_status']}")
        self.log_file.write(f"Response Status: {response['response_status']}\n")

        print(f"Response Body Length: {response['response_body_length']}")
        self.log_file.write(f"Response Body Length: {response['response_body_length']}\n")

        print(f"Response Body Content: {self.__process_string(response['response_body_content'])}")
        self.log_file.write(f"Response Body Content: {self.__process_string(response['response_body_content'])}\n")

        print("Response Interpretation: %s" % response['response_body_content'].decode('utf-8'))
        self.log_file.write("Response Interpretation: %s\n" % response['response_body_content'].decode('utf-8'))


    # Function that sends the GDB command to the server
    def __send_gdb_command(self):

        # Pergunta o comando GDB
        gdb_command = str(input("Enter the GDB command: "))

        # Codifica o comando GDB
        gdb_command = gdb_command.encode('utf-8')
    
        # Formata o comando
        command = self.__format_command(self.command_id, 0x1, 0x15, gdb_command)
        self.command_id += 1

        # Envia o comando
        self.client_socket.send(command)

        # Recebe a resposta
        response = self.client_socket.recv(1024)

        # Processa a resposta
        response = self.__deformat_response(response)

        # Interpreta o status
        response["response_status"] = self.__interpret_status(response["response_status"])

        # Printa o resultado
        print(f"Response ID: {response['response_id']}")
        self.log_file.write(f"Response ID: {response['response_id']}\n")

        print(f"Response Status: {response['response_status']}")
        self.log_file.write(f"Response Status: {response['response_status']}\n")

        print(f"Response Body Length: {response['response_body_length']}")
        self.log_file.write(f"Response Body Length: {response['response_body_length']}\n")

        print(f"Response Body Content: {self.__process_string(response['response_body_content'])}")
        self.log_file.write(f"Response Body Content: {self.__process_string(response['response_body_content'])}\n")

        print("Response Interpretation: %s" % response['response_body_content'].decode('utf-8'))
        self.log_file.write("Response Interpretation: %s\n" % response['response_body_content'].decode('utf-8'))
        


    # Function that sends an arbitrary command to the server
    def __send_random_command(self):

        # Pergunta o comando a ser enviado
        arbitrary_command = input("Enter the arbitrary command: ")

        # Codifica o comando
        arbitrary_command = self.__process_bytes(arbitrary_command)
        
        self.command_id += 1

        # Envia o comando
        print("Command sent: ", arbitrary_command)
        self.client_socket.send(arbitrary_command)

        # Recebe a resposta
        response = self.client_socket.recv(1024)

        # Processa a resposta
        response = self.__deformat_response(response)

        # Interpreta o status
        response["response_status"] = self.__interpret_status(response["response_status"])

        # Printa o resultado
        print(f"Response ID: {response['response_id']}")
        self.log_file.write(f"Response ID: {response['response_id']}\n")

        print(f"Response Status: {response['response_status']}")
        self.log_file.write(f"Response Status: {response['response_status']}\n")

        print(f"Response Body Length: {response['response_body_length']}")
        self.log_file.write(f"Response Body Length: {response['response_body_length']}\n")

        print(f"Response Body Content: {self.__process_string(response['response_body_content'])}")
        self.log_file.write(f"Response Body Content: {self.__process_string(response['response_body_content'])}\n")


    # Function that sends the read I/O command to the server
    def __send_read_io_command(self):
        # Pergunta o endereço de I/O
        io_address = int(input("Enter the I/O address: "))

        # Formata o comando
        command = self.__format_command(self.command_id, 0x1, 0x0B, io_address.to_bytes(4, byteorder="big"))
        self.command_id += 1

        # Envia o comando
        self.client_socket.send(command)

        # Recebe a resposta
        response = self.client_socket.recv(1024)

        # Processa a resposta
        response = self.__deformat_response(response)

        # Interpreta o status
        response["response_status"] = self.__interpret_status(response["response_status"])

        # Printa o resultado
        print(f"Response ID: {response['response_id']}")
        self.log_file.write(f"Response ID: {response['response_id']}\n")

        print(f"Response Status: {response['response_status']}")
        self.log_file.write(f"Response Status: {response['response_status']}\n")

        print(f"Response Body Length: {response['response_body_length']}")
        self.log_file.write(f"Response Body Length: {response['response_body_length']}\n")

        print(f"Response Body Content: {self.__process_string(response['response_body_content'])}")
        self.log_file.write(f"Response Body Content: {self.__process_string(response['response_body_content'])}\n")


    # Function that sends the write I/O command to the server
    def __send_write_io_command(self):
        # Pergunta o endereço de I/O
        io_address = int(input("Enter the I/O address: "))

        # Pergunta o valor a ser escrito
        io_value = int(input("Enter the value to be written: "))

        # Formata o comando
        command_body = io_address.to_bytes(4, byteorder="big") + io_value.to_bytes(4, byteorder="big")
        command = self.__format_command(self.command_id, 0x1, 0x0C, command_body)
        self.command_id += 1

        # Envia o comando
        self.client_socket.send(command)

        # Recebe a resposta
        response = self.client_socket.recv(1024)

        # Processa a resposta
        response = self.__deformat_response(response)

        # Interpreta o status
        response["response_status"] = self.__interpret_status(response["response_status"])

        # Printa o resultado
        print(f"Response ID: {response['response_id']}")
        self.log_file.write(f"Response ID: {response['response_id']}\n")

        print(f"Response Status: {response['response_status']}")
        self.log_file.write(f"Response Status: {response['response_status']}\n")

        print(f"Response Body Length: {response['response_body_length']}")
        self.log_file.write(f"Response Body Length: {response['response_body_length']}\n")

        print(f"Response Body Content: {self.__process_string(response['response_body_content'])}")
        self.log_file.write(f"Response Body Content: {self.__process_string(response['response_body_content'])}\n")

    def __hex_to_bytes(self, hex_string: str) -> bytes:
        """
        Converte string no formato 'AA BB CC 01 02' para bytes reais.
        """
        hex_string = hex_string.replace(" ", "")  # remove espaços
        return bytes.fromhex(hex_string)

    # Function that sends an err inject command to the server
    def __send_err_inject_command(self):

        # Pergunta o endereço de I/O
        err_inject_payload = input("Enter the err inject payload command: ")

        # Formata o comando
        command = self.__format_command(self.command_id, 0x1, 0x16, self.__hex_to_bytes(err_inject_payload))
        self.command_id += 1

        # Envia o comando
        self.client_socket.send(command)

        # Recebe a resposta
        response = self.client_socket.recv(1024)

        # Processa a resposta
        response = self.__deformat_response(response)

        # Interpreta o status
        response["response_status"] = self.__interpret_status(response["response_status"])

        # Printa o resultado
        print(f"Response ID: {response['response_id']}")
        self.log_file.write(f"Response ID: {response['response_id']}\n")

        print(f"Response Status: {response['response_status']}")
        self.log_file.write(f"Response Status: {response['response_status']}\n")

        print(f"Response Body Length: {response['response_body_length']}")
        self.log_file.write(f"Response Body Length: {response['response_body_length']}\n")

        print(f"Response Body Content: {self.__process_string(response['response_body_content'])}")
        self.log_file.write(f"Response Body Content: {self.__process_string(response['response_body_content'])}\n")

        
    # Function that resets a connection to the control interface
    def __restart_connection(self):

        # Closes the socket with the client
        self.client_socket.close()

        # Waits for a certain amount of time
        time.sleep(1)

        # Reconnects again
        self.client_socket = socket.socket(DOCKER_SOCKET_FAMILY, DOCKER_SOCKET_TYPE)
        self.client_socket.connect((DOCKER_HOST, DOCKER_PORT))

        # Sets the timeout for the socket
        self.client_socket.settimeout(TEST_TIMEOUT)

        # Logs the operation
        print("The connection has been reset!")
        self.log_file.write("The connection has been reset!")

    # Function that writes the packet sent to a .csv file
    def __write_packet_sent_csv(self, command, response):
    
        # Define the CSV file path
        csv_file_path = "packets_log.csv"

        # Define the header for the CSV file
        header = ["Command ID", "Command Machine State", "Command Type", "Command Body Length", "Command Body Content", "Command CRC",
                  "Response ID", "Response Status", "Response Body Length", "Response Body Content", "Response CRC"]

        # Deformat the command and response
        command_parts = self.__deformat_response(command)
        response_parts = self.__deformat_response(response)

        # Prepare the row to be written
        row = [
            command_parts["response_id"],
            command_parts["response_status"],
            command_parts["response_body_length"],
            self.__process_string(command_parts["response_body_content"]),
            command_parts["response_CRC"],
            response_parts["response_id"],
            response_parts["response_status"],
            response_parts["response_body_length"],
            self.__process_string(response_parts["response_body_content"]),
            response_parts["response_CRC"]
        ]

        # Check if the CSV file exists
        file_exists = os.path.isfile(csv_file_path)

        # Open the CSV file in append mode
        with open(csv_file_path, mode='a', newline='') as file:
            writer = csv.writer(file)

            # Write the header if the file does not exist
            if not file_exists:
                writer.writerow(header)

            # Write the row
            writer.writerow(row)

        

    # Function that runs the test
    def __run_test(self):

        # Initiates the decision variable
        decision = 1

        while decision != 0:

            # Prints the menu
            decision = self.__print_menu()

            # Calls the desired function
            self.test_functions[decision]()

            # The packte was sent successfully, so put the intere packet was sent in .csv file and the response packet was received in .csv file
            #self.__write_packet_sent_csv()

            # Waits for a input to continue
            input("\nPress Enter to continue...")

            # Clears the screen
            os.system('clear')

        # Closes the log file
        self.log_file.close()
            

    def __print_menu(self):

        # Prints the menu
        print("\n\nWelcome to QEMULA test menu!\n\n")

        print("** General Commands **\n")

        print("0 - Exit")
        print("1 - Send Verify State Command")
        print("2 - Restart Connection")

        print("\n** CONFIG Commands **\n")

        print("3 - Send Inject .ELF Command")
        print("4 - Send Inject AHBROM Command")
        print("5 - Send Config RAM Command")
        print("6 - Send Config Debug Command")
        print("7 - Send Set OS ABI for Debug Command")
        print("8 - Send Start Emulation Command")
        print("24 - Send Inject CONFIG Command")

        print("\n** RUN Commands **\n")

        print("9 - Send Pause Machine Command")
        print("10 - Send Unpause Machine Command")
        print("11 - Send Dump Memory Command")
        print("12 - Send Quit Emulation Command")
        print("13 - Send Configure Breakpoint Command")
        print("14 - Send Delete Breakpoint Command")
        print("15 - Send Continue Emulation Command")
        print("16 - Send Finish Execution Command")
        print("17 - Send Next Line Command")
        print("18 - Send Step Into Command")
        print("19 - Send Verify Variable Command")
        print("20 - Send GDB Command")
        print("21 - Send Arbitrary Command")
        print("22 - Send Read I/O Command (addr)")
        print("23 - Send Write I/O Command (addr, value)")
        print("25 - Send Err Inject Command")
        

        print("\n")

        # Gets the user input
        decision = int(input("Enter the desired option: "))

        # Processes the user input
        return decision


##################################################################################################################################################################################


##################################################################################################################################################################################
# Main Function

if __name__ == "__main__":

    # Initializes the test class
    test = Protocol_Test()

    print("\nTest finished. Exiting...")

