function [data_out] = moving_avg(num_terms, matrix_in)

coder.cinclude('<stdio.h>');
num_terms_inside = num_terms;

%f_in = zeros(1000,3,'double');
f_in = matrix_in;


sum = 0;
cont = 0;
data_out = zeros(1,(length(f_in)/num_terms_inside));
j = 0;


L= length(f_in);

for i = 1:L
    sum = sum + f_in(i,1);
    cont = cont + 1;

    if cont == num_terms_inside
            cont = 0;
            j = j + 1;
            data_out(j) = sum/num_terms_inside;
            sum = 0;
    end

end


end



