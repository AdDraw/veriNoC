yosys -import

read_verilog -defer ../srcs/switch/constants.v

# Set parameter values (values taken from EnvVars set by yosys_wrapper.sh)
set top_module xy_router
# elaborate design hierarchy

#TOP module param names when running with YOSYS
set params(0) ROW_CORD
set params(1) COL_CORD
set params(2) OUT_N_W
set params(3) COL_ADDR_W
set params(4) ROW_ADDR_W

#default values for synth
set values(0) 1
set values(1) 1
set values(2) 3
set values(3) 3
set values(4) 3

chparam -list
log "Parameters and their values:(after they were overriden with arguments)"
for { set index 0 }  { $index < [array size params] }  { incr index } {
   if { [info exists ::env($params($index))] } {
     set values($index) $::env($params($index))
   }
   log "$index. : $params($index) = $values($index)"
}

# IF SHOW_PARAMS is set to 1, it only specifies what the TOPMODULE parameters are
# it also shows params and values lists of parameters that are modifiable and their default values
if {$::env(SHOW_PARAMS) == 1} {
  read_verilog ../srcs/switch/routers/xy_router.v
  log "Parameters from the top-module"
  chparam -list
  exit 0
}

echo on
read_verilog  -DYS_ROUTER_TOP=1 \
              -DYS_$params(0)=$values(0) \
              -DYS_$params(1)=$values(1) \
              -DYS_$params(2)=$values(2) \
              -DYS_$params(3)=$values(3) \
              -DYS_$params(4)=$values(4) \
              ../srcs/switch/routers/xy_router.v
echo off

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

json -o $::env(JSON_PATH)/$top_module.json
write_verilog ../srcs/switch/simple_mesh_xy/rtr_synth.v

stat
