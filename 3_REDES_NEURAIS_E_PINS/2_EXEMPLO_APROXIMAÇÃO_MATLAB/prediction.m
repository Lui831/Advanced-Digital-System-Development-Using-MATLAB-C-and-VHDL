function [y,dydx,d2ydx2,y0,y1] = prediction(x,w0,b0,w1,b1)
    % Preprocessing for vectorisation of the output
    Nn = length(w0);
    N  = length(x);
    
    W0 = repmat(w0,1,N);
    B0 = repmat(b0,1,N);
    W1 = repmat(w1,1,N);
    X  = repmat(x,Nn,1);
    
    % The prediction of y(x)
    z_i   = call_custom_fcn(W0.*X+B0);     % NnxN matrix
    mySzp = call_custom_fcn(W0.*X+B0).*... % Prime of the sigmoid at z_i
             (1-call_custom_fcn(W0.*X+B0));
    mySzpp = mySzp.*(1-2*call_custom_fcn(w0*x+b0));
         
    y     = sum(W1.*z_i)+b1;        % The prediction at current batch
    
    % The prediction of dy/dx 
    dydx  = sum(W1.*W0.*mySzp);
    
    % The prediction of d2y/dx2 
    d2ydx2 = sum(w1.*w0.^2.*mySzpp);
    
    % The prediction of y(0). N.B. scalar value
    y0    = sum(w1.*call_custom_fcn(b0))+b1;
    
    % The prediction of y(1). N.B. scalar value
    y1    = sum(w1.*call_custom_fcn(w0+b0))+b1;
end
