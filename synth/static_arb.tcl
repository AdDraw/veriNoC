yosys -import

set top_module static_priority_arbiter
# Set parameter values (values taken from EnvVars set by yosys_wrapper.sh)
set params(0) IN_N

#default values for synth
set values(0) 5

chparam -list
log "Parameters and their values:"
for { set index 0 }  { $index < [array size params] }  { incr index } {
   if { [info exists ::env($params($index))] } {
     set values($index) $::env($params($index))
   }
   log "$index. : $params($index)= $values($index)"
}

# IF SHOW_PARAMS is set to 1, it only specifies what the TOPMODULE parameters are
# it also shows params and values lists of parameters that are modifiable and their default values
if {$::env(SHOW_PARAMS) == 1} {
  read_verilog ../srcs/switch/arbiters/static_priority_arbiter.v
  log "Parameters from the top-module"
  chparam -list
  exit 0
}

read_verilog  -DYS_STATIC_PRIORITY_ARBITER_TOP=1 \
              -DYS_$params(0)=$values(0) \
              ../srcs/switch/arbiters/static_priority_arbiter.v

# elaborate design hierarchy
hierarchy -check -top $top_module

# the high-level stuff
procs; opt; fsm; opt; memory; opt

# mapping to internal cell library
techmap; opt

# cleanup
clean

if { ![info exists ::env(NO_XDOT)] } {
  show  -enum -width -colors 3 $top_module
}

json -o $::env(JSON_PATH)/$top_module-$values(0).json
write_verilog ../srcs/switch/arbiters/static_priority_arbiter_synth.v

stat
