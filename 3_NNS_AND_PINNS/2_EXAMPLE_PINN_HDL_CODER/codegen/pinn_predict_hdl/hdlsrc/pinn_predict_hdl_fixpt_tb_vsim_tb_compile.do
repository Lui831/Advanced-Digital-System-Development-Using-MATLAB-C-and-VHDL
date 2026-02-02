onerror {quit -f}
onbreak {quit -f}
vlib work
vmap -c
vcom  pinn_predict_hdl_fixpt_pkg.vhd
vcom  pinn_predict_hdl_fixpt.vhd
vcom  pinn_predict_hdl_fixpt_tb_pkg.vhd
vcom  pinn_predict_hdl_fixpt_tb.vhd
quit -f
