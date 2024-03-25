#!/usr/bin/tclsh
yosys -import
echo on

set src ../srcs
set top_module allocator

# Define parameter names + values (values taken from EnvVars set by yosys_wrapper.sh)
array set params {
  IN_N 5
  ARB_TYPE 0
}

# File list
set files {
  switch/constants.v
  switch/arbiters/matrix_arbiter.v
  switch/arbiters/round_robin_arbiter.v
  switch/arbiters/grant_with_carry.v
  switch/arbiters/static_priority_arbiter.v
  switch/allocators/allocator.sv
}

# Executes the basic backend for synth + opt + report
source common.tcl
