yosys -import
set std_lib $::env(STD_LIB)

read_verilog  -defer ../srcs/components/circ_fifo.v
read_verilog  -defer ../srcs/switch/constants.v
read_verilog  -defer ../srcs/switch/virtual_channels/virtual_channel.v
read_verilog  -sv -defer ../srcs/switch/arbiters/matrix_arbiter.v
read_verilog  -sv -defer ../srcs/switch/arbiters/round_robin.v
read_verilog  -sv -defer ../srcs/switch/arbiters/static_priority_arbiter.v
read_verilog  -defer ../srcs/switch/arbiters/hop_cnt_arbiter.v
read_verilog  -defer ../srcs/switch/routers/xy_router.v
read_verilog  -defer ../srcs/switch/crossbars/nxn_parrallel_crossbar.v
read_verilog  -defer ../srcs/switch/allocators/allocator.v

# Set parameter values (values taken from EnvVars set by yosys_wrapper.sh)
set top_module mesh_wormhole_node
# elaborate design hierarchy

set params(0) ROW_CORD
set params(1) COL_CORD
set params(2) IN_N
set params(3) OUT_M
set params(4) COL_ADDR_W
set params(5) ROW_ADDR_W
set params(6) FLIT_ID_W
set params(7) FLIT_DATA_W
set params(8) BUFFER_DEPTH_W
set params(9) ARB_TYPE

set values(0) 1
set values(1) 1
set values(2) 5
set values(3) 5
set values(4) 2
set values(5) 2
set values(6) 2
set values(7) 8
set values(8) 2
set values(9) 0

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
  read_verilog ../srcs/switch/mesh_wormhole/mesh_wormhole_node.v
  log "Parameters from the top-module"
  chparam -list
  exit 0
}

echo on

read_verilog -sv -DYS_MESH_WORMHOLE_NODE_TOP=1 \
              -DYS_$params(0)=$values(0) \
              -DYS_$params(1)=$values(1) \
              -DYS_$params(2)=$values(2) \
              -DYS_$params(3)=$values(3) \
              -DYS_$params(4)=$values(4) \
              -DYS_$params(5)=$values(5) \
              -DYS_$params(6)=$values(6) \
              -DYS_$params(7)=$values(7) \
              -DYS_$params(8)=$values(8) \
              -DYS_$params(9)=$values(9) \
              ../srcs/switch/mesh_wormhole/mesh_wormhole_node.v

echo off
hierarchy -top $top_module -keep_portwidths -check
synth -top $top_module -flatten
dfflibmap -liberty $std_lib
abc -liberty $std_lib

# cleanup
clean

if { ![info exists ::env(NO_XDOT)] } {
  show -enum -width -colors 3 -stretch $top_module
}

json -o $::env(JSON_PATH)/$top_module.json
write_verilog ../srcs/switch/mesh_wormhole/mesh_wormhole_node_synth.v

stat -top $top_module -liberty $std_lib -tech cmos
ltp
