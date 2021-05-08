yosys -import

read_verilog  -defer ../srcs/components/circ_fifo.v
read_verilog  -defer ../srcs/switch/simple_mesh_xy/switch_constants.v
read_verilog  -defer ../srcs/switch/arbiters/static_priority_arbiter.v
read_verilog  -defer ../srcs/switch/routers/xy_router.v
read_verilog  -defer ../srcs/switch/crossbars/nxn_single_crossbar.v
read_verilog  -defer ../srcs/switch/simple_mesh_xy/control_unit.v

# Set parameter values (values taken from EnvVars set by yosys_wrapper.sh)
set top_module xy_switch
# elaborate design hierarchy

set params(0) ROW_CORD
set params(1) COL_CORD
set params(2) PORT_N
set params(3) IN_FIFO_DEPTH_W
set params(4) PCKT_COL_ADDR_W
set params(5) PCKT_ROW_ADDR_W
set params(6) PCKT_DATA_W

set values(0) 1
set values(1) 1
set values(2) 5
set values(3) 6
set values(4) 3
set values(5) 3
set values(6) 8

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
  read_verilog ../srcs/switch/simple_mesh_xy/xy_switch.v
  log "Parameters from the top-module"
  chparam -list
  exit 0
}

echo on

read_verilog  -DYS_XY_SW_TOP=1 \
              -DYS_$params(0)=$values(0) \
              -DYS_$params(1)=$values(1) \
              -DYS_$params(2)=$values(2) \
              -DYS_$params(3)=$values(3) \
              -DYS_$params(4)=$values(4) \
              -DYS_$params(5)=$values(5) \
              -DYS_$params(6)=$values(6) \
              ../srcs/switch/simple_mesh_xy/xy_switch.v

echo off

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
write_verilog ../srcs/switch/simple_mesh_xy/xy_synth.v

stat
