#!/usr/bin/tclsh
yosys -import
echo on

set src ../srcs
set top_module round_robin_arbiter

# Define parameter names + values (values taken from EnvVars set by yosys_wrapper.sh)
array set params {
  IN_N 5
}

# File list
set files {
  switch/constants.v
  switch/arbiters/round_robin_arbiter.v
}

# Executes the basic backend for synth + opt + report
source common.tcl
