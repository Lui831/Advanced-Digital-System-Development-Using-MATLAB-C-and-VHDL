function [data_out] = moving_avg(num_terms, matrix_in)


num_terms_inside = num_terms;

%f_in = zeros(1000,3,'double');
f_in = matrix_in;

data_out=zeros(1,(length(f_in(:,2))- num_terms_inside));

L= length(f_in);
sum=0;
for i = 1:(L-num_terms_inside)
    for j =1:num_terms_inside

        sum = sum + f_in(i+j-1,2);
    end
       data_out(i) = sum/num_terms_inside;
       sum=0;       
end


end



