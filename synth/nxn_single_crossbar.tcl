#!/usr/bin/tclsh
yosys -import
echo on

set src ../srcs
set top_module nxn_single_crossbar

# Define parameter names + values (values taken from EnvVars set by yosys_wrapper.sh)
array set params {
  DATA_W 10
  PORT_N 5
}

# File list
set files {
  switch/constants.v
  switch/crossbars/nxn_single_crossbar.v
}

# Executes the basic backend for synth + opt + report
source common.tcl