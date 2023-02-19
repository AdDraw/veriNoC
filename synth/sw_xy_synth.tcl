#!/usr/bin/tclsh
yosys -import
echo on

set src ../srcs
set top_module xy_switch

# Define parameter names + values (values taken from EnvVars set by yosys_wrapper.sh)
array set params {
  ROW_CORD 1
  COL_CORD 1
  PORT_N 5
  FIFO_DEPTH_W 2
  COL_ADDR_W 2
  ROW_ADDR_W 2
  PCKT_DATA_W 64
  ARB_TYPE 0
}

# File list
set files {
  switch/constants.v
  components/circ_fifo.v
  switch/simple_mesh_xy/switch_constants.v
  switch/arbiters/matrix_arbiter.v
  switch/arbiters/round_robin_arbiter.v
  switch/arbiters/grant_with_carry.v
  switch/arbiters/static_priority_arbiter.v
  switch/routers/xy_router.v
  switch/crossbars/nxn_single_crossbar.v
  switch/simple_mesh_xy/control_unit.v
  switch/simple_mesh_xy/xy_switch.v
}

# Executes the basic backend for synth + opt + report
source common.tcl