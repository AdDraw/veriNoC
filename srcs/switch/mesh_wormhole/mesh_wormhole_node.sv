/*
  Adam Drawc @2021-2024

  Node:
  - 2D MESH topology
  - flit-based FlowControl (WORMHOLE)
    - backpressure FIFO_FULL
  - Dimension Order Routing
  - M channel routes at once ( no longer 1 route as in simple mesh switch)

  Description:
  Each output channel has it's own input MUX and Resource ALLOCATOR.
  Each input channel has it's own ROUTER.

*/
`timescale 1ns / 1ps `default_nettype none
module mesh_wormhole_node #(
  parameter IN_N           = 5,
  parameter OUT_M          = 5,
  parameter FLIT_DATA_W    = 8,
  parameter FLIT_ID_W      = 2,
  parameter ROW_ADDR_W     = 2,
  parameter COL_ADDR_W     = 2,
  parameter ROW_CORD       = 1,
  parameter COL_CORD       = 1,
  parameter BUFFER_DEPTH_W = 2,
  parameter ARB_TYPE       = 0,
  parameter FLIT_W         = FLIT_ID_W + FLIT_DATA_W,
  parameter TAIL_ID        = 2'b11,
  parameter HEADER_ID      = 2'b10,
  parameter PAYLOAD_ID     = 2'b01
) (
  input  wire                       clk_i,
  input  wire                       rst_ni,
  // INPUT CHANNEL signals
  input  wire [IN_N-1:0][FLIT_W-1:0] in_chan_data_i,  // data in
  input  wire [            IN_N-1:0] in_chan_vld_i,   // FIFO in wr_en
  output wire [            IN_N-1:0] in_chan_rdy_o,   // FIFO in backpressure

  // Output channel Signals
  output wire [OUT_M-1:0][FLIT_W-1:0] out_chan_data_o,  // data out
  output wire [            OUT_M-1:0] out_chan_vld_o,   // FIFO out wr_en
  input  wire [            OUT_M-1:0] out_chan_rdy_i    // FIFO out backpressure
);
  // Wires
  wire [               IN_N-1:0] ic_data_vld_w;
  wire [   IN_N-1:0][FLIT_W-1:0] ic_data_out_w;  // sends Data from VCs to the crossbar
  wire [    IN_N-1:0][OUT_M-1:0] ic_req_w;  // sends Routing result from ROUTER to ALLOCATOR

  wire [               IN_N-1:0] flit_id_is_tail_w;  // assert only if flit_id_is_tail
  wire [    IN_N-1:0][OUT_M-1:0] oc_grant_w;  // SEL from allocator to CROSSBAR

  wire [OUT_M-1:0][FLIT_W-1:0] out_chan_data_w;

  // Generate Blocks
  genvar ic, oc;
  generate
    for (ic = 0; ic < IN_N; ic = ic + 1) begin : GEN_INPUT_CHANNEL
      // INPUT VIRTUAL CHANNELS (for WORMHOLE act as Physical Channels)
      virtual_channel # (
        .VC_DEPTH_W(BUFFER_DEPTH_W),
        .FLIT_DATA_W(FLIT_DATA_W),
        .COL_CORD(COL_CORD),
        .FLIT_ID_W(FLIT_ID_W),
        .ROW_CORD(ROW_CORD),
        .OUT_M(OUT_M),
        .COL_ADDR_W(COL_ADDR_W),
        .ROW_ADDR_W(ROW_ADDR_W),
        .HEADER_ID(HEADER_ID),
        .TAIL_ID(TAIL_ID),
        .FLIT_W(FLIT_W)
      ) x_input_channel(
        .clk_i(clk_i),
        .rst_ni(rst_ni),
        .data_i(in_chan_data_i[ic]),
        .wr_en_i(in_chan_vld_i[ic]),
        .rdy_o(in_chan_rdy_o[ic]),
        .oc_req_o(ic_req_w[ic]),
        .oc_flit_id_is_tail_o(flit_id_is_tail_w[ic]),
        .oc_granted_i(|oc_grant_w[ic]), // maybe it's best to match it with request coming out of the VC
        .oc_data_o(ic_data_out_w[ic]),
        .oc_data_vld_o(ic_data_vld_w[ic]),
        .oc_rdy_i(|(out_chan_rdy_i & oc_grant_w[ic])) // only check rdy from a valid out channel(based on grant)
      );
    end

    for (oc = 0; oc < OUT_M; oc = oc + 1) begin : GEN_ALLOC
      wire [IN_N-1:0] x_alloc_req_w;
      wire [IN_N-1:0] x_grant_w;
      for (ic = 0; ic < IN_N; ic = ic + 1) begin
        assign x_alloc_req_w[ic]  = ic_req_w[ic][oc];
        assign oc_grant_w[ic][oc] = x_grant_w[ic];
      end

      output_channel # (
        .IN_N(IN_N),
        .ARB_TYPE(ARB_TYPE),
        .DATA_W(FLIT_W)
      ) x_output_channel (
        .clk_i(clk_i),
        .rst_ni(rst_ni),
        .req_i(x_alloc_req_w),
        .grant_o(x_grant_w),
        .data_vld_i(ic_data_vld_w),
        .flit_id_is_tail_i(flit_id_is_tail_w),
        .oc_rdy_i(out_chan_rdy_i[oc]),
        .oc_vld_o(out_chan_vld_o[oc]),
        .ic_data_i(ic_data_out_w),
        .oc_data_o(out_chan_data_o[oc])
      );
    end

  endgenerate
endmodule  // mesh_wormhole_node
`default_nettype wire
