#!/usr/bin/tclsh
yosys -import
echo on

set src ../srcs
set top_module hop_cnt_arbiter

# Define parameter names + values (values taken from EnvVars set by yosys_wrapper.sh)
array set params {
  IN_N 5
  HOP_CNT_W 3
}

# File list
set files {
  switch/constants.v
  switch/arbiters/hop_cnt_arbiter.v
}

# Executes the basic backend for synth + opt + report
source common.tcl
