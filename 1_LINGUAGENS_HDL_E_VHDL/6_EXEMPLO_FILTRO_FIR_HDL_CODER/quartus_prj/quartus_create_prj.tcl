project_new system -overwrite
set HDLVerifierAXI {off}
set HDLVerifierFDC {JTAG}
set_global_assignment -name FAMILY "Cyclone V"
set_global_assignment -name DEVICE "5CSXFC6D6F31C8"
load_package flow
# Run check_ios to ensure we have a valid license
if {[catch {execute_flow -check_ios} result]} {
	puts "\nResult: $result\n"
	puts "ERROR: Quartus license check failed. See report files.\n"
	exit 1
} else {
	puts "\nINFO: Quartus license check was successful.\n"
}
set_global_assignment -name TOP_LEVEL_ENTITY system_soc
set_global_assignment -name SEARCH_PATH ./qsys_prj/system_soc/synthesis
set_global_assignment -name SEARCH_PATH ./qsys_prj/system_soc/synthesis/submodules
set_global_assignment -name SEARCH_PATH ./qsys_prj/system_soc/synthesis/submodules/sequencer
set_global_assignment -name QIP_FILE ./qsys_prj/system_soc/synthesis/system_soc.qip
set_global_assignment -name SDC_FILE constraints.sdc
set_global_assignment -name TIMEQUEST_REPORT_SCRIPT quartus_timing_query.tcl
project_close
