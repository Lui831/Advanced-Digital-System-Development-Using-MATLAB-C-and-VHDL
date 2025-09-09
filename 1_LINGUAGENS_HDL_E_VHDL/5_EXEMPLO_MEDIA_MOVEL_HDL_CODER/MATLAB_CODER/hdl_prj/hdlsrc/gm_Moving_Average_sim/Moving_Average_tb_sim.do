onbreak resume
onerror resume
vsim -voptargs=+acc work.Moving_Average_tb

add wave sim:/Moving_Average_tb/u_Moving_Average/clk
add wave sim:/Moving_Average_tb/u_Moving_Average/reset
add wave sim:/Moving_Average_tb/u_Moving_Average/clk_enable
add wave sim:/Moving_Average_tb/u_Moving_Average/Input
add wave sim:/Moving_Average_tb/u_Moving_Average/ce_out
add wave sim:/Moving_Average_tb/u_Moving_Average/Output
add wave sim:/Moving_Average_tb/Output_ref
run -all
