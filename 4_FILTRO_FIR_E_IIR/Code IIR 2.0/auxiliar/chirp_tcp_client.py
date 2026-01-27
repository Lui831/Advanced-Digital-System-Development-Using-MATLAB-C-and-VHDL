#!/usr/bin/env python3
"""
Cliente TCP para enviar dados chirp para localhost:5050 e coletar valores filtrados
"""

import socket
import pandas as pd
import re
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os

class ChirpTCPClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Cliente TCP - Dados Chirp")
        self.root.geometry("800x700")
        
        self.df = None
        self.filtered_values = []
        self.is_running = False
        
        self.setup_ui()
    
    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Configurações de conexão
        conn_frame = ttk.LabelFrame(main_frame, text="Configurações de Conexão", padding="5")
        conn_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        conn_frame.columnconfigure(1, weight=1)
        
        ttk.Label(conn_frame, text="Servidor:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.server_var = tk.StringVar(value="localhost")
        server_entry = ttk.Entry(conn_frame, textvariable=self.server_var, width=15)
        server_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        ttk.Label(conn_frame, text="Porta:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.port_var = tk.StringVar(value="5050")
        port_entry = ttk.Entry(conn_frame, textvariable=self.port_var, width=8)
        port_entry.grid(row=0, column=3, sticky=tk.W, padx=(0, 20))
        
        ttk.Label(conn_frame, text="Delay (ms):").grid(row=0, column=4, sticky=tk.W, padx=(0, 5))
        self.delay_var = tk.StringVar(value="100")
        delay_entry = ttk.Entry(conn_frame, textvariable=self.delay_var, width=8)
        delay_entry.grid(row=0, column=5, sticky=tk.W)
        
        # Seleção de arquivo
        file_frame = ttk.LabelFrame(main_frame, text="Arquivo de Dados", padding="5")
        file_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        ttk.Label(file_frame, text="Arquivo:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        self.file_var = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.file_var, state="readonly")
        file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(file_frame, text="Selecionar", command=self.select_file).grid(row=0, column=2)
        ttk.Button(file_frame, text="Carregar dados_chirp.xlsx", 
                  command=self.load_default_file).grid(row=0, column=3, padx=(5, 0))
        
        # Informações do arquivo
        self.info_var = tk.StringVar(value="Nenhum arquivo carregado")
        ttk.Label(file_frame, textvariable=self.info_var).grid(row=1, column=0, columnspan=4, sticky=tk.W, pady=(5, 0))
        
        # Controles de execução
        control_frame = ttk.LabelFrame(main_frame, text="Controles", padding="5")
        control_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.start_button = ttk.Button(control_frame, text="Iniciar Envio", command=self.start_sending)
        self.start_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_button = ttk.Button(control_frame, text="Parar", command=self.stop_sending, state="disabled")
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="Salvar Resultados", 
                  command=self.save_results).pack(side=tk.LEFT, padx=5)
        
        self.progress_var = tk.StringVar(value="Pronto")
        ttk.Label(control_frame, textvariable=self.progress_var).pack(side=tk.RIGHT)
        
        # Log de saída
        log_frame = ttk.LabelFrame(main_frame, text="Log de Comunicação", padding="5")
        log_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="Selecionar arquivo Excel",
            filetypes=[("Arquivos Excel", "*.xlsx *.xls"), ("Todos os arquivos", "*.*")]
        )
        
        if file_path:
            self.load_file(file_path)
    
    def load_default_file(self):
        default_file = "dados_chirp.xlsx"
        if os.path.exists(default_file):
            self.load_file(default_file)
        else:
            messagebox.showerror("Erro", f"Arquivo '{default_file}' não encontrado no diretório atual.")
    
    def load_file(self, file_path):
        try:
            self.df = pd.read_excel(file_path)
            self.file_var.set(os.path.basename(file_path))
            
            # Obter informações do arquivo
            num_rows = len(self.df)
            columns = list(self.df.columns)
            
            # Assumir que queremos a primeira coluna numérica
            numeric_columns = []
            for col in columns:
                if pd.api.types.is_numeric_dtype(self.df[col]):
                    numeric_columns.append(col)
            
            if numeric_columns:
                self.data_column = numeric_columns[0]
                self.info_var.set(f"Carregado: {num_rows} valores da coluna '{self.data_column}'")
                self.log(f"Arquivo carregado: {file_path}")
                self.log(f"Coluna de dados: {self.data_column}")
                self.log(f"Total de valores: {num_rows}")
            else:
                messagebox.showerror("Erro", "Nenhuma coluna numérica encontrada no arquivo.")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar arquivo: {str(e)}")
    
    def log(self, message):
        """Adiciona mensagem ao log com timestamp"""
        timestamp = time.strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def parse_filtered_value(self, response):
        """Extrai o valor filtrado da resposta do servidor"""
        try:
            # Procurar por "DEBUG: Valor filtrado: X.XXXXXX"
            match = re.search(r'DEBUG: Valor filtrado: ([-+]?\d*\.?\d+)', response)
            if match:
                return float(match.group(1))
            return None
        except Exception as e:
            self.log(f"Erro ao extrair valor filtrado: {e}")
            return None
    
    def send_value_to_server(self, value):
        """Envia um valor para o servidor e retorna a resposta"""
        try:
            server = self.server_var.get()
            port = int(self.port_var.get())
            
            # Criar socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5.0)  # 5 segundos de timeout
            
            # Conectar
            sock.connect((server, port))
            
            # Enviar valor com '!' no final
            message = f"{value}!"
            sock.send(message.encode('utf-8'))
            
            # Receber resposta
            response = ""
            while True:
                data = sock.recv(1024).decode('utf-8')
                if not data:
                    break
                response += data
                # Verificar se recebemos a resposta completa
                if "DEBUG: Processamento concluido" in response:
                    break
            
            sock.close()
            return response
            
        except Exception as e:
            return f"ERRO: {str(e)}"
    
    def start_sending(self):
        if self.df is None:
            messagebox.showwarning("Aviso", "Carregue um arquivo primeiro.")
            return
        
        if self.is_running:
            return
        
        # Iniciar thread para envio
        self.is_running = True
        self.filtered_values = []
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        
        thread = threading.Thread(target=self.send_data_thread, daemon=True)
        thread.start()
    
    def stop_sending(self):
        self.is_running = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.progress_var.set("Parado pelo usuário")
    
    def send_data_thread(self):
        """Thread para envio dos dados"""
        try:
            values = self.df[self.data_column].dropna().tolist()
            total_values = len(values)
            delay_ms = int(self.delay_var.get())
            
            self.log(f"Iniciando envio de {total_values} valores...")
            
            for i, value in enumerate(values):
                if not self.is_running:
                    break
                
                # Atualizar progresso
                progress = f"Enviando {i+1}/{total_values} ({(i+1)/total_values*100:.1f}%)"
                self.progress_var.set(progress)
                
                # Enviar valor
                self.log(f"Enviando: {value}!")
                response = self.send_value_to_server(value)
                
                # Processar resposta
                if "ERRO:" not in response:
                    filtered_value = self.parse_filtered_value(response)
                    if filtered_value is not None:
                        self.filtered_values.append(filtered_value)
                        self.log(f"Valor filtrado recebido: {filtered_value}")
                    else:
                        self.log(f"Não foi possível extrair valor filtrado da resposta")
                        self.filtered_values.append(None)
                else:
                    self.log(f"Erro na comunicação: {response}")
                    self.filtered_values.append(None)
                
                # Delay entre envios
                if delay_ms > 0:
                    time.sleep(delay_ms / 1000.0)
            
            # Finalizar
            if self.is_running:
                self.progress_var.set(f"Concluído: {len(self.filtered_values)} valores processados")
                self.log(f"Envio concluído! {len(self.filtered_values)} valores filtrados coletados.")
            
        except Exception as e:
            self.log(f"Erro durante envio: {str(e)}")
        finally:
            self.is_running = False
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")
    
    def save_results(self):
        if not self.filtered_values:
            messagebox.showwarning("Aviso", "Nenhum resultado para salvar.")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Salvar resultados",
            defaultextension=".xlsx",
            filetypes=[("Arquivos Excel", "*.xlsx"), ("Todos os arquivos", "*.*")]
        )
        
        if file_path:
            try:
                # Criar DataFrame com valores originais e filtrados
                original_values = self.df[self.data_column].dropna().tolist()
                
                # Garantir que temos o mesmo número de valores
                min_length = min(len(original_values), len(self.filtered_values))
                
                results_df = pd.DataFrame({
                    'Valor_Original': original_values[:min_length],
                    'Valor_Filtrado': self.filtered_values[:min_length]
                })
                
                # Salvar no Excel
                results_df.to_excel(file_path, index=False)
                
                self.log(f"Resultados salvos em: {file_path}")
                messagebox.showinfo("Sucesso", f"Resultados salvos em:\n{file_path}")
                
            except Exception as e:
                self.log(f"Erro ao salvar: {str(e)}")
                messagebox.showerror("Erro", f"Erro ao salvar arquivo: {str(e)}")

def main():
    root = tk.Tk()
    app = ChirpTCPClient(root)
    root.mainloop()

if __name__ == "__main__":
    main()