#!/usr/bin/tclsh
yosys -import
echo on

set src ../srcs
set top_module nxn_parrallel_crossbar

# Define parameter names + values (values taken from EnvVars set by yosys_wrapper.sh)
array set params {
  DATA_W 10
  IN_N 5
  OUT_M 5
}

# File list
set files {
  switch/constants.v
  switch/crossbars/nxn_parrallel_crossbar.v
}

# Executes the basic backend for synth + opt + report
source common.tcl