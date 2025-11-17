onerror {quit -f}
onbreak {quit -f}
vlib work
vmap -c
vcom  prediction_v2_fixpt_pkg.vhd
vcom  prediction_v2_fixpt.vhd
vcom  prediction_v2_fixpt_tb_pkg.vhd
vcom  prediction_v2_fixpt_tb.vhd
quit -f
