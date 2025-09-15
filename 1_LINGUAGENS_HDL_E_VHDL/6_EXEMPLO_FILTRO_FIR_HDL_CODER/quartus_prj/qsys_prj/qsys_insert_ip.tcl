package require -exact qsys 13.1
load_system system_soc.qsys
set HDLCODERIPINST filter_lo_ip_0
set HDLVerifierAXI {off}
set HDLVerifierFDC {JTAG}
add_instance ${HDLCODERIPINST} filter_lo_ip 1.0
add_connection pll_0.outclk0 ${HDLCODERIPINST}.ip_clk
add_connection hps_0.h2f_reset ${HDLCODERIPINST}.ip_rst
set_instance_parameter_value pll_0 {gui_output_clock_frequency0} {50.000000}
add_connection hps_0.h2f_axi_master ${HDLCODERIPINST}.s_axi
set_connection_parameter_value hps_0.h2f_axi_master/${HDLCODERIPINST}.s_axi baseAddress {0x0000}
add_connection pll_0.outclk0 ${HDLCODERIPINST}.axi_clk
add_connection hps_0.h2f_reset ${HDLCODERIPINST}.axi_reset
validate_system
save_system system_soc.qsys
