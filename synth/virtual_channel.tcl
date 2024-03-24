#!/usr/bin/tclsh
yosys -import
echo on

set src ../srcs
set top_module virtual_channel

# Define parameter names + values (values taken from EnvVars set by yosys_wrapper.sh)
array set params {
  VC_DEPTH_W 2
  FLIT_DATA_W 8
  FLIT_ID_W 2
  ROW_CORD 1
  COL_CORD 1
  OUT_M 5
  ROW_ADDR_W 2
  COL_ADDR_W 2
}

# File list
set files {
  components/circ_fifo.v
  switch/constants.v
  switch/routers/xy_router.v
  switch/virtual_channels/virtual_channel.v
}

# Executes the basic backend for synth + opt + report
source common.tcl