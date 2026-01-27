from scipy import signal
import numpy as np
import matplotlib.pyplot as plt

# --- 5 Parâmetros de entrada (valores atualizados) ---
# 1. Ordem do filtro (N): Aumentada para 5
order = 5
# 2. Frequência crítica (Wn): Frequência de corte em Hz
cutoff_freq = 500  # Exemplo: 500 Hz
# 3. Frequência de amostragem (fs): 8192 Hz
sampling_freq = 8192  # Hz
# 4. Tipo de filtro (btype): 'lowpass'
filter_type = 'lowpass'
# 5. Design do filtro (ftype): 'butter' (Butterworth)
filter_design = 'butter'

# Gerar os coeficientes do filtro (b e a)
b, a = signal.iirfilter(
    order,
    cutoff_freq / (sampling_freq / 2),
    btype=filter_type,
    ftype=filter_design
)
print(f"Coeficientes do numerador (b): {b}")
print(f"Coeficientes do denominador (a): {a}")

# Gerar um sinal de teste
t = np.linspace(0, 1, sampling_freq, endpoint=False)
# Sinal com duas ondas senoidais: uma de 200 Hz (passa) e uma de 1500 Hz (corta)
input_signal = np.sin(2 * np.pi * 200 * t) + 0.5 * np.sin(2 * np.pi * 1500 * t)

# Aplicar o filtro ao sinal
output_signal = signal.lfilter(b, a, input_signal)

# --- 5 Parâmetros de saída ---
# 1. Sinal filtrado: O componente de 200 Hz é mantido, enquanto o de 1500 Hz é atenuado.
# 2. Coeficientes da função de transferência (b e a): As matrizes de coeficientes, que agora terão um tamanho diferente devido à ordem 5.
# 3. Resposta de magnitude: A atenuação será mais acentuada após a frequência de corte de 500 Hz do que no exemplo anterior.
# 4. Resposta de fase: O atraso de fase será mais pronunciado devido à ordem mais alta.
# 5. Estabilidade: O filtro continua estável.

# Plotar os resultados
plt.figure(figsize=(10, 6))
plt.plot(t, input_signal, label='Sinal de Entrada (200 Hz + 1500 Hz)', alpha=0.6)
plt.plot(t, output_signal, label='Sinal de Saída (Filtrado)', linewidth=2)
plt.title(f'Filtro Low-pass Butterworth de Ordem {order}')
plt.xlabel('Tempo (s)')
plt.ylabel('Amplitude')
plt.legend()
plt.grid(True)
plt.show()

print("\n--- Detalhes do Design do Filtro ---")
print(f"Ordem do filtro: {order}")
print(f"Frequência de corte: {cutoff_freq} Hz")
print(f"Frequência de amostragem: {sampling_freq} Hz")
print(f"Frequência crítica normalizada: {cutoff_freq / (sampling_freq / 2):.4f}")
print(f"Tipo de filtro: {filter_type.capitalize()}")

print("\n--- Coeficientes da Função de Transferência ---")
print(f"Coeficientes do numerador (b): {b}")
print(f"Coeficientes do denominador (a): {a}")
 