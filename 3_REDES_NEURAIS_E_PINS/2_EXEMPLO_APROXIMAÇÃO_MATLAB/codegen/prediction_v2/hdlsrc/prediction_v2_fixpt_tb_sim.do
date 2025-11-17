onerror {quit -f}
onbreak {quit -f}
vsim -voptargs=+acc work.prediction_v2_fixpt_tb

add wave sim:/prediction_v2_fixpt_tb/u_prediction_v2_fixpt/x
add wave sim:/prediction_v2_fixpt_tb/u_prediction_v2_fixpt/w0
add wave sim:/prediction_v2_fixpt_tb/u_prediction_v2_fixpt/b0
add wave sim:/prediction_v2_fixpt_tb/u_prediction_v2_fixpt/w1
add wave sim:/prediction_v2_fixpt_tb/u_prediction_v2_fixpt/b1
add wave sim:/prediction_v2_fixpt_tb/u_prediction_v2_fixpt/y
add wave sim:/prediction_v2_fixpt_tb/y_ref
add wave sim:/prediction_v2_fixpt_tb/u_prediction_v2_fixpt/dydx
add wave sim:/prediction_v2_fixpt_tb/dydx_ref
add wave sim:/prediction_v2_fixpt_tb/u_prediction_v2_fixpt/d2ydx2
add wave sim:/prediction_v2_fixpt_tb/d2ydx2_ref
add wave sim:/prediction_v2_fixpt_tb/u_prediction_v2_fixpt/y0
add wave sim:/prediction_v2_fixpt_tb/y0_ref
add wave sim:/prediction_v2_fixpt_tb/u_prediction_v2_fixpt/y1
add wave sim:/prediction_v2_fixpt_tb/y1_ref
run -all
quit -f
