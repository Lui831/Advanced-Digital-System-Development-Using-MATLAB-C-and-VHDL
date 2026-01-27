#!/usr/bin/env python3
"""
Script para converter dados de resultado.txt em vetor de som para MATLAB
Uso: python convert_to_matlab_audio.py
"""

import re
import numpy as np
import os

def extract_numeric_data(text):
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

def filter_outliers(data):
    """Remove outliers usando IQR"""
    q75, q25 = np.percentile(data, [75, 25])
    iqr = q75 - q25
    lower_bound = q25 - 1.5 * iqr
    upper_bound = q75 + 1.5 * iqr
    return data[(data >= lower_bound) & (data <= upper_bound)]

def normalize_audio(data):
    """Normaliza dados para range de áudio [-1, 1]"""
    max_val = np.max(np.abs(data))
    if max_val > 0:
        return data / max_val
    return data

def generate_matlab_code(audio_data, sample_rate=44100):
    """Gera código MATLAB para o vetor de áudio"""
    
    # Converter array para string MATLAB (limitado para não ficar muito longo)
    if len(audio_data) > 1000:
        # Para vetores muito grandes, salvar em arquivo e carregar no MATLAB
        matlab_code = f"""% Vetor de áudio extraído dos dados
% Taxa de amostragem: {sample_rate} Hz
% Número de amostras: {len(audio_data)}
% Duração: {len(audio_data)/sample_rate:.2f} segundos

% ATENÇÃO: Vetor muito grande ({len(audio_data)} elementos)
% Salve os dados em arquivo .mat e carregue no MATLAB

% Código Python para salvar (execute primeiro):
% import numpy as np
% from scipy.io import savemat
% audio_vector = [...] % seus dados aqui
% savemat('audio_data.mat', {{'audio_vector': audio_vector, 'fs': {sample_rate}}})

% No MATLAB, carregue o arquivo:
load('audio_data.mat');
fs = {sample_rate};

% Reproduzir áudio
sound(audio_vector, fs);

% Plotar sinal
figure;
t = (0:length(audio_vector)-1) / fs;
subplot(2,1,1);
plot(t, audio_vector);
xlabel('Tempo (s)');
ylabel('Amplitude');
title('Sinal de Áudio no Tempo');
grid on;

% Análise espectral
subplot(2,1,2);
N = length(audio_vector);
f = (0:N-1) * fs / N;
Y = abs(fft(audio_vector));
plot(f(1:N/2), Y(1:N/2));
xlabel('Frequência (Hz)');
ylabel('Magnitude');
title('Espectro de Frequência');
grid on;

% Salvar como arquivo WAV (opcional)
% audiowrite('audio_output.wav', audio_vector, fs);"""
    
    else:
        # Para vetores menores, incluir os dados diretamente
        data_str = ', '.join([f'{x:.6e}' for x in audio_data])
        
        matlab_code = f"""% Vetor de áudio extraído dos dados
% Taxa de amostragem: {sample_rate} Hz
% Número de amostras: {len(audio_data)}
% Duração: {len(audio_data)/sample_rate:.2f} segundos

audio_vector = [{data_str}];

% Configurar taxa de amostragem
fs = {sample_rate};

% Reproduzir áudio
sound(audio_vector, fs);

% Plotar sinal
figure;
t = (0:length(audio_vector)-1) / fs;
subplot(2,1,1);
plot(t, audio_vector);
xlabel('Tempo (s)');
ylabel('Amplitude');
title('Sinal de Áudio no Tempo');
grid on;

% Análise espectral
subplot(2,1,2);
N = length(audio_vector);
f = (0:N-1) * fs / N;
Y = abs(fft(audio_vector));
plot(f(1:N/2), Y(1:N/2));
xlabel('Frequência (Hz)');
ylabel('Magnitude');
title('Espectro de Frequência');
grid on;

% Salvar como arquivo WAV (opcional)
% audiowrite('audio_output.wav', audio_vector, fs);

% Estatísticas do sinal
fprintf('Estatísticas do sinal:\\n');
fprintf('Valor mínimo: %.6f\\n', min(audio_vector));
fprintf('Valor máximo: %.6f\\n', max(audio_vector));
fprintf('Valor médio: %.6f\\n', mean(audio_vector));
fprintf('Desvio padrão: %.6f\\n', std(audio_vector));"""
    
    return matlab_code

def main():
    input_file = "resultado.txt"
    output_file = "matlab_audio_code.m"
    
    if not os.path.exists(input_file):
        print(f"Erro: Arquivo '{input_file}' não encontrado.")
        print("Certifique-se de que o arquivo resultado.txt está no mesmo diretório.")
        return
    
    print("Processando dados de áudio...")
    
    # Ler arquivo
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Erro ao ler arquivo: {e}")
        return
    
    # Extrair dados numéricos
    print("Extraindo valores numéricos...")
    raw_data = extract_numeric_data(content)
    print(f"Valores extraídos: {len(raw_data)}")
    
    if len(raw_data) == 0:
        print("Erro: Nenhum dado numérico válido encontrado.")
        return
    
    # Filtrar outliers
    print("Filtrando outliers...")
    filtered_data = filter_outliers(raw_data)
    print(f"Valores após filtragem: {len(filtered_data)}")
    
    # Normalizar
    print("Normalizando dados...")
    audio_data = normalize_audio(filtered_data)
    audio_data = np.clip(audio_data, -1, 1)  # Garantir range de áudio
    
    # Estatísticas
    print(f"\\nEstatísticas do sinal:")
    print(f"Número de amostras: {len(audio_data)}")
    print(f"Valor mínimo: {np.min(audio_data):.6f}")
    print(f"Valor máximo: {np.max(audio_data):.6f}")
    print(f"Valor médio: {np.mean(audio_data):.6f}")
    print(f"Desvio padrão: {np.std(audio_data):.6f}")
    
    # Taxa de amostragem
    sample_rate = 44100
    duration = len(audio_data) / sample_rate
    print(f"Duração estimada (44.1kHz): {duration:.2f} segundos")
    
    # Gerar código MATLAB
    print("\\nGerando código MATLAB...")
    matlab_code = generate_matlab_code(audio_data, sample_rate)
    
    # Salvar código MATLAB
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(matlab_code)
        print(f"Código MATLAB salvo em: {output_file}")
    except Exception as e:
        print(f"Erro ao salvar arquivo: {e}")
        return
    
    # Salvar dados em formato numpy (opcional)
    try:
        np.save("audio_data.npy", audio_data)
        print("Dados salvos em: audio_data.npy")
    except Exception as e:
        print(f"Aviso: Não foi possível salvar dados numpy: {e}")
    
    print("\\nProcessamento concluído!")
    print(f"\\nPara usar no MATLAB:")
    print(f"1. Abra o arquivo '{output_file}' no MATLAB")
    print(f"2. Execute o código para reproduzir o áudio")
    print(f"3. Use 'sound(audio_vector, fs)' para tocar o som")

if __name__ == "__main__":
    main()