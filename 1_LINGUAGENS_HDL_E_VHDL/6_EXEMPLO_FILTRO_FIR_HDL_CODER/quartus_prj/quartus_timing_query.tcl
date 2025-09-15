create_timing_netlist
read_sdc
update_timing_netlist
report_timing -append
set worst_path [get_timing_paths -npaths 1 -setup]
foreach_in_collection path $worst_path {
	set slack [get_path_info $path -slack] }
if {$slack > 0} {
	set worst_path [get_timing_paths -npaths 1 -hold]
	foreach_in_collection path $worst_path {
	set slack [get_path_info $path -slack] }
}
if {$slack < 0} {
	report_timing -setup -multi_corner -file system.timingerror.rpt -panel_name {Report Setup Timing} -npaths 3 -detail full_path
	report_timing -append -hold -multi_corner -file system.timingerror.rpt -panel_name {Report Hold Timing} -npaths 3 -detail full_path
	file rename system.sof system_timingfailure.sof 
	return -code error [format "ERROR- Timing constraints NOT met!
The worst slack is $slack ns
"]
}
