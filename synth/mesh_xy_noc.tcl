yosys -import

read_verilog -defer ../srcs/components/fifo.v
read_verilog -defer ../srcs/switch/simple_mesh_xy/switch_constants.v
read_verilog -defer ../srcs/switch/simple_mesh_xy/packet_arbiter.v
read_verilog -defer ../srcs/switch/simple_mesh_xy/router_xy.v
read_verilog -defer ../srcs/switch/simple_mesh_xy/crossbar.v
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
set values(0) 3
set values(1) 3
set values(2) 8
set values(3) 4

chparam -list
for { set index 0 }  { $index < [array size params] }  { incr index } {
   log "params($index) : $params($index)"
   if { [info exists ::env($params($index))] } {
     set values($index) $::env($params($index))
   }
}

echo on
read_verilog  -DYS_MESH_XY_TOP=1 \
              -DYS_$params(0)=$values(0) \
              -DYS_$params(1)=$values(1) \
              -DYS_$params(2)=$values(2) \
              -DYS_$params(3)=$values(3) \
              ../srcs/noc/mesh_xy_noc.v
echo off

hierarchy -check -top $top_module

# the high-level stuff
procs; opt; fsm; opt; memory; opt

# mapping to internal cell library
techmap; opt

# cleanup
clean

show  -enum -stretch -width -colors 3 $top_module

json -o $::env(JSON_PATH)/$top_module-$values(0)-$values(1).json
write_verilog ../srcs/noc/mesh_xy_noc_synth.v
