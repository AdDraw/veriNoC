#!/usr/bin/tclsh
yosys -import
echo on

set src ../srcs
set top_module mesh_wormhole_node

# Define parameter names + values (values taken from EnvVars set by yosys_wrapper.sh)
array set params {
  ROW_CORD 1
  COL_CORD 1
  IN_N 5
  OUT_M 5
  COL_ADDR_W 2
  ROW_ADDR_W 2
  FLIT_ID_W 2
  FLIT_DATA_W 8
  BUFFER_DEPTH_W 2
  ARB_TYPE 0
}

# File list
set files {
  components/circ_fifo.v
  switch/constants.v
  switch/arbiters/hop_cnt_arbiter.v
  switch/virtual_channels/virtual_channel.v
  switch/arbiters/matrix_arbiter.v
  switch/arbiters/round_robin_arbiter.v
  switch/arbiters/grant_with_carry.v
  switch/arbiters/static_priority_arbiter.v
  switch/routers/xy_router.v
  switch/crossbars/nxn_parrallel_crossbar.v
  switch/allocators/allocator.v
  switch/mesh_wormhole/mesh_wormhole_node.v
}

# Executes the basic backend for synth + opt + report
source common.tcl