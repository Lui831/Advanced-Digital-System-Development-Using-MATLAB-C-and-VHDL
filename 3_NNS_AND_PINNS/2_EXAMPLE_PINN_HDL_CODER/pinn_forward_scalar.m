function y = pinn_forward_scalar(x, W1, b1, W2, b2, W3, b3, W4, b4)
%#codegen
%PINN_FORWARD_SCALAR Forward pass com entrada escalar (amigavel a HDL).
% Arquitetura esperada: 1-32-32-32-1
% x: escalar

% Garante escalar
x = x(1);

% Camada 1
b1 = b1(:).';
a1 = tanh(x * W1 + b1);

% Camada 2
b2 = b2(:).';
a2 = tanh(a1 * W2 + b2);

% Camada 3
b3 = b3(:).';
a3 = tanh(a2 * W3 + b3);

% Saida
b4 = b4(:).';
y = a3 * W4 + b4;
end
