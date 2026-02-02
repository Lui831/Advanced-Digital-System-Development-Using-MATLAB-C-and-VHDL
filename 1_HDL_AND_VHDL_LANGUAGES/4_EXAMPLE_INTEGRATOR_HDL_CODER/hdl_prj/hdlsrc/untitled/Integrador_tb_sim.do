onbreak resume
onerror resume
vsim -voptargs=+acc work.Integrador_tb

add wave sim:/Integrador_tb/u_Integrador/clk
add wave sim:/Integrador_tb/u_Integrador/reset
add wave sim:/Integrador_tb/u_Integrador/clk_enable
add wave sim:/Integrador_tb/u_Integrador/In1
add wave sim:/Integrador_tb/u_Integrador/ce_out
add wave sim:/Integrador_tb/u_Integrador/Out1
add wave sim:/Integrador_tb/Out1_ref
run -all
