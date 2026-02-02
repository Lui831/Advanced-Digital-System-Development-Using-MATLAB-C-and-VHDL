function y = pinn_predict_hdl(x)
%#codegen
%PINN_PREDICT_HDL Wrapper para uso com HDL Coder (pesos numericos fixos).

persistent W1 b1 W2 b2 W3 b3 W4 b4
if isempty(W1)
    s = coder.load('pinn_weights.mat', 'W1','b1','W2','b2','W3','b3','W4','b4');
    W1 = s.W1; b1 = s.b1;
    W2 = s.W2; b2 = s.b2;
    W3 = s.W3; b3 = s.b3;
    W4 = s.W4; b4 = s.b4;
end

y = pinn_forward_scalar(x, W1, b1, W2, b2, W3, b3, W4, b4);
end
