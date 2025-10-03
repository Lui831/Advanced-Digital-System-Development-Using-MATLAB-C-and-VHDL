function [data_out] = moving_avg(num_terms, matrix_in)


num_terms_inside = num_terms;

%f_in = zeros(1000,3,'double');
f_in = matrix_in;

data_out=zeros(1,(length(f_in(:,2))- num_terms_inside));

L= length(f_in);

for i = 1:(L-num_terms_inside)
    sum = f_in(i,2) + f_in(i+1,2) + f_in(i+2,2) + f_in(i+3,2);
    data_out(i) = sum/num_terms_inside;
end


end



