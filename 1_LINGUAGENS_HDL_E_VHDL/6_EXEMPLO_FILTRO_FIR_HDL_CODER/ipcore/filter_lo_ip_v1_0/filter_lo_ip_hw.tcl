# request TCL package from ACDS 13.1
package require -exact qsys 13.1

# module filter_lo_ip
set_module_property DESCRIPTION ""
set_module_property NAME filter_lo_ip
set_module_property VERSION 1.0
set_module_property INTERNAL false
set_module_property OPAQUE_ADDRESS_MAP true
set_module_property GROUP "HDL Coder Generated IP"
set_module_property AUTHOR ""
set_module_property DISPLAY_NAME filter_lo_ip
set_module_property INSTANTIATE_IN_SYSTEM_MODULE true
set_module_property EDITABLE true
set_module_property ANALYZE_HDL AUTO
set_module_property REPORT_TO_TALKBACK false
set_module_property ALLOW_GREYBOX_GENERATION false

# documentation
set docprefix file:///
add_documentation_link "DATASHEET" [append docprefix [get_module_property MODULE_DIRECTORY] /doc/filter_low_pass_simulink_ip_core_report.html]

# file sets
add_fileset QUARTUS_SYNTH QUARTUS_SYNTH "" ""
set_fileset_property QUARTUS_SYNTH TOP_LEVEL filter_lo_ip
set_fileset_property QUARTUS_SYNTH ENABLE_RELATIVE_INCLUDE_PATHS false
add_fileset_file alterafpf_add_single.vhd VHDL PATH hdl/alterafpf_add_single.vhd 
add_fileset_file filter_lo_ip_src_nfp_gain_pow2_single.vhd VHDL PATH hdl/filter_lo_ip_src_nfp_gain_pow2_single.vhd 
add_fileset_file filter_lo_ip_src_Discrete_FIR_Filter1.vhd VHDL PATH hdl/filter_lo_ip_src_Discrete_FIR_Filter1.vhd 
add_fileset_file filter_lo_ip_src_filter_low_pass_simulink.vhd VHDL PATH hdl/filter_lo_ip_src_filter_low_pass_simulink.vhd 
add_fileset_file filter_lo_ip_reset_sync.vhd VHDL PATH hdl/filter_lo_ip_reset_sync.vhd 
add_fileset_file filter_lo_ip_dut.vhd VHDL PATH hdl/filter_lo_ip_dut.vhd 
add_fileset_file filter_lo_ip_addr_decoder.vhd VHDL PATH hdl/filter_lo_ip_addr_decoder.vhd 
add_fileset_file filter_lo_ip_axi_lite_module.vhd VHDL PATH hdl/filter_lo_ip_axi_lite_module.vhd 
add_fileset_file filter_lo_ip_axi_lite.vhd VHDL PATH hdl/filter_lo_ip_axi_lite.vhd 
add_fileset_file filter_lo_ip.vhd VHDL PATH hdl/filter_lo_ip.vhd TOP_LEVEL_FILE
add_fileset_file dspba_library_package.vhd VHDL PATH hdl/dspba_library_package.vhd
add_fileset_file dspba_library.vhd VHDL PATH hdl/dspba_library.vhd

# connection point ip_clk
add_interface ip_clk clock end
set_interface_property ip_clk clockRate 0
set_interface_property ip_clk ENABLED true
set_interface_property ip_clk EXPORT_OF ""
set_interface_property ip_clk PORT_NAME_MAP ""
set_interface_property ip_clk CMSIS_SVD_VARIABLES ""
set_interface_property ip_clk SVD_ADDRESS_GROUP ""
add_interface_port ip_clk IPCORE_CLK clk Input 1

# connection point ip_rst
add_interface ip_rst reset end
set_interface_property ip_rst associatedClock ip_clk
set_interface_property ip_rst synchronousEdges DEASSERT
set_interface_property ip_rst ENABLED true
set_interface_property ip_rst EXPORT_OF ""
set_interface_property ip_rst PORT_NAME_MAP ""
set_interface_property ip_rst CMSIS_SVD_VARIABLES ""
set_interface_property ip_rst SVD_ADDRESS_GROUP ""
add_interface_port ip_rst IPCORE_RESETN reset_n Input 1

