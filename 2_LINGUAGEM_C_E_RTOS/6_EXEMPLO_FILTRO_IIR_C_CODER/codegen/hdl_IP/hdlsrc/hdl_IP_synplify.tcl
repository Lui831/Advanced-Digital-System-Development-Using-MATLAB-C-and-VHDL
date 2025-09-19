project -new hdl_IP.prj
add_file BiquadDF2Section1.vhd
add_file BiquadDF2Section2.vhd
add_file BiquadDF2Section3.vhd
add_file BiquadDF2Section4.vhd
add_file BiquadDF2Section5.vhd
add_file dsphdl_BiquadFilter.vhd
add_file hdl_IP.vhd
set_option -technology VIRTEX4
set_option -part XC4VSX35
set_option -synthesis_onoff_pragma 0
set_option -frequency auto
project -run synthesis
