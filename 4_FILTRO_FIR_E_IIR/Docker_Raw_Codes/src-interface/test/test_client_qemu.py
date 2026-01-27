##########################################################################################################################################################
# Import de bibliotecas necessárias

import socket
import subprocess
import threading
import time
import pexpect
import re
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

##########################################################################################################################################################


##########################################################################################################################################################
# Definição de constantes importantes

# Tabela de Comandos
# | MACHINE_STATE |        COMMAND_TYPE         |                 BODY_CONTENT                  |
# | :-----------: | :-------------------------: | :-------------------------------------------: |
# |      0xX      |     0x00 (Verify State)     |                       -                       |
# | 0x0 (CONFIG)  |     0x01 (Inject .ELF)      |                 .ELF Binaries                 |
# | 0x0 (CONFIG)  |     0x02 (Inject AHBROM Mem file)      |                 AHBROM Binaries                 |
# | 0x0 (CONFIG)  |      0x03 (Config RAM)      |                   RAM in MB                   |
# | 0x0 (CONFIG)  |     0x04 (Config Debug)     |    0x0 - Without Debug / 0x1 - With Debug and with a discrete interface / 0x2 - With Debug and with implicit interface     
# | 0x0 (CONFIG)  | 0x05 (Set OS ABI for Debug) |     GDB OS ABI in utf-8 (default is none)     ||
# | 0x0 (CONFIG)  |   0x06 (Start Emulation)    |                       -                       |
# |   0x1 (RUN)   |    0x07 (Pause Machine)     |                       -                       |
# |   0x1 (RUN)   |   0x08 (Unpause Machine)    |                       -                       |
# |   0x1 (RUN)   |     0x09 (Dump Memory)      |       0xXXXXXXXX - Mem ADDR + Mem DATA        |
# |   0x1 (RUN)   |     0x0A (Load Memory)      | 0xXXXXXXXX - Mem ADDR + Mem Length (in bytes) |
# |   0x1 (RUN)   |       0x0B (Read I/O)       |             0xXXXXXXXX - Mem ADDR             |
# |   0x1 (RUN)   |      0x0C (Write I/O)       |     0xXXXXXXXX - Mem ADDR + 0xX IO Value      |
# |   0x1 (RUN)   |    0x0D (Quit Emulation)    |                       -                       |
# |   0x1 (RUN)   | 0x0E (Configure Breakpoint) |              Breakpoint Line Num              |
# |   0x1 (RUN)   |  0x0F (Delete Breakpoint)   |              Breakpoint Line Num              |
# |   0x1 (RUN)   |  0x10 (Continue Emulation)  |              -              |
# |   0x1 (RUN)   |  0x11 (Finish Execution)  |              -              |
# |   0x1 (RUN)   |  0x12 (Next Line)           |              -               |
# |   0x1 (RUN)   |  0x13 (Step Into)           |              -               |
# |   0x1 (RUN)   |  0x14 (Verify Variable)     |              Variable Name in utf-8
# |   0x1 (RUN)   |   0x15 (Send GDB Command)   |             GDB Command in utf-8              |

# Constantes de Configuração
CONFIG_TABLE_DEBUG = {"yes": "-s -S", "no": ""}
QEMU_MONITOR_PORT = 4444

QEMU_INST_PORT1 = 5050
QEMU_INST_PORT2 = 5151


# Constantes para determinação dos erros
QEMU_ERROR = 0x00
EXECUTED_SUCCESSFULLY = 0x01
CRC_ERROR = 0x02
INVALID_COMMAND = 0x03
INVALID_BODY_CONTENT = 0x04
TIME_OUT = 0x05
INVALID_MACHINE_STATE = 0x06
INVALID_COMMAND_ID = 0x07
INVALID_LEN = 0x08


# Constantes de determinação do estado da máquina
MACHINE_STATE_CONFIG = 0x00
MACHINE_STATE_RUN = 0x01


# Constantes para condições de contorno
MAX_AHBROM_SIZE = 0x10000000

##########################################################################################################################################################


##########################################################################################################################################################
# Classe de Emulação do QEMU

