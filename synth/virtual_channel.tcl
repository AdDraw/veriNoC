yosys -import

read_verilog -defer ../srcs/switch/constants.v
read_verilog -defer ../srcs/components/circ_fifo.v
read_verilog -defer ../srcs/switch/routers/xy_router.v

set top_module virtual_channel
# Set parameter values (values taken from EnvVars set by yosys_wrapper.sh)
set params(0) VC_DEPTH_W
set params(1) FLIT_DATA_W
set params(2) FLIT_ID_W
set params(3) ROW_CORD
set params(4) COL_CORD
set params(5) OUT_N_W
set params(6) ROW_ADDR_W
set params(7) COL_ADDR_W

#default values for synth
set values(0) 2
set values(1) 8
set values(2) 2
set values(3) 1
set values(4) 1
set values(5) 3
set values(6) 2
set values(7) 2

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
  read_verilog ../srcs/switch/virtual_channels/virtual_channel.v
  log "Parameters from the top-module"
  chparam -list
  exit 0
}

read_verilog  -DYS_VC_TOP=1 \
              -DYS_$params(0)=$values(0) \
              -DYS_$params(1)=$values(1) \
              -DYS_$params(2)=$values(2) \
              -DYS_$params(3)=$values(3) \
              -DYS_$params(4)=$values(4) \
              -DYS_$params(5)=$values(5) \
              -DYS_$params(6)=$values(6) \
              -DYS_$params(7)=$values(7) \
              ../srcs/switch/virtual_channels/virtual_channel.v

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
write_verilog ../srcs/switch/virtual_channels/virtual_channel_synth.v
stat
