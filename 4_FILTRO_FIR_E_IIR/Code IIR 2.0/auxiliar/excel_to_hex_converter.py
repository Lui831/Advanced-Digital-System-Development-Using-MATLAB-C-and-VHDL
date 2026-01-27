import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pandas as pd
import os

class ExcelToHexConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Conversor Excel para Hexadecimal")
        self.root.geometry("800x600")
        
        self.df = None
        self.file_path = ""
        
        self.setup_ui()
    
    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
        # Seleção de arquivo
        ttk.Label(main_frame, text="Arquivo Excel:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        file_frame = ttk.Frame(main_frame)
        file_frame.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        file_frame.columnconfigure(0, weight=1)
        
        self.file_var = tk.StringVar()
        self.file_entry = ttk.Entry(file_frame, textvariable=self.file_var, state="readonly")
        self.file_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(file_frame, text="Selecionar", command=self.select_file).grid(row=0, column=1)
        
        # Seleção de planilha
        ttk.Label(main_frame, text="Planilha:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.sheet_var = tk.StringVar()
        self.sheet_combo = ttk.Combobox(main_frame, textvariable=self.sheet_var, state="readonly")
        self.sheet_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        self.sheet_combo.bind('<<ComboboxSelected>>', self.load_sheet)
        
        # Seleção de coluna
        ttk.Label(main_frame, text="Coluna:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.column_var = tk.StringVar()
        self.column_combo = ttk.Combobox(main_frame, textvariable=self.column_var, state="readonly")
        self.column_combo.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Configuração de tamanho do pacote
        ttk.Label(main_frame, text="Pontos por pacote:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.packet_size_var = tk.StringVar(value="1000")
        packet_size_entry = ttk.Entry(main_frame, textvariable=self.packet_size_var, width=10)
        packet_size_entry.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # Botão converter
        ttk.Button(main_frame, text="Converter para Hexadecimal", 
                  command=self.convert_to_hex).grid(row=4, column=0, columnspan=3, pady=10)
        
        # Área de resultado
        result_frame = ttk.LabelFrame(main_frame, text="Resultado", padding="5")
        result_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(2, weight=1)
        
        # Informações dos pacotes
        ttk.Label(result_frame, text="Informações dos Pacotes:").grid(row=0, column=0, sticky=tk.W)
        self.info_text = scrolledtext.ScrolledText(result_frame, height=3, wrap=tk.WORD)
        self.info_text.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 10))
        
        # Resultados com abas para cada pacote
        self.notebook = ttk.Notebook(result_frame)
        self.notebook.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Botões de ação
        button_frame = ttk.Frame(result_frame)
        button_frame.grid(row=3, column=0, pady=5)
        
        ttk.Button(button_frame, text="Copiar Pacote Atual", 
                  command=self.copy_current_packet).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Salvar Todos os Pacotes", 
                  command=self.save_all_packets).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Salvar Pacote Atual", 
                  command=self.save_current_packet).pack(side=tk.LEFT, padx=5)
    
    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="Selecionar arquivo Excel",
            filetypes=[("Arquivos Excel", "*.xlsx *.xls"), ("Todos os arquivos", "*.*")]
        )
        
        if file_path:
            self.file_path = file_path
            self.file_var.set(os.path.basename(file_path))
            self.load_file()
    
    def load_file(self):
        try:
            # Carregar todas as planilhas
            excel_file = pd.ExcelFile(self.file_path)
            sheet_names = excel_file.sheet_names
            
            self.sheet_combo['values'] = sheet_names
            if sheet_names:
                self.sheet_combo.set(sheet_names[0])
                self.load_sheet()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar arquivo: {str(e)}")
    
    def load_sheet(self, event=None):
        try:
            sheet_name = self.sheet_var.get()
            if not sheet_name:
                return
            
            self.df = pd.read_excel(self.file_path, sheet_name=sheet_name)
            
            # Carregar colunas numéricas
            numeric_columns = []
            for col in self.df.columns:
                if pd.api.types.is_numeric_dtype(self.df[col]):
                    numeric_columns.append(col)
            
            self.column_combo['values'] = numeric_columns
            if numeric_columns:
                self.column_combo.set(numeric_columns[0])
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar planilha: {str(e)}")
    
    def convert_to_hex(self):
        try:
            if self.df is None:
                messagebox.showwarning("Aviso", "Selecione um arquivo Excel primeiro.")
                return
            
            column_name = self.column_var.get()
            if not column_name:
                messagebox.showwarning("Aviso", "Selecione uma coluna.")
                return
            
            # Obter tamanho do pacote
            try:
                packet_size = int(self.packet_size_var.get())
                if packet_size <= 0:
                    raise ValueError("Tamanho do pacote deve ser maior que zero")
            except ValueError:
                messagebox.showerror("Erro", "Tamanho do pacote deve ser um número inteiro positivo.")
                return
            
            # Extrair valores da coluna, removendo NaN
            values = self.df[column_name].dropna().tolist()
            
            if not values:
                messagebox.showwarning("Aviso", "A coluna selecionada não contém valores válidos.")
                return
            
            # Dividir em pacotes
            packets = []
            for i in range(0, len(values), packet_size):
                packet = values[i:i + packet_size]
                packets.append(packet)
            
            # Limpar abas existentes
            for tab in self.notebook.tabs():
                self.notebook.forget(tab)
            
            # Armazenar dados dos pacotes para uso posterior
            self.packets_data = []
            
            # Criar uma aba para cada pacote
            for i, packet in enumerate(packets):
                # Criar frame para a aba
                tab_frame = ttk.Frame(self.notebook)
                self.notebook.add(tab_frame, text=f"Pacote {i+1}")
                
                # Configurar grid da aba
                tab_frame.columnconfigure(0, weight=1)
                tab_frame.rowconfigure(1, weight=1)
                tab_frame.rowconfigure(3, weight=1)
                
                # Formatar como lista com ponto e vírgula
                formatted_values = [str(value) for value in packet]
                list_string = "[" + ";".join(formatted_values) + "]"
                
                # Adicionar quebra de linha
                list_string_with_newline = list_string + "\n"
                
                # Converter para hexadecimal
                hex_string = ""
                for char in list_string_with_newline:
                    hex_value = format(ord(char), '02X')
                    hex_string += hex_value + " "
                
                # Remover último espaço
                hex_string = hex_string.strip()
                
                # Armazenar dados do pacote
                packet_data = {
                    'list_string': list_string,
                    'hex_string': hex_string,
                    'values': packet
                }
                self.packets_data.append(packet_data)
                
                # Lista formatada na aba
                ttk.Label(tab_frame, text="Lista formatada:").grid(row=0, column=0, sticky=tk.W, pady=(5, 0))
                list_text = scrolledtext.ScrolledText(tab_frame, height=6, wrap=tk.WORD)
                list_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(5, 10))
                list_text.insert(1.0, list_string)
                
                # Hexadecimal na aba
                ttk.Label(tab_frame, text="Hexadecimal:").grid(row=2, column=0, sticky=tk.W)
                hex_text = scrolledtext.ScrolledText(tab_frame, height=8, wrap=tk.WORD)
                hex_text.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(5, 0))
                hex_text.insert(1.0, hex_string)
            
            # Exibir informações dos pacotes
            total_values = len(values)
            num_packets = len(packets)
            last_packet_size = len(packets[-1]) if packets else 0
            
            info_text = f"""Total de valores: {total_values}
Tamanho do pacote: {packet_size} pontos
Número de pacotes: {num_packets}
Último pacote: {last_packet_size} pontos
Arquivo: {os.path.basename(self.file_path)}
Coluna: {column_name}"""
            
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(1.0, info_text)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao converter: {str(e)}")
    
    def copy_current_packet(self):
        if not hasattr(self, 'packets_data') or not self.packets_data:
            messagebox.showwarning("Aviso", "Processe os dados primeiro.")
            return
        
        # Obter índice da aba atual
        current_tab = self.notebook.index(self.notebook.select())
        
        if current_tab < len(self.packets_data):
            packet_data = self.packets_data[current_tab]
            
            # Criar texto completo do pacote
            content = f"Pacote {current_tab + 1}:\n\n"
            content += f"Lista formatada:\n{packet_data['list_string']}\n\n"
            content += f"Hexadecimal:\n{packet_data['hex_string']}\n"
            
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            messagebox.showinfo("Sucesso", f"Pacote {current_tab + 1} copiado para a área de transferência!")
    
    def save_current_packet(self):
        if not hasattr(self, 'packets_data') or not self.packets_data:
            messagebox.showwarning("Aviso", "Processe os dados primeiro.")
            return
        
        # Obter índice da aba atual
        current_tab = self.notebook.index(self.notebook.select())
        
        if current_tab < len(self.packets_data):
            file_path = filedialog.asksaveasfilename(
                title=f"Salvar Pacote {current_tab + 1}",
                defaultextension=".txt",
                filetypes=[("Arquivo de texto", "*.txt"), ("Todos os arquivos", "*.*")]
            )
            
            if file_path:
                try:
                    packet_data = self.packets_data[current_tab]
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(f"Pacote {current_tab + 1}\n")
                        f.write(f"Pontos: {len(packet_data['values'])}\n\n")
                        f.write("Lista formatada:\n")
                        f.write(packet_data['list_string'] + "\n\n")
                        f.write("Hexadecimal:\n")
                        f.write(packet_data['hex_string'] + "\n")
                    
                    messagebox.showinfo("Sucesso", f"Pacote {current_tab + 1} salvo em: {file_path}")
                except Exception as e:
                    messagebox.showerror("Erro", f"Erro ao salvar arquivo: {str(e)}")
    
    def save_all_packets(self):
        if not hasattr(self, 'packets_data') or not self.packets_data:
            messagebox.showwarning("Aviso", "Processe os dados primeiro.")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Salvar Todos os Pacotes",
            defaultextension=".txt",
            filetypes=[("Arquivo de texto", "*.txt"), ("Todos os arquivos", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"Conversão Excel para Hexadecimal - Pacotes\n")
                    f.write(f"Arquivo: {os.path.basename(self.file_path)}\n")
                    f.write(f"Coluna: {self.column_var.get()}\n")
                    f.write(f"Total de pacotes: {len(self.packets_data)}\n")
                    f.write(f"Tamanho do pacote: {self.packet_size_var.get()} pontos\n")
                    f.write("=" * 60 + "\n\n")
                    
                    for i, packet_data in enumerate(self.packets_data):
                        f.write(f"PACOTE {i + 1}\n")
                        f.write(f"Pontos: {len(packet_data['values'])}\n")
                        f.write("-" * 40 + "\n")
                        f.write("Lista formatada:\n")
                        f.write(packet_data['list_string'] + "\n\n")
                        f.write("Hexadecimal:\n")
                        f.write(packet_data['hex_string'] + "\n")
                        f.write("\n" + "=" * 60 + "\n\n")
                
                messagebox.showinfo("Sucesso", f"Todos os pacotes salvos em: {file_path}")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar arquivo: {str(e)}")

def main():
    root = tk.Tk()
    app = ExcelToHexConverter(root)
    root.mainloop()

if __name__ == "__main__":
    main()
