project -new hdl_IP.prj
add_file hdl_IP_pkg.vhd
add_file FilterCoef.vhd
add_file FilterTapSystolicPreAddWvlIn.vhd
add_file subFilter.vhd
add_file Filter.vhd
add_file dsphdl_FIRFilter.vhd
add_file hdl_IP.vhd
set_option -technology VIRTEX4
set_option -part XC4VSX35
set_option -synthesis_onoff_pragma 0
set_option -frequency auto
project -run synthesis
