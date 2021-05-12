yosys -import

read_verilog -defer ../srcs/switch/constants.v
read_verilog -defer ../srcs/components/circ_fifo.v

set top_module virtual_channel
# Set parameter values (values taken from EnvVars set by yosys_wrapper.sh)
set params(0) VC_DEPTH_W
set params(1) FLIT_DATA_W
set params(2) FLIT_ID_W

#default values for synth
set values(0) 2
set values(1) 8
set values(2) 2

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
  read_verilog ../srcs/switch/virtual_channels/virtual_channel.v
  log "Parameters from the top-module"
  chparam -list
  exit 0
}

read_verilog  -DYS_VC_TOP=1 \
              -DYS_$params(0)=$values(0) \
              -DYS_$params(1)=$values(1) \
              -DYS_$params(2)=$values(2) \
              ../srcs/switch/virtual_channels/virtual_channel.v

# elaborate design hierarchy
hierarchy -check -top $top_module

# the high-level stuff
#procs;
#opt; wreduce; share; opt; fsm;
#procs;
#opt;
synth -top $top_module
# cleanup
#clean

if { ![info exists ::env(NO_XDOT)] } {
  show  -enum -width -colors 3 $top_module
}

json -o $::env(JSON_PATH)/$top_module-$values(0)-$values(1).json
write_verilog ../srcs/switch/virtual_channels/virtual_channel_synth.v
stat
