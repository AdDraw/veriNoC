#!/usr/bin/tclsh
yosys -import
echo on

set src ../srcs
set top_module matrix_arbiter

# Define parameter names + values (values taken from EnvVars set by yosys_wrapper.sh)
array set params {
  IN_N 5
}

# File list
set files {
  switch/constants.v
  switch/arbiters/matrix_arbiter.v
}

# Executes the basic backend for synth + opt + report
source common.tcl
