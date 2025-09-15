package require -exact qsys 13.1
load_system system_soc.qsys
set HDLCODERIPINST filter_lo_ip_0
set HDLVerifierAXI {off}
set HDLVerifierFDC {JTAG}
set_project_property deviceFamily "Cyclone V"
set_project_property device "5CSXFC6D6F31C8"
validate_system
save_system system_soc.qsys
