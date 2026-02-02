function [W, b, params] = load_pinn_weights(matfile)
%LOAD_PINN_WEIGHTS Carrega pesos salvos pelo Python.

if nargin < 1
    matfile = 'pinn_weights.mat';
end

s = load(matfile);
if isfield(s, 'W') && isfield(s, 'b')
    W = s.W;
    b = s.b;
    params = rmfield(s, {'W', 'b'});
else
    % Formato fixo (HDL-friendly): W1..W4, b1..b4
    W = {s.W1, s.W2, s.W3, s.W4};
    b = {s.b1, s.b2, s.b3, s.b4};
    params = rmfield(s, {'W1','W2','W3','W4','b1','b2','b3','b4'});
end
end
