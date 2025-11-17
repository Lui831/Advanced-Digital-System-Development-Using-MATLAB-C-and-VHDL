function [y,dydx,d2ydx2,y0,y1] = prediction_v2(x,w0,b0,w1,b1)
    % x é vetor de tamanho Nx1
    % w0, b0, w1 são vetores de tamanho Nn
    Nn = length(w0);
    N = length(x);

    y = zeros(1,N);
    dydx = zeros(1,N);
    d2ydx2 = zeros(1,N);

    for j = 1:N
        yj = 0;
        dyj = 0;
        d2yj = 0;
        for i = 1:Nn
            z = call_custom_fcn(w0(i)*x(j) + b0(i));
            szp = z * (1 - z);
            szpp = szp * (1 - 2 * call_custom_fcn(w0(i)*x(j) + b0(i)));

            yj = yj + w1(i) * z;
            dyj = dyj + w1(i) * w0(i) * szp;
            d2yj = d2yj + w1(i) * w0(i)^2 * szpp;
        end
        y(j) = yj + b1;
        dydx(j) = dyj;
        d2ydx2(j) = d2yj;
    end

    % Cálculo de y(0) e y(1)
    y0 = b1;
    y1 = b1;
    for i = 1:Nn
        y0 = y0 + w1(i) * call_custom_fcn(b0(i));
        y1 = y1 + w1(i) * call_custom_fcn(w0(i) + b0(i));
    end
end


