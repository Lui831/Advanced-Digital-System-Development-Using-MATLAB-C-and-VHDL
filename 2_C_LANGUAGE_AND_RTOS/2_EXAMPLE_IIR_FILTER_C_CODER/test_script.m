%% Parâmetros do sinal
fs = 48000;              % Frequência de amostragem (100 kHz)
t  = 0:1/fs:0.01;         % 10 ms de sinal

f1 = 1000;                % 5 kHz
f2 = 5000;               % 15 kHz

%% Sinal de entrada: senoides sobrepostas
x = sin(2*pi*f1*t) + sin(2*pi*f2*t);

%% Aplicação do filtro
y = doFilter(x);

%% Plot dos sinais
figure;

subplot(2,1,1);
plot(t, x, 'r');
grid on;
xlabel('Tempo (s)');
ylabel('Amplitude');
title('Sinal de entrada: senoides de 5 kHz e 15 kHz');

subplot(2,1,2);
plot(t, y, 'b', 'LineWidth', 1.2);
grid on;
xlabel('Tempo (s)');
ylabel('Amplitude');
title('Sinal de saída após aplicação do filtro');
