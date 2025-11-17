function y = custom_fcn(x)
  [L,C] = size(x);
  % Initialize the output array
  y = zeros(L, C);
   for i= 1:L
       for j=1:C
          y(i,j) = 1./(1+exp(-x(i,j)));
       end
   end   
end