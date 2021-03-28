yosys -import

read_verilog ../srcs/switch/simple_mesh_xy/switch_constants.v

# Set parameter values (values taken from EnvVars set by yosys_wrapper.sh)
set top_module xy_router
# elaborate design hierarchy

#TOP module param names when running with YOSYS
set params(0) ROW_CORD
set params(1) COL_CORD
set params(2) OUTPUT_N_W
set params(3) PACKET_ADDR_COL_W
set params(4) PACKET_ADDR_ROW_W
set params(5) SW_CONFIG

#default values for synth
set values(0) 1
set values(1) 1
set values(2) 3
set values(3) 3
set values(4) 3
set values(5) 0

chparam -list
for { set index 0 }  { $index < [array size params] }  { incr index } {
   log "params($index) : $params($index)"
   if { [info exists ::env($params($index))] } {
     set values($index) $::env($params($index))
   }
}

echo on
read_verilog  -DYS_ROUTER_TOP=1 \
              -DYS_$params(0)=$values(0) \
              -DYS_$params(1)=$values(1) \
              -DYS_$params(2)=$values(2) \
              -DYS_$params(3)=$values(3) \
              -DYS_$params(4)=$values(4) \
              -DYS_$params(5)=$values(5) \
              ../srcs/switch/simple_mesh_xy/router_xy.v
echo off

# elaborate design hierarchy
hierarchy -check -top $top_module

# the high-level stuff
procs; opt; fsm; opt; memory; opt

# mapping to internal cell library
techmap; opt

# cleanup
clean

show  -enum -width -colors 3 $top_module

json -o $::env(JSON_PATH)/$top_module.json
write_verilog ../srcs/switch/simple_mesh_xy/rtr_synth.v
