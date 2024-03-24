#!/usr/bin/tclsh
yosys -import
echo on

set src ../srcs
set top_module xy_router

# Define parameter names + values (values taken from EnvVars set by yosys_wrapper.sh)
array set params {
  ROW_CORD 1
  COL_CORD 1
  OUT_M 5
  COL_ADDR_W 3
  ROW_ADDR_W 3
}

# File list
set files {
  components/circ_fifo.v
  switch/constants.v
  switch/routers/xy_router.v
}

# Executes the basic backend for synth + opt + report
source common.tcl