class QemuEmulator:

    def __init__(self):

        # Valores de variáveis referentes à operação do QEMU
        self.memory_value = None
        self.debug_value = None
        self.debug_interface_value = None
        self.osabi_value = 'none'
        self.breakpoint_list = []
        self.breakpoint_count = 1



        # Objetos importantes para as manipulações das funções do QEMU
        self.monitor_socket = None
        self.gdb_object = None
        self.current_state = MACHINE_STATE_CONFIG

        # Flags de controle
        self.kernel_loaded = False



    def __open_monitor_socket(self):

        try:
            self.monitor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.monitor_socket.connect(('0.0.0.0', QEMU_MONITOR_PORT))

            self.monitor_socket.recv(1024)

        except ConnectionRefusedError:
            print(f"Erro: A conexão foi recusada. Certifique-se de que o QEMU está rodando e ouvindo na porta {self.port}.")
        except socket.error as e:
            print(f"Erro de socket: {e}")


    def __open_debug_socket(self):

        # Inicia o comando de abertura do gdb, baseanndo-se no pexpect
        self.gdb_object = pexpect.spawn(f"sparc-gaisler-elf-gdb")
        self.gdb_object.logfile = None
        self.gdb_object.timeout = 1
        self.gdb_object.expect_exact("(gdb)")

        # Seta as opções do gdb para compilação do kernel, carregando os seus símbolos
        self.gdb_object.sendline("file kernel")
        self.gdb_object.expect_exact("(gdb)")

        self.gdb_object.sendline("set osabi " + self.osabi_value)
        self.gdb_object.expect_exact("(gdb)")

        # Conecta o gdb ao QEMU
        self.gdb_object.sendline("target remote localhost:1234")
        self.gdb_object.expect_exact("(gdb)")


    def start_emulation(self, body_content):

        # Caso o sistema esteja em estado de run, o comando é inválido
        if self.current_state == MACHINE_STATE_RUN:
                
                return (INVALID_MACHINE_STATE, None)

        # Caso o body_content seja diferente de None, o body content do comando é inválido
        if body_content != b'':

            # Permanece em estado de configuração
            self.current_state = MACHINE_STATE_CONFIG

            # Retorna o erro de INVALID_BODY_CONTENT
            return (INVALID_BODY_CONTENT, None)
        
        # Caso a memória ou o debug não tenham sido configurados
        if self.memory_value is None or self.debug_value is None or self.kernel_loaded is False:

            # Permanece em estado de configuração
            self.current_state = MACHINE_STATE_CONFIG

            # Retorna o erro de INVALID_BODY_CONTENT
            return (QEMU_ERROR, None)
        
        command = (
	    f"./qemu-system-sparc-uarts -M leon3_generic -m {self.memory_value}M {self.debug_value} -nographic -no-reboot "
	    f"-chardev socket,id=mon1,host=0.0.0.0,port={QEMU_MONITOR_PORT},server=on,wait=on -mon chardev=mon1 -kernel kernel "
	    f"-serial tcp:0.0.0.0:{QEMU_INST_PORT1},server=on,wait=off -serial tcp:0.0.0.0:{QEMU_INST_PORT2},server=on,wait=off"
	    )

        def run_qemu():

            # Transiciona para o estado de RUNNING
            self.current_state = MACHINE_STATE_RUN

            # Executa o comando do QEMU
            subprocess.run(command, shell=True)

            # Transiciona para o estado de CONFIG
            self.current_state = MACHINE_STATE_CONFIG

            return
        
        # Inicializa a thread de execução do QEMU
        thread = threading.Thread(target=run_qemu, args=())
        thread.start()

        time.sleep(1)

        # Abre o socket de monitoramento
        self.__open_monitor_socket()

        # Caso a opção de debug esteja ativada, conecta-se ao gdb
        if self.debug_value == "-s -S" and self.debug_interface_value == False:
           self.__open_debug_socket()
            
        return (EXECUTED_SUCCESSFULLY, None)


    # Função para terminar a emulação
    def quit_emulation(self, body_content):

        # Caso o sistema esteja em estado de configuração, o comando é inválido
        if self.current_state == MACHINE_STATE_CONFIG:
                    
                    return (INVALID_MACHINE_STATE, None)

        # Caso o body_content seja diferente de None, o body content do comando é inválido
        if body_content != b'':
                return (INVALID_BODY_CONTENT, None)

        try:

            # Envia o Comando para o QEMU, fechando o socket
            self.monitor_socket.sendall('q\n'.encode('utf-8'))
            time.sleep(1)
            self.monitor_socket.close()
            
            # Caso o gdb esteja ativo, fecha
            if self.debug_value == "-s -S":
                self.gdb_object.close()

            return (EXECUTED_SUCCESSFULLY, None)
        
        except Exception as e:
            return (QEMU_ERROR, None)


    # Função para configurar a RAM
    def config_ram(self, body_content):
        
        # Caso o sistema esteja em estado de run, o comando é inválido
        if self.current_state == MACHINE_STATE_RUN:
                
                return (INVALID_MACHINE_STATE, None)

        # Obtém o valor da memória
        memory_value_int = int.from_bytes(body_content, byteorder='big')

        # Caso a memória seja múltipla de 4 e não seja nula
        if memory_value_int % 4 == 0 and memory_value_int != 0:

            # Configura o valor da memória
            self.memory_value = memory_value_int

            return (EXECUTED_SUCCESSFULLY, None)

        # Caso contrário, é inválida
        else:
            return (INVALID_BODY_CONTENT, None)


    # Função para injetar um arquivo .ELF
    def inject_elf(self, body_content):

        # Caso o sistema esteja em estado de run, o comando é inválido
        if self.current_state == MACHINE_STATE_RUN:
                
                return (INVALID_MACHINE_STATE, None)

        # Caso o body_content seja None, o comando é inválido
        if body_content == b'':
            return (INVALID_BODY_CONTENT, None)
        
        # Caso o body_content seja diferente de None, o comando é válido
        try:
            
            # Escreve o conteúdo do body_content no arquivo kernel
            with open("kernel", "wb") as f:
                f.write(body_content)

            # Seta a flag de kernel
            self.kernel_loaded = True

            return (EXECUTED_SUCCESSFULLY, None)

        # Caso ocorra uma exceção, o comando é inválido
        except Exception as e:
            return (QEMU_ERROR, None)


    # Função para injetar um arquivo da AHBROM
    def inject_ahbrom(self, body_content):

        # Caso o sistema esteja em estado de run, o comando é inválido
        if self.current_state == MACHINE_STATE_RUN:
                
                return (INVALID_MACHINE_STATE, None)

        # Caso o body_content seja None, o comando é inválido
        if len(body_content) > MAX_AHBROM_SIZE:
            return (INVALID_BODY_CONTENT, None)

        # Caso o body_content seja diferente de None, o comando é válido
        try:
            
            # Escreve o conteúdo do body_content no arquivo kernel
            with open("ahbrom", "wb") as f:
                f.write(body_content)

            # Seta a flag de kernel
            self.kernel_loaded = True

            return (EXECUTED_SUCCESSFULLY, None)

        # Caso ocorra uma exceção, o comando é inválido
        except Exception as e:
            return (QEMU_ERROR, None)
        

    # Função para configurar o modo de debug
    def config_debug(self, body_content):
        
        # Caso o sistema esteja em estado de run, o comando é inválido
        if self.current_state == MACHINE_STATE_RUN:

            return (INVALID_MACHINE_STATE, None)

        # Caso seja configurado para modo de debug com interface
        if int.from_bytes(body_content, byteorder='big') == 1:

            self.debug_value = CONFIG_TABLE_DEBUG["yes"]
            self.debug_interface_value = True

            return (EXECUTED_SUCCESSFULLY, None)

        # Caso não seja configurado para modo de debug
        elif int.from_bytes(body_content, byteorder='big') == 0:

            self.debug_value = CONFIG_TABLE_DEBUG["no"]
            self.debug_interface_value = False

            return (EXECUTED_SUCCESSFULLY, None)

        # Caso seja configurado para modo de debug com interface implícita
        elif int.from_bytes(body_content, byteorder='big') == 2:

            self.debug_value = CONFIG_TABLE_DEBUG["yes"]
            self.debug_interface_value = False

            return (EXECUTED_SUCCESSFULLY, None)

        # Caso seja inválido
        else:

            return (INVALID_BODY_CONTENT, None)
        

    # Função para configurar o OS ABI
    def set_osabi(self, body_content):

        # Caso o sistema esteja em estado de run, o comando é inválido
        if self.current_state == MACHINE_STATE_RUN:

            return (INVALID_MACHINE_STATE, None)

        # Caso o body_content seja none, o comando é inválido
        if body_content == b'':

            return (INVALID_BODY_CONTENT, None)
        
        # Seta o OS ABI, decodificando o body_content
        self.osabi_value = body_content.decode('utf-8')

        return (EXECUTED_SUCCESSFULLY, None)


    # Função para obter o estado atual
    def get_current_state(self, body_content):

        # Caso o body_content seja diferente de None, o body content do comando é inválido
        if body_content != b'':
            return (INVALID_BODY_CONTENT, None)

        return (EXECUTED_SUCCESSFULLY, self.current_state.to_bytes(1, byteorder='big'))
        
        
    # Função para pausar a emulação
    def pause_emulation(self, body_content):

        # Caso o sistema esteja em estado de configuração, o comando é inválido
        if self.current_state == MACHINE_STATE_CONFIG:
                
                return (INVALID_MACHINE_STATE, None)

        # Caso o body_content seja diferente de None, o body content do comando é inválido
        if body_content != b'':

            return (INVALID_BODY_CONTENT, None)

        # Envia o comando para pausar a emulação
        try:
            self.monitor_socket.sendall('s\n'.encode('utf-8'))
            self.monitor_socket.recv(1024)

            return (EXECUTED_SUCCESSFULLY, None)

        # Caso ocorra uma exceção, o comando é inválido
        except Exception as e:

            return (QEMU_ERROR, None)


    # Função para despausar a emulação
    def unpause_emulation(self, body_content):

        # Caso o sistema esteja em estado de configuração, o comando é inválido
        if self.current_state == MACHINE_STATE_CONFIG:

            return (INVALID_MACHINE_STATE, None)

        # Caso o body_content seja diferente de None, o body content do comando é inválido
        if body_content != b'':

            return (INVALID_BODY_CONTENT, None)

        # Envia o comando para pausar a emulação
        try:
            self.monitor_socket.sendall('c\n'.encode('utf-8'))
            self.monitor_socket.recv(1024)

            return (EXECUTED_SUCCESSFULLY, None)

        # Caso ocorra uma exceção, o comando é inválido
        except Exception as e:

            return (QEMU_ERROR, None)
        


    # Função para ler a memória
    def dump_memory(self, body_content):

        # Caso o sistema esteja em estado de configuração, o comando é inválido
        if self.current_state == MACHINE_STATE_CONFIG:

            return (INVALID_MACHINE_STATE, None)

        # Caso o tamanho do body_content seja menor que 5, o body content do comando é inválido
        if len(body_content) < 5:
                
                return (INVALID_BODY_CONTENT, None)

        # Processa o body_content recebido, em MEM_ADDR e MEM_DATA
        try:

            # Obtém o tamanho e o addr
            addr = body_content[:4].hex().zfill(8)
            size = str(int(body_content[4:].hex(), 16))

            # Envia o comando para o QEMU
            self.monitor_socket.sendall(f'xp/{size}xb 0x{addr}\n'.encode('utf-8'))

            time.sleep(0.5)      

            # Recebe a resposta do QEMU
            body_content = self.monitor_socket.recv(self.monitor_socket.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)).decode('utf-8')

            # Caso não haja ':" no body_content, o comando falhou
            if "Cannot" in body_content or ":" not in body_content:

                return (QEMU_ERROR, None)

            # Lendo a entrada de dados o body content só é lido depois dos ":" e do espaço deve ser feito para todas as linhas com um for
            lines = body_content.split('\n')
            packet = []

            for line in lines:
                if ": " in line:
                    packet.extend(line.split(": ", 1)[1].split(' '))

            # Converta todos os elementos da lista de inteiros para elementos de um byte de tamanho
            byte_list = [int(item, 16).to_bytes(1, byteorder='big') for item in packet]
            byte_list = b''.join(byte_list)
            
            return (EXECUTED_SUCCESSFULLY, byte_list)
        
        except Exception as e:

            return (QEMU_ERROR, None)
        
    
    # Função para configurar um breakpoint via GDB
    def configure_breakpoint(self, body_content):

        # Caso o sistema esteja em estado de configuração, o comando é inválido
        if self.current_state == MACHINE_STATE_CONFIG:

            return (INVALID_MACHINE_STATE, None)

        # Caso o tamanho do body_content seja nulo, o body content do comando é inválido
        if len(body_content) == 0:
                
            return (INVALID_BODY_CONTENT, None)
        
        # Caso o debug não esteja ativado, o comando é inválido
        if self.debug_value != "-s -S" and self.debug_interface_value != False:

            return (QEMU_ERROR, None)


        # Transforma o breakpoint em inteiro, adicionando-o na lista
        breakpoint = int.from_bytes(body_content, byteorder='big')
        self.breakpoint_list.append((breakpoint, self.breakpoint_count))
        self.breakpoint_count += 1

        # Cria o conteudo em bytes a ser enviado para o gdb
        command_string = ("b %i" % breakpoint).encode("utf-8")

        # Envia o comando a partir do send_gdb
        (command_status, response) = self.send_gdb_command(command_string)

        # Retorna o resultado da execução do comando
        return (command_status, response)
    

    def delete_breakpoint(self, body_content):

        # Caso o sistema esteja em estado de configuração, o comando é inválido
        if self.current_state == MACHINE_STATE_CONFIG:

            return (INVALID_MACHINE_STATE, None)

        # Caso o tamanho do body_content seja nulo, o body content do comando é inválido
        if len(body_content) == 0:
                    
            return (INVALID_BODY_CONTENT, None)
        
        # Caso o debug não esteja ativado, o comando é inválido
        if self.debug_value != "-s -S" and self.debug_interface_value != False:

            return (QEMU_ERROR, None)

        # Envia um caractere de interrupção para o gdb
        self.gdb_object.sendintr()
        self.gdb_object.expect_exact("(gdb)")

        # Obtém o breakpoint a ser deletado
        breakpoint = int.from_bytes(body_content, byteorder='big')

        # Obtém a contagem do breakpoint
        try:

            breakpoint_count = [item for item in self.breakpoint_list if item[0] == breakpoint][0][1]

            # Remove o breakpoint da lista
            self.breakpoint_list = [item for item in self.breakpoint_list if item[0] != breakpoint]

        # Caso o breakpoint ainda não tenha sido configurado
        except:

            return (QEMU_ERROR, None)

        # Deleta o breakpoint na linha específica
        try:

            self.gdb_object.sendline(f"del {str(breakpoint_count)}")
            self.gdb_object.expect_exact("(gdb)")

            return (EXECUTED_SUCCESSFULLY, None)

        # Caso ocorra uma exceção, o comando é inválido
        except Exception as e:

            return (QEMU_ERROR, None)
    

    # Função para continuar a execução via GDB
    def continue_execution(self, body_content):

        # Caso o sistema esteja em estado de configuração, o comando é inválido
        if self.current_state == MACHINE_STATE_CONFIG:

            return (INVALID_MACHINE_STATE, None)

        # Caso o tamanho do body_content seja nulo, o body content do comando é inválido
        if len(body_content) != 0:
                    
            return (INVALID_BODY_CONTENT, None)
        
        # Caso o debug não esteja ativado, o comando é inválido
        if self.debug_value != "-s -S" and self.debug_interface_value != False:

            return (QEMU_ERROR, None)

        try:

            # Envia um caractere de interrupção para o gdb
            self.gdb_object.sendintr()
            self.gdb_object.expect_exact("(gdb)")

            # Transforma a string de continuação para bytes
            self.gdb_object.sendline('c')
            self.gdb_object.expect_exact("(gdb)")
        
            return (EXECUTED_SUCCESSFULLY, (self.gdb_object.before.decode('utf-8').partition('\n')[2]).encode('utf-8'))

        except Exception as e:

            return (QEMU_ERROR, None)
    

    # Função para finalizar a execução de uma função via GDB
    def finish_execution(self, body_content):

        # Caso o sistema esteja em estado de configuração, o comando é inválido
        if self.current_state == MACHINE_STATE_CONFIG:

            return (INVALID_MACHINE_STATE, None)

        # Caso o tamanho do body_content seja nulo, o body content do comando é inválido
        if len(body_content) != 0:
                    
            return (INVALID_BODY_CONTENT, None)
        
        # Caso o debug não esteja ativado, o comando é inválido
        if self.debug_value != "-s -S" and self.debug_interface_value != False:

            return (QEMU_ERROR, None)

        # Transforma a string de término para bytes
        command_string = "fin".encode("utf-8")

        # Envia o comando para o gdb, recebendo uma resposta
        (command_status, response) = self.send_gdb_command(command_string)
        
        return (command_status, response)
    

    # Função para ler a próxima linha via GDB
    def next_line(self, body_content):

        # Caso o sistema esteja em estado de configuração, o comando é inválido
        if self.current_state == MACHINE_STATE_CONFIG:

            return (INVALID_MACHINE_STATE, None)

        # Caso o tamanho do body_content seja nulo, o body content do comando é inválido
        if len(body_content) != 0:
                    
            return (INVALID_BODY_CONTENT, None)
        
        # Caso o debug não esteja ativado, o comando é inválido
        if self.debug_value != "-s -S" and self.debug_interface_value != False:

            return (QEMU_ERROR, None)

        # Transforma a string de pula linha para bytes
        command_string = "n".encode("utf-8")

        # Envia o comando para o gdb, recebendo uma resposta
        (command_status, response) = self.send_gdb_command(command_string)

        # Retorna o valor
        return (command_status, response)
    

    # Função para entrar em uma função via GDB
    def step_into(self, body_content):

        # Caso o sistema esteja em estado de configuração, o comando é inválido
        if self.current_state == MACHINE_STATE_CONFIG:

            return (INVALID_MACHINE_STATE, None)

        # Caso o tamanho do body_content seja nulo, o body content do comando é inválido
        if len(body_content) != 0:
                    
            return (INVALID_BODY_CONTENT, None)
        
        # Caso o debug não esteja ativado, o comando é inválido
        if self.debug_value != "-s -S" and self.debug_interface_value != False:

            return (QEMU_ERROR, None)

        # Transforma a string de entrar para bytes
        command_string = "s".encode("utf-8")

        # Envia o comando para o gdb, recebendo uma resposta
        (command_status, response) = self.send_gdb_command(command_string)

        # Retorna o valor
        return (command_status, response)
    

    # Função para verificar uma variável via GDB
    def verify_variable(self, body_content):

        # Caso o sistema esteja em estado de configuração, o comando é inválido
        if self.current_state == MACHINE_STATE_CONFIG:

            return (INVALID_MACHINE_STATE, None)

        # Caso o tamanho do body_content seja nulo, o body content do comando é inválido
        if len(body_content) == 0:
                    
            return (INVALID_BODY_CONTENT, None)
        
        # Caso o debug não esteja ativado, o comando é inválido
        if self.debug_value != "-s -S" and self.debug_interface_value != False:

            return (QEMU_ERROR, None)

        # Obtém a string de envio de comando para o gdb
        command_string = "p ".encode("utf-8") + body_content

        # Envia o comando para o gdb, recebendo uma resposta
        (command_status, response) = self.send_gdb_command(command_string)

        # Retorna o valor
        return (command_status, response)


    # Função para enviar um comando qualquer para o GDB
    def send_gdb_command(self, body_content):

        # Caso o sistema esteja em estado de configuração, o comando é inválido
        if self.current_state == MACHINE_STATE_CONFIG:

            return (INVALID_MACHINE_STATE, None)

        # Caso o tamanho do body_content seja nulo, o body content do comando é inválido
        if len(body_content) == 0:
                    
            return (INVALID_BODY_CONTENT, None)
        
        # Caso o debug não esteja ativado, o comando é inválido
        if self.debug_value != "-s -S" and self.debug_interface_value != False:

            return (QEMU_ERROR, None)

        try:

            # Envia um caractere de interrupção para o gdb
            self.gdb_object.sendintr()
            self.gdb_object.expect_exact("(gdb)")

            # Envia o comando para o gdb
            self.gdb_object.sendline(body_content.decode('utf-8'))
            self.gdb_object.expect_exact("(gdb)")

            # Obtém a resposta do gdb
            response = self.gdb_object.before.decode('utf-8').partition('\n')[2]

            # Remove os caracteres de escape ANSI
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            response = ansi_escape.sub('', response)

            # Converte a resposta para bytes
            response = response.encode('utf-8')

            return (EXECUTED_SUCCESSFULLY, response)

        except Exception as e:

            return (QEMU_ERROR, None)

    # Função para separar o body_content em partes de 2 bytes
    def split_body_content(self, body_content, control):
        # Divide o body_content a cada 2 bytes
        byte_array = [body_content[i:i+control] for i in range(0, len(body_content), control)]
        return byte_array

    # Função para escrever em um I/O