## AXI4 Bus
# connection point axi_clk
add_interface axi_clk clock end
set_interface_property axi_clk clockRate 0
set_interface_property axi_clk ENABLED true
set_interface_property axi_clk EXPORT_OF ""
set_interface_property axi_clk PORT_NAME_MAP ""
set_interface_property axi_clk CMSIS_SVD_VARIABLES ""
set_interface_property axi_clk SVD_ADDRESS_GROUP ""
add_interface_port axi_clk AXI4_Lite_ACLK clk Input 1

# connection point axi_reset
add_interface axi_reset reset end
set_interface_property axi_reset associatedClock axi_clk
set_interface_property axi_reset synchronousEdges DEASSERT
set_interface_property axi_reset ENABLED true
set_interface_property axi_reset EXPORT_OF ""
set_interface_property axi_reset PORT_NAME_MAP ""
set_interface_property axi_reset CMSIS_SVD_VARIABLES ""
set_interface_property axi_reset SVD_ADDRESS_GROUP ""
add_interface_port axi_reset AXI4_Lite_ARESETN reset_n Input 1

# connection point s_axi
add_interface s_axi axi4lite end
set_interface_property s_axi associatedClock axi_clk
set_interface_property s_axi associatedReset axi_reset
set_interface_property s_axi readAcceptanceCapability 1
set_interface_property s_axi writeAcceptanceCapability 1
set_interface_property s_axi combinedAcceptanceCapability 1
set_interface_property s_axi readDataReorderingDepth 1
set_interface_property s_axi bridgesToMaster ""
set_interface_property s_axi ENABLED true
set_interface_property s_axi EXPORT_OF ""
set_interface_property s_axi PORT_NAME_MAP ""
set_interface_property s_axi CMSIS_SVD_VARIABLES ""
set_interface_property s_axi SVD_ADDRESS_GROUP ""
add_interface_port s_axi AXI4_Lite_AWADDR awaddr Input 16
add_interface_port s_axi AXI4_Lite_AWVALID awvalid Input 1
add_interface_port s_axi AXI4_Lite_WDATA wdata Input 32
add_interface_port s_axi AXI4_Lite_WSTRB wstrb Input 4
add_interface_port s_axi AXI4_Lite_WVALID wvalid Input 1
add_interface_port s_axi AXI4_Lite_BREADY bready Input 1
add_interface_port s_axi AXI4_Lite_ARADDR araddr Input 16
add_interface_port s_axi AXI4_Lite_ARVALID arvalid Input 1
add_interface_port s_axi AXI4_Lite_RREADY rready Input 1
add_interface_port s_axi AXI4_Lite_ARPROT arprot Input 3
add_interface_port s_axi AXI4_Lite_AWPROT awprot Input 3
add_interface_port s_axi AXI4_Lite_AWREADY awready Output 1
add_interface_port s_axi AXI4_Lite_WREADY wready Output 1
add_interface_port s_axi AXI4_Lite_BRESP bresp Output 2
add_interface_port s_axi AXI4_Lite_BVALID bvalid Output 1
add_interface_port s_axi AXI4_Lite_ARREADY arready Output 1
add_interface_port s_axi AXI4_Lite_RDATA rdata Output 32
add_interface_port s_axi AXI4_Lite_RRESP rresp Output 2
add_interface_port s_axi AXI4_Lite_RVALID rvalid Output 1

## External Ports
# connection point In1
add_interface In1 conduit end
set_interface_property In1 associatedClock ip_clk
set_interface_property In1 associatedReset ip_rst
set_interface_property In1 ENABLED true
set_interface_property In1 EXPORT_OF ""
set_interface_property In1 PORT_NAME_MAP ""
set_interface_property In1 CMSIS_SVD_VARIABLES ""
set_interface_property In1 SVD_ADDRESS_GROUP ""
add_interface_port In1 In1 pin Input 32

# connection point Out1
add_interface Out1 conduit end
set_interface_property Out1 associatedClock ip_clk
set_interface_property Out1 associatedReset ip_rst
set_interface_property Out1 ENABLED true
set_interface_property Out1 EXPORT_OF ""
set_interface_property Out1 PORT_NAME_MAP ""
set_interface_property Out1 CMSIS_SVD_VARIABLES ""
set_interface_property Out1 SVD_ADDRESS_GROUP ""
add_interface_port Out1 Out1 pin Output 32

