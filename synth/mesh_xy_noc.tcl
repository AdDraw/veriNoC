yosys -import

read_verilog -defer ../srcs/switch/constants.v
read_verilog -defer ../srcs/components/circ_fifo.v
read_verilog -defer ../srcs/switch/simple_mesh_xy/switch_constants.v
read_verilog -defer ../srcs/switch/arbiters/static_priority_arbiter.v
read_verilog -defer ../srcs/switch/arbiters/matrix_arbiter.v
read_verilog -defer ../srcs/switch/routers/xy_router.v
read_verilog -defer ../srcs/switch/crossbars/nxn_single_crossbar.v
read_verilog -defer ../srcs/switch/simple_mesh_xy/control_unit.v
read_verilog -defer ../srcs/switch/simple_mesh_xy/xy_switch.v

set top_module mesh_xy_noc
# elaborate design hierarchy

# Set parameter values (values taken from EnvVars set by yosys_wrapper.sh)
set params(0) ROW_N
set params(1) COL_M
set params(2) PCKT_DATA_W
set params(3) FIFO_DEPTH_W

#default values for synth
set values(0) 4
set values(1) 4
set values(2) 8
set values(3) 4

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
  read_verilog ../srcs/noc/mesh_xy_noc.v
  log "Parameters from the top-module"
  chparam -list
  exit 0
}

echo on
read_verilog  -DYS_MESH_XY_TOP=1 \
              -DYS_$params(0)=$values(0) \
              -DYS_$params(1)=$values(1) \
              -DYS_$params(2)=$values(2) \
              -DYS_$params(3)=$values(3) \
              ../srcs/noc/mesh_xy_noc.v

echo off
hierarchy -top $top_module -keep_portwidths -check
synth -top $top_module -flatten
dfflibmap -liberty ~/opt/yosys/examples/cmos/cmos_cells.lib
abc -liberty ~/opt/yosys/examples/cmos/cmos_cells.lib

# cleanup
clean

if { ![info exists ::env(NO_XDOT)] } {
  show  -enum -width -colors 3 $top_module
}

json -o $::env(JSON_PATH)/$top_module-$values(0)-$values(1).json
write_verilog ../srcs/noc/mesh_xy_noc_synth.v

stat $top_module
ltp
