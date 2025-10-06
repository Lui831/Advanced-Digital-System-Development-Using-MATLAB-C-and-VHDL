function [data_out] = moving_avg(num_terms, matrix_in)

coef=(double((1/num_terms)).*ones(1,num_terms));
data_out = conv(coef,matrix_in);

end



