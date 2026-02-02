function demo_matlab_pinn()
%DEMO_MATLAB_PINN Comparacao da PINN com a solucao analitica.

[W, b, p] = load_pinn_weights('pinn_weights.mat');

t = linspace(0, p.t_max, 200).';
T_pred = pinn_forward(t, W, b);
T_true = p.T_amb + (p.T0 - p.T_amb) * exp(-p.k * t);

figure;
plot(t, T_true, 'k--', 'LineWidth', 1.5); hold on;
plot(t, T_pred, 'b', 'LineWidth', 1.5);
legend('Analitica', 'PINN');
xlabel('t (s)'); ylabel('T (C)');
title('Resfriamento de Newton - PINN');
grid on;
end
