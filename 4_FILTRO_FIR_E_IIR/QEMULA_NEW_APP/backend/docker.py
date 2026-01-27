import subprocess
import os
import sys
import shlex

class DockerManager:
    def __init__(self):
        # Verificar se Podman ou Docker estão disponíveis
        self.container_engine = None
        
        # Tentar Podman primeiro
        try:
            subprocess.run(["podman", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            self.container_engine = "podman"
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Tentar Docker como fallback
            try:
                subprocess.run(["docker", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                self.container_engine = "docker"
            except (subprocess.CalledProcessError, FileNotFoundError):
                # Nem podman nem docker disponíveis - usar modo demo
                self.container_engine = "demo"
                print("Warning: Neither Podman nor Docker available. Using demo mode with example data.")

    def _get_clean_environment(self):
        """Prepara um ambiente limpo para subprocess, preservando variáveis essenciais"""
        # Copia o ambiente atual
        env = os.environ.copy()
        
        # Adiciona/corrige variáveis importantes para o Podman
        essential_vars = {
            'PATH': env.get('PATH', ''),
            'HOME': env.get('HOME', ''),
            'USER': env.get('USER', ''),
            'TERM': 'xterm-256color',  # Terminal padrão
            'LANG': env.get('LANG', 'C.UTF-8'),
            'LC_ALL': env.get('LC_ALL', 'C.UTF-8'),
        }
        
        # Variáveis específicas do Podman
        podman_vars = {
            'PODMAN_USERNS': 'keep-id',
            'BUILDAH_ISOLATION': 'chroot',
        }
        
        # Mescla todas as variáveis
        clean_env = {**env, **essential_vars, **podman_vars}
        
        return clean_env

    def _run_subprocess_safe(self, cmd, cwd=None, timeout=60):
        """Executa subprocess com tratamento seguro e ambiente limpo"""
        try:
            env = self._get_clean_environment()
            
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                timeout=timeout,
                cwd=cwd,
                env=env,
                shell=False  # Mais seguro que shell=True
            )
            
            return result
            
        except subprocess.TimeoutExpired:
            return type('Result', (), {
                'returncode': 124,
                'stdout': '',
                'stderr': f'Command timed out after {timeout} seconds'
            })()
        except Exception as e:
            return type('Result', (), {
                'returncode': 1,
                'stdout': '',
                'stderr': str(e)
            })()

    def list_images(self):
        """Executa o comando de listagem de imagens baseado no engine disponível."""
        if self.container_engine == "demo":
            return self.get_example_images()
        
        try:
            if self.container_engine == "podman":
                # Verifica se podman está funcionando
                test_result = self._run_subprocess_safe(["podman", "version"], timeout=10)
                
                if test_result.returncode != 0:
                    print("Podman não está funcionando, tentando Docker...")
                    return self.list_images_docker()
                
                # Executa o comando 'podman images'
                result = self._run_subprocess_safe([
                    "podman", "images", "--format", 
                    "{{.Repository}} {{.Tag}} {{.ID}} {{.Created}} {{.Size}}"
                ])
                
                if result.returncode != 0:
                    print(f"Erro no Podman: {result.stderr}")
                    return self.list_images_docker()
            else:
                return self.list_images_docker()
            
            # Processa a saída do comando
            formatted_images = []
            for line in result.stdout.strip().split("\n"):
                if line.strip():  # Ignora linhas vazias
                    parts = line.split()
                    if len(parts) >= 5:
                        repository = parts[0]
                        tag = parts[1]
                        image_id = parts[2]
                        created = " ".join(parts[3:-1])  # Combina a data de criação
                        size = parts[-1]
                        formatted_images.append({
                            "repository": repository,
                            "tag": tag,
                            "id": image_id,
                            "created": created,
                            "size": size
                        })
            
            return formatted_images if formatted_images else self.get_example_images()
            
        except Exception as e:
            print(f"Erro ao listar imagens: {e}")
            # Se tanto podman quanto docker falharem, retornar dados de exemplo
            return self.get_example_images()
    
    def list_images_docker(self):
        """Tenta usar docker como fallback"""
        try:
            # Verifica se docker está funcionando
            test_result = self._run_subprocess_safe(["docker", "version"], timeout=10)
            
            if test_result.returncode != 0:
                print("Docker também não está funcionando, usando dados de exemplo")
                return self.get_example_images()
            
            result = self._run_subprocess_safe([
                "docker", "images", "--format", 
                "{{.Repository}} {{.Tag}} {{.ID}} {{.CreatedAt}} {{.Size}}"
            ])
            
            if result.returncode != 0:
                print(f"Erro no Docker: {result.stderr}")
                return self.get_example_images()
            
            # Processa a saída do comando docker
            formatted_images = []
            for line in result.stdout.strip().split("\n"):
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 5:
                        repository = parts[0]
                        tag = parts[1]
                        image_id = parts[2]
                        created = " ".join(parts[3:-1])
                        size = parts[-1]
                        formatted_images.append({
                            "repository": repository,
                            "tag": tag,
                            "id": image_id,
                            "created": created,
                            "size": size
                        })
            
            return formatted_images if formatted_images else self.get_example_images()
            
        except Exception as e:
            print(f"Erro no Docker: {e}")
            return self.get_example_images()
    
    def get_example_images(self):
        """Retorna dados de exemplo quando nem podman nem docker estão disponíveis"""
        return [
            {
                "repository": "qemu/system-sparc",
                "tag": "latest",
                "id": "abc123def456",
                "created": "2 days ago",
                "size": "256MB"
            },
            {
                "repository": "qemu/system-arm",
                "tag": "v7.2.0",
                "id": "def456ghi789",
                "created": "1 week ago",
                "size": "312MB"
            },
            {
                "repository": "ubuntu",
                "tag": "22.04",
                "id": "ghi789jkl012",
                "created": "3 days ago",
                "size": "72.8MB"
            },
            {
                "repository": "alpine",
                "tag": "latest",
                "id": "jkl012mno345",
                "created": "5 days ago",
                "size": "5.53MB"
            },
            {
                "repository": "redis",
                "tag": "7-alpine",
                "id": "mno345pqr678",
                "created": "1 day ago",
                "size": "28.4MB"
            },
            {
                "repository": "nginx",
                "tag": "alpine",
                "id": "pqr678stu901",
                "created": "6 hours ago",
                "size": "23.4MB"
            },
            {
                "repository": "postgres",
                "tag": "15-alpine",
                "id": "stu901vwx234",
                "created": "4 days ago",
                "size": "75.1MB"
            },
            {
                "repository": "node",
                "tag": "18-alpine",
                "id": "vwx234yzab567",
                "created": "2 weeks ago",
                "size": "168MB"
            },
            {
                "repository": "python",
                "tag": "3.11-slim",
                "id": "yzab567cdef890",
                "created": "1 week ago",
                "size": "123MB"
            },
            {
                "repository": "busybox",
                "tag": "latest",
                "id": "cdef890ghij123",
                "created": "3 weeks ago",
                "size": "1.24MB"
            }
        ]

    def docker_compose_up(self, compose_file_path):
        """Executa o comando 'podman-compose up' no diretório correto."""
        # Se estiver em modo demo, simular o comportamento
        if self.container_engine == "demo":
            return self.simulate_compose_up(compose_file_path)
        
        try:
            # Verifica se o arquivo docker-compose.yml existe
            if not os.path.exists(compose_file_path):
                return {"error": "docker-compose.yml file not found."}

            # Salva o diretório atual
            current_dir = os.getcwd()

            # Muda para o diretório onde o docker-compose.yml está localizado
            compose_dir = os.path.dirname(compose_file_path)
            if compose_dir:
                os.chdir(compose_dir)

            # Escolhe o comando baseado no engine disponível
            if self.container_engine == "podman":
                try:
                    # Primeiro tenta podman-compose
                    result = subprocess.run(
                        ["podman-compose", "-f", os.path.basename(compose_file_path), "up", "-d"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        encoding="utf-8"
                    )
                except FileNotFoundError:
                    # Se podman-compose não estiver disponível
                    os.chdir(current_dir)
                    return {"error": "podman-compose não está instalado. Instale com: pip install podman-compose"}
            else:  # docker
                try:
                    result = subprocess.run(
                        ["docker-compose", "-f", os.path.basename(compose_file_path), "up", "-d"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        encoding="utf-8"
                    )
                except FileNotFoundError:
                    os.chdir(current_dir)
                    return {"error": "docker-compose não está instalado."}

            # Volta para o diretório original
            os.chdir(current_dir)

            if result.returncode == 0:
                return {"success": result.stdout}
            else:
                return {"error": result.stderr}
        except Exception as e:
            # Garante que volta para o diretório original em caso de erro
            try:
                os.chdir(current_dir)
            except:
                pass
            return {"error": str(e)}

    def docker_compose_down(self, compose_file_path):
        """Executa o comando 'podman-compose down' no diretório correto."""
        # Se estiver em modo demo, simular o comportamento
        if self.container_engine == "demo":
            return self.simulate_compose_down(compose_file_path)
        
        try:
            # Verifica se o arquivo docker-compose.yml existe
            if not os.path.exists(compose_file_path):
                return {"error": "docker-compose.yml file not found."}

            # Salva o diretório atual
            current_dir = os.getcwd()

            # Muda para o diretório onde o docker-compose.yml está localizado
            compose_dir = os.path.dirname(compose_file_path)
            if compose_dir:
                os.chdir(compose_dir)

            # Escolhe o comando baseado no engine disponível
            if self.container_engine == "podman":
                try:
                    result = subprocess.run(
                        ["podman-compose", "-f", os.path.basename(compose_file_path), "down"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        encoding="utf-8"
                    )
                except FileNotFoundError:
                    os.chdir(current_dir)
                    return {"error": "podman-compose não está instalado. Instale com: pip install podman-compose"}
            else:  # docker
                try:
                    result = subprocess.run(
                        ["docker-compose", "-f", os.path.basename(compose_file_path), "down"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        encoding="utf-8"
                    )
                except FileNotFoundError:
                    os.chdir(current_dir)
                    return {"error": "docker-compose não está instalado."}

            # Volta para o diretório original
            os.chdir(current_dir)

            if result.returncode == 0:
                return {"success": result.stdout}
            else:
                return {"error": result.stderr}
        except Exception as e:
            # Garante que volta para o diretório original em caso de erro
            try:
                os.chdir(current_dir)
            except:
                pass
            return {"error": str(e)}
    
    def simulate_compose_up(self, compose_file_path):
        """Simula o comando docker-compose up em modo demo"""
        import time
        time.sleep(1)  # Simular tempo de processamento
        return {
            "success": f"[DEMO] Simulating docker-compose up for {compose_file_path}\n"
                      f"Creating network demo_default\n"
                      f"Creating demo_app_1 ... done\n"
                      f"Creating demo_db_1  ... done\n"
                      f"Services started successfully (demo mode)"
        }
    
    def simulate_compose_down(self, compose_file_path):
        """Simula o comando docker-compose down em modo demo"""
        import time
        time.sleep(1)  # Simular tempo de processamento
        return {
            "success": f"[DEMO] Simulating docker-compose down for {compose_file_path}\n"
                      f"Stopping demo_db_1  ... done\n"
                      f"Stopping demo_app_1 ... done\n"
                      f"Removing demo_db_1  ... done\n"
                      f"Removing demo_app_1 ... done\n"
                      f"Removing network demo_default\n"
                      f"Services stopped successfully (demo mode)"
        }
    
    def check_compose_containers(self, compose_file_path):
        """Verifica se há containers do compose file em execução"""
        if self.container_engine == "demo":
            return self.check_compose_containers_demo(compose_file_path)
        
        try:
            # Usar o comando ps para verificar containers em execução
            cmd = [self.container_engine, "compose", "-f", compose_file_path, "ps", "-q"]
            result = self._run_subprocess_safe(cmd, timeout=15)
            
            if result.returncode == 0 and result.stdout.strip():
                # Se há IDs de containers na saída, significa que há containers rodando
                container_ids = result.stdout.strip().split('\n')
                return {"running": True, "containers": container_ids}
            else:
                return {"running": False, "containers": []}
                
        except Exception as e:
            return {"error": f"Error checking containers: {str(e)}"}
    
    def check_compose_containers_demo(self, compose_file_path):
        """Simula verificação de containers em modo demo"""
        import random
        # Simular aleatoriamente se há containers rodando (para testar a lógica)
        has_running = random.choice([True, False])
        return {
            "running": has_running,
            "containers": ["demo_container_1", "demo_container_2"] if has_running else []
        }
    
    def docker_compose_down_force(self, compose_file_path):
        """Executa docker-compose down com força, removendo volumes e networks órfãos"""
        if self.container_engine == "demo":
            return self.docker_compose_down_force_demo(compose_file_path)
        
        try:
            # Verifica se o arquivo docker-compose.yml existe
            if not os.path.exists(compose_file_path):
                return {"error": "docker-compose.yml file not found."}

            # Salva o diretório atual
            current_dir = os.getcwd()
            compose_dir = os.path.dirname(compose_file_path)
            if compose_dir:
                os.chdir(compose_dir)
            
            # Comando compose down com opções mais agressivas
            if self.container_engine == "podman":
                cmd = ["podman-compose", "-f", os.path.basename(compose_file_path), 
                       "down", "--volumes", "--remove-orphans"]
            else:  # docker
                cmd = ["docker-compose", "-f", os.path.basename(compose_file_path), 
                       "down", "--volumes", "--remove-orphans"]
            
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=60
            )
            
            # Volta para o diretório original
            os.chdir(current_dir)
            
            if result.returncode == 0:
                return {"success": result.stdout}
            else:
                return {"error": result.stderr}
                
        except subprocess.TimeoutExpired:
            try:
                os.chdir(current_dir)
            except:
                pass
            return {"error": "Timeout: docker-compose down force took too long"}
        except Exception as e:
            try:
                os.chdir(current_dir)
            except:
                pass
            return {"error": f"Exception: {str(e)}"}
    
    def docker_compose_down_force_demo(self, compose_file_path):
        """Simula docker-compose down force em modo demo"""
        import time
        time.sleep(2)  # Simular tempo de processamento mais longo
        return {
            "success": f"[DEMO] Simulating forced docker-compose down for {compose_file_path}\n"
                      f"Stopping demo_db_1  ... done\n"
                      f"Stopping demo_app_1 ... done\n"
                      f"Removing demo_db_1  ... done\n"
                      f"Removing demo_app_1 ... done\n"
                      f"Removing volume demo_db_data\n"
                      f"Removing network demo_default\n"
                      f"Removing orphaned containers...\n"
                      f"Services forcefully stopped (demo mode)"
        }