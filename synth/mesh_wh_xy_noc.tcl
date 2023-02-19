#!/usr/bin/tclsh
yosys -import
echo on

set src ../srcs
set top_module mesh_wormhole_xy_noc

# Define parameter names + values (values taken from EnvVars set by yosys_wrapper.sh)
array set params {
  ROW_N 3
  COL_M 3
  NODE_RADIX 5
  CHANNEL_W 10
  FLIT_ID_W 2
  NODE_BUFFER_DEPTH_W 2
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
  noc/mesh_wormhole_xy_noc.v
}

# Executes the basic backend for synth + opt + report
source common.tcl