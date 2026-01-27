import re
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

class AudioVectorProcessor:
    def __init__(self, root):
        self.root = root
        self.root.title("Conversor de Dados para Vetor de Som MATLAB")
        self.root.geometry("900x700")
        
        self.audio_data = None
        self.sample_rate = 44100  # Taxa de amostragem padrão
        
        self.setup_ui()
    
    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Seleção de arquivo
        file_frame = ttk.LabelFrame(main_frame, text="Arquivo de Dados", padding="5")
        file_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        ttk.Label(file_frame, text="Arquivo:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        self.file_var = tk.StringVar()
        self.file_entry = ttk.Entry(file_frame, textvariable=self.file_var, state="readonly")
        self.file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(file_frame, text="Selecionar", command=self.select_file).grid(row=0, column=2)
        
        # Configurações de processamento
        config_frame = ttk.LabelFrame(main_frame, text="Configurações de Áudio", padding="5")
        config_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Taxa de amostragem
        ttk.Label(config_frame, text="Taxa de Amostragem (Hz):").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.sample_rate_var = tk.StringVar(value="44100")
        sample_rate_entry = ttk.Entry(config_frame, textvariable=self.sample_rate_var, width=10)
        sample_rate_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        # Normalização
        self.normalize_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(config_frame, text="Normalizar áudio", variable=self.normalize_var).grid(row=0, column=2, sticky=tk.W)
        
        # Filtrar valores extremos
        self.filter_outliers_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(config_frame, text="Filtrar valores extremos", variable=self.filter_outliers_var).grid(row=0, column=3, sticky=tk.W, padx=(20, 0))
        
        # Botão processar
        ttk.Button(config_frame, text="Processar Dados", command=self.process_data).grid(row=1, column=0, columnspan=4, pady=(10, 0))
        
        # Área de resultado
        result_frame = ttk.LabelFrame(main_frame, text="Resultados", padding="5")
        result_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(1, weight=1)
        
        # Informações do processamento
        self.info_text = scrolledtext.ScrolledText(result_frame, height=8, wrap=tk.WORD)
        self.info_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Vetor MATLAB
        ttk.Label(result_frame, text="Código MATLAB:").grid(row=2, column=0, sticky=tk.W)
        self.matlab_text = scrolledtext.ScrolledText(result_frame, height=6, wrap=tk.WORD)
        self.matlab_text.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(5, 10))
        
        # Botões de ação
        button_frame = ttk.Frame(result_frame)
        button_frame.grid(row=4, column=0, pady=5)
        
        ttk.Button(button_frame, text="Copiar MATLAB", command=self.copy_matlab).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Salvar .MAT", command=self.save_mat_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Salvar .WAV", command=self.save_wav_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Plotar Sinal", command=self.plot_signal).pack(side=tk.LEFT, padx=5)
    
    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="Selecionar arquivo de dados",
            filetypes=[("Arquivos de texto", "*.txt"), ("Todos os arquivos", "*.*")]
        )
        
        if file_path:
            self.file_var.set(file_path)
    
    def extract_numeric_data(self, text):
        """Extrai valores numéricos válidos do texto"""
        # Remove marcadores [RX] e outros textos
        text = re.sub(r'\[RX\]', '', text)
        
        # Encontra todos os números (incluindo notação científica)
        pattern = r'[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?'
        numbers = re.findall(pattern, text)
        
        valid_numbers = []
        for num_str in numbers:
            try:
                num = float(num_str)
                # Filtra valores muito grandes ou inválidos
                if abs(num) < 1e10 and not np.isnan(num) and not np.isinf(num):
                    # Ignora valores que parecem ser timestamps ou IDs
                    if abs(num) < 1e6:  # Valores de áudio tipicamente são pequenos
                        valid_numbers.append(num)
            except (ValueError, OverflowError):
                continue
        
        return np.array(valid_numbers)
    
    def process_data(self):
        file_path = self.file_var.get()
        if not file_path:
            messagebox.showwarning("Aviso", "Selecione um arquivo primeiro.")
            return
        
        try:
            # Ler arquivo
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extrair dados numéricos
            raw_data = self.extract_numeric_data(content)
            
            if len(raw_data) == 0:
                messagebox.showerror("Erro", "Nenhum dado numérico válido encontrado.")
                return
            
            # Filtrar outliers se solicitado
            if self.filter_outliers_var.get():
                q75, q25 = np.percentile(raw_data, [75, 25])
                iqr = q75 - q25
                lower_bound = q25 - 1.5 * iqr
                upper_bound = q75 + 1.5 * iqr
                filtered_data = raw_data[(raw_data >= lower_bound) & (raw_data <= upper_bound)]
            else:
                filtered_data = raw_data
            
            # Normalizar se solicitado
            if self.normalize_var.get() and len(filtered_data) > 0:
                max_val = np.max(np.abs(filtered_data))
                if max_val > 0:
                    audio_data = filtered_data / max_val
                else:
                    audio_data = filtered_data
            else:
                audio_data = filtered_data
            
            # Garantir que os valores estão no range [-1, 1] para áudio
            audio_data = np.clip(audio_data, -1, 1)
            
            self.audio_data = audio_data
            self.sample_rate = int(self.sample_rate_var.get())
            
            # Gerar informações
            info = f"""PROCESSAMENTO CONCLUÍDO
            
Arquivo processado: {file_path}
Valores extraídos: {len(raw_data)}
Valores após filtragem: {len(filtered_data)}
Valores finais no vetor: {len(audio_data)}

Estatísticas do sinal:
- Valor mínimo: {np.min(audio_data):.6f}
- Valor máximo: {np.max(audio_data):.6f}
- Valor médio: {np.mean(audio_data):.6f}
- Desvio padrão: {np.std(audio_data):.6f}

Configurações de áudio:
- Taxa de amostragem: {self.sample_rate} Hz
- Duração estimada: {len(audio_data)/self.sample_rate:.2f} segundos
- Normalizado: {'Sim' if self.normalize_var.get() else 'Não'}
- Filtros aplicados: {'Sim' if self.filter_outliers_var.get() else 'Não'}"""
            
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(1.0, info)
            
            # Gerar código MATLAB
            matlab_code = self.generate_matlab_code(audio_data)
            self.matlab_text.delete(1.0, tk.END)
            self.matlab_text.insert(1.0, matlab_code)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao processar arquivo: {str(e)}")
    
    def generate_matlab_code(self, data):
        """Gera código MATLAB para o vetor de áudio"""
        # Converter array para string MATLAB
        data_str = np.array2string(data, separator=', ', threshold=np.inf, max_line_width=80)
        data_str = data_str.replace('[', '').replace(']', '')
        
        # Truncar se muito longo para exibição
        if len(data_str) > 2000:
            data_preview = data_str[:2000] + "..."
            full_data_note = f"\n% Nota: Vetor completo tem {len(data)} elementos"
        else:
            data_preview = data_str
            full_data_note = ""
        
        matlab_code = f"""% Vetor de áudio extraído dos dados
% Taxa de amostragem: {self.sample_rate} Hz
% Número de amostras: {len(data)}
% Duração: {len(data)/self.sample_rate:.2f} segundos

audio_vector = [{data_preview}];{full_data_note}

% Configurar taxa de amostragem
fs = {self.sample_rate};

% Reproduzir áudio
sound(audio_vector, fs);

% Plotar sinal
figure;
t = (0:length(audio_vector)-1) / fs;
plot(t, audio_vector);
xlabel('Tempo (s)');
ylabel('Amplitude');
title('Sinal de Áudio');
grid on;

% Salvar como arquivo WAV (opcional)
% audiowrite('audio_output.wav', audio_vector, fs);

% Análise espectral (opcional)
% figure;
% spectrogram(audio_vector, 1024, 512, 1024, fs, 'yaxis');
% title('Espectrograma do Sinal');"""
        
        return matlab_code
    
    def copy_matlab(self):
        matlab_content = self.matlab_text.get(1.0, tk.END).strip()
        if matlab_content:
            self.root.clipboard_clear()
            self.root.clipboard_append(matlab_content)
            messagebox.showinfo("Sucesso", "Código MATLAB copiado para a área de transferência!")
    
    def save_mat_file(self):
        if self.audio_data is None:
            messagebox.showwarning("Aviso", "Processe os dados primeiro.")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Salvar arquivo .MAT",
            defaultextension=".mat",
            filetypes=[("Arquivos MATLAB", "*.mat"), ("Todos os arquivos", "*.*")]
        )
        
        if file_path:
            try:
                from scipy.io import savemat
                data_dict = {
                    'audio_vector': self.audio_data,
                    'sample_rate': self.sample_rate,
                    'duration': len(self.audio_data) / self.sample_rate
                }
                savemat(file_path, data_dict)
                messagebox.showinfo("Sucesso", f"Arquivo .MAT salvo: {file_path}")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar arquivo .MAT: {str(e)}")
    
    def save_wav_file(self):
        if self.audio_data is None:
            messagebox.showwarning("Aviso", "Processe os dados primeiro.")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Salvar arquivo WAV",
            defaultextension=".wav",
            filetypes=[("Arquivos WAV", "*.wav"), ("Todos os arquivos", "*.*")]
        )
        
        if file_path:
            try:
                # Converter para 16-bit
                audio_16bit = (self.audio_data * 32767).astype(np.int16)
                wavfile.write(file_path, self.sample_rate, audio_16bit)
                messagebox.showinfo("Sucesso", f"Arquivo WAV salvo: {file_path}")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar arquivo WAV: {str(e)}")
    
    def plot_signal(self):
        if self.audio_data is None:
            messagebox.showwarning("Aviso", "Processe os dados primeiro.")
            return
        
        try:
            # Criar janela de plot
            plt.figure(figsize=(12, 8))
            
            # Plot do sinal no tempo
            plt.subplot(2, 1, 1)
            t = np.arange(len(self.audio_data)) / self.sample_rate
            plt.plot(t, self.audio_data)
            plt.xlabel('Tempo (s)')
            plt.ylabel('Amplitude')
            plt.title(f'Sinal de Áudio - {len(self.audio_data)} amostras @ {self.sample_rate} Hz')
            plt.grid(True)
            
            # Plot do espectro
            plt.subplot(2, 1, 2)
            freqs = np.fft.fftfreq(len(self.audio_data), 1/self.sample_rate)
            fft_data = np.abs(np.fft.fft(self.audio_data))
            
            # Plotar apenas metade positiva do espectro
            half_len = len(freqs) // 2
            plt.plot(freqs[:half_len], fft_data[:half_len])
            plt.xlabel('Frequência (Hz)')
            plt.ylabel('Magnitude')
            plt.title('Espectro de Frequência')
            plt.xlim(0, self.sample_rate // 2)
            plt.grid(True)
            
            plt.tight_layout()
            plt.show()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao plotar sinal: {str(e)}")

def main():
    root = tk.Tk()
    app = AudioVectorProcessor(root)
    root.mainloop()

if __name__ == "__main__":
    main()