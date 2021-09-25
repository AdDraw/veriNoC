yosys -import
set std_lib $::env(STD_LIB)

read_verilog  -defer ../srcs/components/circ_fifo.v
read_verilog  -defer ../srcs/switch/constants.v
read_verilog  -defer ../srcs/switch/virtual_channels/virtual_channel.v
read_verilog  -defer ../srcs/switch/arbiters/matrix_arbiter.v
read_verilog  -defer ../srcs/switch/routers/xy_router.v
read_verilog  -defer ../srcs/switch/crossbars/nxn_parrallel_crossbar.v
read_verilog  -defer ../srcs/switch/allocators/allocator.v
read_verilog  -defer ../srcs/switch/mesh_wormhole/mesh_wormhole_node.v

# Set parameter values (values taken from EnvVars set by yosys_wrapper.sh)
set top_module mesh_wormhole_xy_noc
# elaborate design hierarchy

set params(0) ROW_N
set params(1) COL_M
set params(2) NODE_RADIX
set params(3) CHANNEL_W
set params(4) FLIT_ID_W
set params(5) NODE_BUFFER_DEPTH_W

set values(0) 3
set values(1) 3
set values(2) 5
set values(3) 10
set values(4) 2
set values(5) 2

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
  read_verilog ../srcs/noc/mesh_wormhole_xy_noc.v
  log "Parameters from the top-module"
  chparam -list
  exit 0
}

echo on
set file_name $top_module-$values(0)-$values(1)-$values(3)-$values(5)

read_verilog  -DYS_MESH_WH_XY_TOP=1 \
              -DYS_$params(0)=$values(0) \
              -DYS_$params(1)=$values(1) \
              -DYS_$params(2)=$values(2) \
              -DYS_$params(3)=$values(3) \
              -DYS_$params(4)=$values(4) \
              -DYS_$params(5)=$values(5) \
              ../srcs/noc/mesh_wormhole_xy_noc.v

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

json -o $::env(JSON_PATH)/$file_name.json
write_verilog ../srcs/noc/mesh_wormhole_xy_noc_synth.v

tee -o $file_name.log stat -top $top_module -liberty $std_lib -tech cmos
ltp
