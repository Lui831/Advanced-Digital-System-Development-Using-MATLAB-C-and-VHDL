function y = iir_filter(x)
% IIR_FILTER Aplica um filtro IIR passa-baixas a um sinal de entrada
%
% Entrada:
%   x - vetor de amostras do sinal de entrada
%
% Saída:
%   y - vetor de amostras do sinal filtrado

    % Coeficientes do filtro IIR (biquad passa-baixas)
    b = [0.0675 0.1349 0.0675];
    a = [1 -1.1430 0.4128];

    % Aplicação do filtro
    y = filter(b, a, x);

end
