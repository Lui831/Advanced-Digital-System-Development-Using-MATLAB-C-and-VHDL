function tb_pinn_predict_hdl()
%TB_PINN_PREDICT_HDL Testbench simples para a PINN em HDL.
% Executa o DUT com um conjunto fixo de entradas e compara com a solucao analitica.

s = load('pinn_weights.mat', 'T_amb', 'T0', 'k', 't_max');

% Estimulos fixos (tamanho constante)
N = 101;
t = linspace(0, s.t_max, N);
y = zeros(1, N);

for i = 1:N
    y(i) = pinn_predict_hdl(t(i));
end

T_true = s.T_amb + (s.T0 - s.T_amb) * exp(-s.k * t);
err = max(abs(y - T_true));

fprintf('Max abs error: %.6f\n', err);
end
