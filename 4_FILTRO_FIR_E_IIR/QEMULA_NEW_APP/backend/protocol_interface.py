import socket
import time
from fastcrc import crc16
import threading

DOCKER_PORT = 4322
DOCKER_HOST = "localhost"
DOCKER_SOCKET_TYPE = socket.SOCK_STREAM
DOCKER_SOCKET_FAMILY = socket.AF_INET
TEST_TIMEOUT = 30
CONNECTION_RETRY_DELAY = 2
MAX_HEALTH_CHECK_ATTEMPTS = 3

class ProtocolInterface:
    def __init__(self):
        self.command_id = 0
        self.socket = None
        self.connected = False
        self.service_ready = False  # Nova flag para verificar se o serviço está pronto
        self.command_type = 0x00
        self.connection_thread = None
        self.start_connection_thread()

    def describe_status(self, code):
        return {
            0x00: "QEMU Error",
            0x01: "Executed Successfully",
            0x02: "CRC Error",
            0x03: "Invalid COMMAND_TYPE",
            0x04: "Invalid BODY_CONTENT",
            0x05: "Timeout",
            0x06: "Invalid MACHINE_STATE",
            0x07: "Invalid COMMAND_ID",
            0x08: "Invalid Requisition Length",
        }.get(code, f"Unknown ({code})")

    def describe_command(self, cmd_id):
        return {
            0x00: "Check State",
            0x01: "Inject ELF",
            0x02: "Inject AHBROM",
            0x03: "Configure RAM",
            0x04: "Configure Debug",
            0x05: "Set OS ABI",
            0x06: "Start Emulation",
            0x07: "Pause Machine",
            0x08: "Resume Execution",
            0x09: "Dump Memory",
            0x0A: "",
            0x0B: "Read I/O",
            0x0C: "Write I/O",
            0x0D: "Quit Emulation",
            0x0E: "Set Breakpoint",
            0x0F: "Delete Breakpoint",
            0x10: "Continue Execution",
            0x11: "Finish Execution",
            0x12: "Next Line",
            0x13: "Step Into",
            0x14: "Verify Variable",
            0x15: "Send GDB Command",
        }.get(cmd_id, f"Unknown Command (0x{cmd_id:02X})")

    def describe_machine_state(self, state_byte):
        states = {
            0x00: "CONFIG",
            0x01: "RUN",
        }
        return f"{state_byte:02X} ({states.get(state_byte, 'Unknown')})"

    def health_check(self):
        """Verifica se o serviço está realmente pronto para processar comandos"""
        if not self.connected or not self.socket:
            return False
            
        for attempt in range(MAX_HEALTH_CHECK_ATTEMPTS):
            try:
                print(f"Health check attempt {attempt + 1}/{MAX_HEALTH_CHECK_ATTEMPTS}")
                
                # Envia um comando simples de verificação de estado
                test_cmd = self.format_command(self.command_id, 0x00, 0x00, b"")
                
                # Configura um timeout menor para o health check
                original_timeout = self.socket.gettimeout()
                self.socket.settimeout(5)
                
                self.socket.sendall(test_cmd)
                response = self.socket.recv(4096)
                
                # Restaura o timeout original
                self.socket.settimeout(original_timeout)
                
                if response and len(response) > 0:
                    print("Health check successful - service is ready")
                    self.command_id += 1  # Incrementa apenas se o comando foi enviado
                    return True
                else:
                    print("Health check failed - no response")
                    
            except socket.timeout:
                print(f"Health check timeout on attempt {attempt + 1}")
            except Exception as e:
                print(f"Health check error on attempt {attempt + 1}: {e}")
                
            if attempt < MAX_HEALTH_CHECK_ATTEMPTS - 1:
                time.sleep(1)  # Aguarda antes da próxima tentativa
                
        return False

    def start_connection_thread(self):
        if not self.connection_thread or not self.connection_thread.is_alive():
            self.connection_thread = threading.Thread(target=self.connect_to_docker, daemon=True)
            self.connection_thread.start()

    def connect_to_docker(self):
        retry_count = 0
        
        while True:  # Loop infinito - continuar tentando até conseguir conectar
            if not self.connected or not self.service_ready:
                try:
                    if self.socket:
                        try:
                            self.socket.shutdown(socket.SHUT_RDWR)
                        except Exception:
                            pass
                        self.socket.close()
                        self.socket = None

                    print("Attempting to connect to Docker server...")
                    self.socket = socket.socket(DOCKER_SOCKET_FAMILY, DOCKER_SOCKET_TYPE)
                    self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    self.socket.connect((DOCKER_HOST, DOCKER_PORT))
                    self.socket.settimeout(TEST_TIMEOUT)
                    self.connected = True
                    print("TCP connection established with Docker server.")
                    
                    # Aguarda um pouco para o serviço se estabilizar
                    time.sleep(1)
                    
                    # Verifica se o serviço está realmente pronto
                    if self.health_check():
                        self.service_ready = True
                        if retry_count > 0:
                            print(f"✅ Successfully connected to Docker after {retry_count} attempts!")
                        else:
                            print("✅ Docker service is ready and responding to commands.")
                        retry_count = 0  # Reset contador após sucesso
                        # Continuar no loop para monitorar a conexão
                    else:
                        print("Service not ready yet, retrying...")
                        self.connected = False
                        self.service_ready = False
                        if self.socket:
                            self.socket.close()
                            self.socket = None
                        
                except (socket.error, ConnectionRefusedError) as e:
                    print(f"Error connecting to Docker: {e}")
                    self.connected = False
                    self.service_ready = False
                except Exception as e:
                    print(f"Unexpected error while connecting to Docker: {e}")
                    self.connected = False
                    self.service_ready = False
                    
                # Incrementar contador apenas quando não conseguiu conectar
                if not self.connected or not self.service_ready:
                    retry_count += 1
                    if retry_count == 1:
                        print("🔄 Starting continuous connection attempts to Docker service...")
                    elif retry_count % 10 == 0:  # Mostrar progresso a cada 10 tentativas
                        print(f"🔄 Still trying to connect... (attempt {retry_count})")
                    print(f"Retry {retry_count} in {CONNECTION_RETRY_DELAY} seconds...")
                    time.sleep(CONNECTION_RETRY_DELAY)
            else:
                # Já conectado e pronto, verificar periodicamente se ainda está conectado
                time.sleep(10)  # Verificar a cada 10 segundos
                if self.connected and self.service_ready:
                    try:
                        # Ping simples para verificar se a conexão ainda está ativa
                        self.socket.settimeout(2)
                        # Se houver erro aqui, a conexão será reestabelecida
                    except:
                        print("Connection lost, will attempt to reconnect...")
                        self.connected = False
                        self.service_ready = False
                        retry_count = 0  # Reset contador para tentar reconectar

    def close(self):
        if self.socket:
            try:
                self.socket.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass
            self.socket.close()
            self.socket = None
        self.connected = False
        self.service_ready = False
        print("Connection with the server closed.")

    def is_connected(self):
        return self.connected and self.service_ready

    def wait_for_connection(self, timeout=10):
        """Aguarda até que a conexão esteja estabelecida e o serviço esteja pronto"""
        start_time = time.time()
        while not self.is_connected():
            if time.time() - start_time > timeout:
                return False
            time.sleep(0.5)
        return True

    def format_command(self, cmd_id, state, cmd_type, body):
        cmd_id_bytes = cmd_id.to_bytes(4, "big")
        state_bytes = state.to_bytes(1, "big")
        cmd_type_bytes = cmd_type.to_bytes(2, "big")
        body_len_bytes = len(body).to_bytes(4, "big")
        command = cmd_id_bytes + state_bytes + cmd_type_bytes + body_len_bytes + body
        crc = crc16.xmodem(command, initial=0xFFFF).to_bytes(2, "big")
        print(f"Formatted command (hex): {command.hex() + crc.hex()}")
        return command + crc

    def deformat_response(self, data):
        print(f"Deframing response: {data.hex() if data else 'Empty response'}")
        if not data:
            return {"error": "Empty response from server"}

        try:
            response = {
                "id": int.from_bytes(data[0:4], "big"),
                "status": int.from_bytes(data[4:5], "big"),
                "length": int.from_bytes(data[5:9], "big"),
                "body": data[9:-2] if len(data) > 11 else b"",
                "crc": int.from_bytes(data[-2:], "big")
            }

            if response["length"] == 0 or len(response["body"]) == 0:
                response["body"] = b"-"

            print(f"Parsed response: {response}")

            return {
                "id": response["id"],
                "command": self.describe_command(self.command_type),
                "return": self.describe_status(response["status"]),
                "machine_state": self.describe_machine_state(response["body"][0]) if self.command_type == 0x00 and len(response["body"]) > 0 else "-",
                "status": response["status"],
                "body": response["body"].hex() if response["body"] != b"-" else "-"
            }
        except Exception as e:
            print(f"Error parsing response: {e}")
            return {"error": str(e)}

    def get_command_id(self):
        return self.command_id

    def send_command(self, cmd_type, state, body):
        if not self.is_connected():
            print("Service not ready. Waiting for connection...")
            if not self.wait_for_connection():
                return {"error": "Failed to connect to server or service not ready"}

        self.command_type = cmd_type
        print(f"Sending command: {self.describe_command(cmd_type)}")
        cmd = self.format_command(self.command_id, state, cmd_type, body)
        self.command_id += 1

        try:
            self.socket.sendall(cmd)
            print(f"Command sent: {cmd.hex()}")
            response = self.socket.recv(4096)
            print("Response received from server.")
            print(f"Response (hex): {response.hex()}")
            if not response:
                # Se não recebeu resposta, marca o serviço como não pronto
                self.service_ready = False
                return {"error": "Empty response from server"}
            return self.deformat_response(response)
        except socket.timeout:
            self.service_ready = False
            return {"error": "Timeout while waiting for server response"}
        except OSError as e:
            self.connected = False
            self.service_ready = False
            return {"error": f"Socket error: {e}"}
        except Exception as e:
            self.service_ready = False
            return {"error": str(e)}

    # Specific Commands
    def send_verify_state(self): return self.send_command(0x00, 0x00, b"")
    def send_inject_elf(self, elf): return self.send_command(0x01, 0x00, elf)
    def send_inject_ahbrom(self, ahb): return self.send_command(0x02, 0x00, ahb)
    def send_config_ram(self, ram_size):
        if not isinstance(ram_size, int) or ram_size <= 0:
            raise ValueError("RAM size must be a positive integer representing bytes.")
        ram_size_bytes = ram_size.to_bytes(4, 'big')
        print(f"RAM size (bytes): {ram_size} -> {ram_size_bytes.hex()}")
        return self.send_command(0x03, 0x00, ram_size_bytes)
        
    def send_config_debug(self, mode): return self.send_command(0x04, 0x00, mode.to_bytes(1, 'big'))
    def send_set_os_abi(self, osabi): return self.send_command(0x05, 0x00, osabi.encode())
    def send_start_emulation(self): return self.send_command(0x06, 0x00, b"")
    def send_pause_machine(self): return self.send_command(0x07, 0x01, b"")
    def send_unpause_machine(self): return self.send_command(0x08, 0x01, b"")
    def send_dump_memory(self, addr, size): return self.send_command(0x09, 0x01, addr.to_bytes(4, 'big') + size.to_bytes(4, 'big'))
    def send_quit_emulation(self): return self.send_command(0x0D, 0x01, b"")
    def send_config_breakpoint(self, line): return self.send_command(0x0B, 0x01, line.to_bytes(4, 'big'))
    def send_delete_breakpoint(self, line): return self.send_command(0x0C, 0x01, line.to_bytes(4, 'big'))
    def send_continue_emulation(self): return self.send_command(0x10, 0x01, b"")
    def send_finish_execution(self): return self.send_command(0x11, 0x01, b"")
    def send_next_line(self): return self.send_command(0x12, 0x01, b"")
    def send_step_into(self): return self.send_command(0x13, 0x01, b"")
    def send_verify_variable(self, name): return self.send_command(0x14, 0x01, name.encode())
    def send_gdb_command(self, cmd): return self.send_command(0x15, 0x01, cmd.encode())
    def send_read_io(self, addr): return self.send_command(0x0B, 0x01, addr.to_bytes(4, 'big'))
    def send_write_io(self, addr, value): return self.send_command(0x0C, 0x01, addr.to_bytes(4, 'big') + value.to_bytes(4, 'big'))

# Quick test
if __name__ == "__main__":
    protocol = ProtocolInterface()
    print("Waiting for service to be ready...")
    
    if protocol.wait_for_connection(timeout=60):
        print("Service is ready! Sending test command...")
        result = protocol.send_verify_state()
        print(f"Test result: {result}")
    else:
        print("Failed to connect to service or timeout reached")
    
    protocol.close()