yosys -import

read_verilog  -defer ../srcs/components/fifo.v
read_verilog  -defer ../srcs/switch/simple_mesh_xy/switch_constants.v
read_verilog  -defer ../srcs/switch/simple_mesh_xy/packet_arbiter.v
read_verilog  -defer ../srcs/switch/simple_mesh_xy/router_xy.v
read_verilog  -defer ../srcs/switch/simple_mesh_xy/crossbar.v
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
set params(7) SW_CONFIG

set values(0) 1
set values(1) 1
set values(2) 5
set values(3) 6
set values(4) 3
set values(5) 3
set values(6) 8
set values(7) 0


chparam -list
for { set index 0 }  { $index < [array size params] }  { incr index } {
   log "params($index) : $params($index)"
   if { [info exists ::env($params($index))] } {
     set values($index) $::env($params($index))
   }
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
              -DYS_$params(7)=$values(7) \
              ../srcs/switch/simple_mesh_xy/xy_switch.v

echo off

hierarchy -check -top $top_module
# the high-level stuff
procs; opt; fsm; opt; memory; opt

# mapping to internal cell library
techmap; opt

# cleanup
clean

show  -enum -width -colors 3 $top_module

json -o $::env(JSON_PATH)/$top_module.json
write_verilog ../srcs/switch/simple_mesh_xy/xy_synth.v
