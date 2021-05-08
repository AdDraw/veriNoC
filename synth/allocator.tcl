yosys -import

read_verilog -defer ../srcs/switch/arbiters/hop_cnt_arbiter.v
read_verilog -defer ../srcs/switch/arbiters/static_priority_arbiter.v

set top_module allocator
# Set parameter values (values taken from EnvVars set by yosys_wrapper.sh)
set params(0) IN_N
set params(1) OUT_M
set params(2) FLIT_ID_W
set params(3) HOP_CNT_W
set params(4) OUT_CHAN_ID

#default values for synth
set values(0) 5
set values(1) 5
set values(2) 2
set values(3) 4
set values(4) 0

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
  read_verilog ../srcs/switch/allocators/allocator.v
  log "Parameters from the top-module"
  chparam -list
  exit 0
}

read_verilog  -DYS_ALLOCATOR_TOP=1 \
              -DYS_$params(0)=$values(0) \
              -DYS_$params(1)=$values(1) \
              -DYS_$params(2)=$values(2) \
              -DYS_$params(3)=$values(3) \
              -DYS_$params(4)=$values(4) \
              ../srcs/switch/allocators/allocator.v

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

json -o $::env(JSON_PATH)/$top_module-$values(0)-$values(1)-$values(2)-$values(3)-$values(4).json
write_verilog ../srcs/switch/allocators/allocator_synth.v

stat
