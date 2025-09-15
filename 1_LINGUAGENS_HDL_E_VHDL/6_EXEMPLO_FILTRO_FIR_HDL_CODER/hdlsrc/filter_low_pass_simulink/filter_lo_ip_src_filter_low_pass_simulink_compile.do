vlib work
vmap -c -modelsimini "FILL_IN_SIMULATION_LIB_PATH/modelsim.ini"
set path_to_quartus C:/intelFPGA/20.1/quartus/bin64/..
vlib work
vmap work work
vcom -work work -2002 -explicit $path_to_quartus/dspba/backend/Libraries/vhdl/base/dspba_library_package.vhd
vcom -work work -2002 -explicit $path_to_quartus/dspba/backend/Libraries/vhdl/base/dspba_library.vhd
vcom  filter_lo_ip_src_filter_low_pass_simulink_pkg.vhd
vcom  filter_lo_ip_src_nfp_gain_pow2_single.vhd
vcom  filter_lo_ip_src_nfp_add_single.vhd
vcom  filter_lo_ip_src_Discrete_FIR_Filter1.vhd
vcom  filter_lo_ip_src_filter_low_pass_simulink.vhd
