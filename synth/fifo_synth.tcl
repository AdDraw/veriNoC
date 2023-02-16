#!/usr/bin/tclsh
yosys -import
echo on

set src ../srcs
set top_module circ_fifo

# Define parameter names + values (values taken from EnvVars set by yosys_wrapper.sh)
array set params {
  FIFO_DEPTH_W 4
  DATA_W 8
}

# File list
set files {
  components/circ_fifo.v
}

# Executes the basic backend for synth + opt + report
source common.tcl
