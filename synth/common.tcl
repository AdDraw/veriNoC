#!/usr/bin/tclsh
# Common backend for synth + opt + report for yosys
set std_lib $::env(STD_LIB)

# Read Verilog part
for { set idx 0 }  { $idx < [llength $files] - 1 }  { incr idx } {
  read_verilog -sv -defer $src/[lindex $files $idx]
}
read_verilog -sv $src/[lindex $files [expr [llength $files] - 1]]

log "SCRIPT_INFO: Parameters and their values:"
foreach name [array names params] {
  if { [info exists ::env($name)] } {
    set params($name) $::env($name)
  }
  log "SCRIPT_INFO: $name = $params($name)"
}

# IF SHOW_PARAMS is set to 1, it only specifies what the TOPMODULE parameters are
# it also shows params and values lists of parameters that are modifiable and their default values
if {$::env(SHOW_PARAMS) == 1} {
  chparam -list
  exit 0
}

# Set parameter values
puts "Set parameters"
foreach name [array names params] {
  chparam -set $name $params($name) $top_module
}

hierarchy -top $top_module -keep_portwidths -check
synth -top $top_module -flatten
dfflibmap -liberty $std_lib
abc -liberty $std_lib
clean

if { [info exists ::env(XDOT)] } {
  show -enum -long -width -signed -stretch $top_module
}

json -o $::env(JSON_PATH)/$top_module.json
write_verilog ./$top_module-netlist.v

stat -top $top_module -liberty $std_lib -tech cmos