# Função para ler de um I/O
    def read_IO(self, body_content):

        # Caso o sistema esteja em estado de configuração, o comando é inválido
        if self.current_state == MACHINE_STATE_CONFIG:
            return (INVALID_MACHINE_STATE, None)

        # Caso o tamanho do body_content seja nulo, o body content do comando é inválido
        if len(body_content) == 0:
            return (INVALID_BODY_CONTENT, None)

        # Inicializa um byte array para armazenar as respostas
        accumulated_response = bytearray()

        # Processa o body_content recebido, em MEM_ADDR
        try:
            # Obtém o addr
            byte_array = self.split_body_content(body_content, 2)
            
            for i in range(len(byte_array)):
                addr = byte_array[i].hex()

                # Envia o comando para o QEMU
                self.monitor_socket.sendall(f'i/1xb 0x{addr}\n'.encode('utf-8'))

                time.sleep(0.5)

                # Recebe a resposta do QEMU
                body_content_resp = self.monitor_socket.recv(1024).decode('utf-8')
                
                # Caso não haja ':" no body_content_resp, o comando falhou
                if len(body_content_resp) == 0:
                    return (QEMU_ERROR, None)

                # Lendo a entrada de dados o body content só é lido depois dos ":" e do espaço deve ser feito para todas as linhas com um for
                lines = body_content_resp.split('\n')
                packet = []

                for line in lines:
                    if "= " in line:
                        packet.extend(line.split("= ", 1)[1].split(' '))

                # Converta todos os elementos da lista de inteiros para elementos de um byte de tamanho
                byte_list = [int(item, 16).to_bytes(1, byteorder='big') for item in packet]
                byte_list = b''.join(byte_list)

                # Adiciona a resposta ao byte array acumulativo
                accumulated_response.extend(byte_list)

            return (EXECUTED_SUCCESSFULLY, accumulated_response)
                        
        except Exception as e:
            return (QEMU_ERROR, None)

    # Função para escrever em um I/O
    def write_IO(self, body_content):

        # Caso o sistema esteja em estado de configuração, o comando é inválido
        if self.current_state == MACHINE_STATE_CONFIG:
            return (INVALID_MACHINE_STATE, None)

        # Caso o tamanho do body_content seja nulo, o body content do comando é inválido
        if len(body_content) == 0:
            return (INVALID_BODY_CONTENT, None)

        # Processa o body_content recebido, em MEM_ADDR e IO_VALUE
        try:
            # Divide o body_content a cada 4 bytes (2 bytes para addr e 2 bytes para value)
            byte_array = self.split_body_content(body_content, 4)

            for i in range(len(byte_array)):
                addr = byte_array[i][:2].decode('utf-8')
                value = byte_array[i][2:].decode('utf-8')

                # Envia o comando para o QEMU
                self.monitor_socket.sendall(f'o/xb 0x{addr} 0x{value}\n'.encode('utf-8'))

                time.sleep(0.5)

                # Recebe a resposta do QEMU
                body_content_resp = self.monitor_socket.recv(1024).decode('utf-8')

                # Caso não haja ':" no body_content_resp, o comando falhou
                if len(body_content_resp) == 0:
                    return (QEMU_ERROR, None)

                # Lendo a entrada de dados o body content só é lido depois dos ":" e do espaço deve ser feito para todas as linhas com um for
                lines = body_content_resp.split('\n')
                packet = []

                for line in lines:
                    if "= " in line:
                        packet.extend(line.split("= ", 1)[1].split(' '))

                # Converta todos os elementos da lista de inteiros para elementos de um byte de tamanho
                byte_list = [int(item, 16).to_bytes(1, byteorder='big') for item in packet]
                byte_list = b''.join(byte_list)

                return (EXECUTED_SUCCESSFULLY, byte_list)

        except Exception as e:
            return (QEMU_ERROR, None)