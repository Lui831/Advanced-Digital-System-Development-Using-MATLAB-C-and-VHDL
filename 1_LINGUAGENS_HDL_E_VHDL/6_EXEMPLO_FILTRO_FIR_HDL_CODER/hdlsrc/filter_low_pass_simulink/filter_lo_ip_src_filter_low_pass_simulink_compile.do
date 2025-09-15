vlib work
vmap -c -modelsimini "FILL_IN_SIMULATION_LIB_PATH/modelsim.ini"
set path_to_quartus C:/intelFPGA_standard/24.1std/quartus/bin64/..
vlib work
vmap work work
vcom -work work -2002 -explicit $path_to_quartus/dspba/backend/Libraries/vhdl/base/dspba_library_package.vhd
vcom -work work -2002 -explicit $path_to_quartus/dspba/backend/Libraries/vhdl/base/dspba_library.vhd
vcom  Altera/Cyclone_V/5CSXFC6D6F31C8/F50/alterafpf_add_single.vhd
vcom  filter_lo_ip_src_nfp_gain_pow2_single.vhd
vcom  filter_lo_ip_src_Discrete_FIR_Filter1.vhd
vcom  filter_lo_ip_src_filter_low_pass_simulink.vhd
