#!/usr/bin/tclsh
yosys -import
echo on

set src ../srcs
set top_module mesh_xy_noc

# Define parameter names + values (values taken from EnvVars set by yosys_wrapper.sh)
array set params {
  ROW_N 4
  COL_M 4
  PCKT_DATA_W 8
  FIFO_DEPTH_W 4
  ARB_TYPE 0
}

# File list
set files {
  switch/simple_mesh_xy/switch_constants.v
  components/circ_fifo.v
  switch/constants.v
  switch/arbiters/matrix_arbiter.v
  switch/arbiters/round_robin.v
  switch/arbiters/static_priority_arbiter.v
  switch/routers/xy_router.v
  switch/crossbars/nxn_single_crossbar.v
  switch/simple_mesh_xy/control_unit.v
  switch/simple_mesh_xy/xy_switch.v
  noc/mesh_xy_noc.v
}

# Executes the basic backend for synth + opt + report
source common.tcl
