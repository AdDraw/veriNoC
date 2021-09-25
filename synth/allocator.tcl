yosys -import
set std_lib $::env(STD_LIB)

read_verilog -defer ../srcs/switch/constants.v
read_verilog -defer ../srcs/switch/arbiters/matrix_arbiter.v

set top_module allocator
# Set parameter values (values taken from EnvVars set by yosys_wrapper.sh)
set params(0) IN_N
set params(1) OUT_M
set params(2) FLIT_ID_W
set params(3) OUT_CHAN_ID

#default values for synth
set values(0) 5
set values(1) 5
set values(2) 2
set values(3) 1

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
              ../srcs/switch/allocators/allocator.v

echo off
hierarchy -top $top_module -keep_portwidths -check
synth -top $top_module -flatten
dfflibmap -liberty $std_lib
abc -liberty $std_lib
# cleanup
clean

if { ![info exists ::env(NO_XDOT)] } {
  show  -enum -width -colors 3 $top_module
}

json -o $::env(JSON_PATH)/$top_module-$values(0)-$values(1)-$values(2)-$values(3).json
write_verilog ../srcs/switch/allocators/allocator_synth.v

stat -top $top_module -liberty $std_lib -tech cmos
