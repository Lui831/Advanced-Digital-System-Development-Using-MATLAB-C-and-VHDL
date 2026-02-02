onerror {quit -f}
onbreak {quit -f}
vsim -voptargs=+acc work.pinn_predict_hdl_fixpt_tb

add wave sim:/pinn_predict_hdl_fixpt_tb/u_pinn_predict_hdl_fixpt/x
add wave sim:/pinn_predict_hdl_fixpt_tb/u_pinn_predict_hdl_fixpt/y
add wave sim:/pinn_predict_hdl_fixpt_tb/y_ref
run -all
quit -f
