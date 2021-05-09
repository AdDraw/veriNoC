/*
  Adam Drawc @2021

  Node:
  - 2D MESH topology
  - flit-based FlowControl (WORMHOLE)
    - backpressure FIFO_FULL
  - Dimension Order Routing
  - M channel routes at once ( no longer 1 route as in simple mesh switch)
  - HOP COUNTs + STATIC PRIORITY arbitration

  Description:
  Each output channel has it's own input MUX and Resource ALLOCATOR.
  Each input channel has it's own ROUTER.

  TODO: ADD Driver for out_chan_data_vld_o!!!!!

*/
`timescale 1ns / 1ps
`define FLIT_W (FLIT_ID_W + FLIT_DATA_W)
`define ROW_ADDR_RANGE  `FLIT_W-FLIT_ID_W-1 : HOP_CNT_W + COL_ADDR_W
`define COL_ADDR_RANGE  HOP_CNT_W + COL_ADDR_W-1 : HOP_CNT_W
`define HOP_CNT_RANGE   HOP_CNT_W-1:0
module mesh_wormhole_node
  #(
  `ifdef `YS_MESH_WORMHOLE_NODE_TOP
    parameter IN_N            = `YS_IN_N,
    parameter OUT_M           = `YS_OUT_M,
    parameter FLIT_DATA_W     = `YS_FLIT_DATA_W,
    parameter FLIT_ID_W       = `YS_FLIT_ID_W,
    parameter HOP_CNT_W       = `YS_HOP_CNT_W,
    parameter ROW_ADDR_W      = `YS_ROW_ADDR_W,
    parameter COL_ADDR_W      = `YS_COL_ADDR_W,
    parameter ROW_CORD        = `YS_ROW_CORD,
    parameter COL_CORD        = `YS_COL_CORD,
    parameter BUFFER_DEPTH_W  = `YS_BUFFER_DEPTH_W
  `else
    parameter IN_N            = 5,
    parameter OUT_M           = 5,
    parameter FLIT_DATA_W     = 8,
    parameter FLIT_ID_W       = 2,
    parameter HOP_CNT_W       = 4,
    parameter ROW_ADDR_W      = 2,
    parameter COL_ADDR_W      = 2,
    parameter ROW_CORD        = 0,
    parameter COL_CORD        = 0,
    parameter BUFFER_DEPTH_W  = 2
  `endif
    )
  ( input clk_i,
    input rst_ni,

    // INPUT CHANNEL signals
    input   [(IN_N*`FLIT_W)-1:0]   in_chan_data_i,     // data in
    input   [IN_N-1:0]             in_chan_data_vld_i, // FIFO in wr_en
    output  [IN_N-1:0]             in_chan_rdy_o,      // FIFO in backpressure

    // Output channel Signals
    output  [(OUT_M*`FLIT_W)-1:0]  out_chan_data_o,     // data out
    output  [OUT_M-1:0]            out_chan_data_vld_o, // FIFO out wr_en
    input   [OUT_M-1:0]            out_chan_rdy_i,      // FIFO out backpressure
    );

  `ifdef SIMULATION
  initial begin
    if (FLIT_W == (HOP_CNT_W+ROW_ADDR_W+COL_ADDR_W)) begin
      $display("FLIT_W == HOP_CNT_W+ROW_ADDR_W+COL_ADDR_W");
      $display("FLIT_W  = %d", `FLIT_W);
      $display("SUM     = %d", (HOP_CNT_W+ROW_ADDR_W+COL_ADDR_W));
    end
    else begin
      $fatal("ERROR: FLIT_W != HOP_CNT_W+ROW_ADDR_W+COL_ADDR_W");
      $display("FLIT_W  = %d", `FLIT_W);
      $display("SUM     = %d", (HOP_CNT_W+ROW_ADDR_W+COL_ADDR_W));
    end
  end
  `endif

  genvar gi, gj;

  wire [(HOP_CNT_W*IN_N)-1:0]     vc_hop_cnt_w;   // sends hop_counts from input VCs to allocators
  wire [(`FLIT_W*IN_N)-1:0]       vc_data_out_w;  // sends the data out from VCs to the crossbar
  wire [($clog2(OUT_M)*IN_N)-1:0] vc_route_res_w; // sends the routing result from ROUTER to ALLOCATOR
  wire [(IN_N*FLIT_ID_W)-1:0]     flit_type_w;    // Sends the FLIT_TYPE to ALLOCATOR from VC
  wire [(OUT_M*$clog2(IN_N))-1:0] sel_w;          // SEL from allocator to CROSSBAR
  wire [IN_N-1:0]                 alloc_chan_alloc_w [OUT_M-1:0]; // FROM ALLOC to VC
  wire [OUT_M-1:0]                alloc_buffer_space_available_w; // FROM ALLOC to VC (alloc provides 1 bit)

  generate
    for(gi=0; gi<IN_N; gi=gi+1) begin
      wire [`FLIT_W-1:0]        x_data_in_w  = in_chan_data_i[(`FLIT_W*(gi+1))-1 : `FLIT_W*gi];
      wire [`FLIT_W-1:0]        x_header_w;
      wire [`FLIT_W-1:0]        x_data_out_w;
      wire [ROW_ADDR_W-1:0]     x_row_addr_w = x_header_w[`ROW_ADDR_RANGE];
      wire [COL_ADDR_W-1:0]     x_col_addr_w = x_header_w[`COL_ADDR_RANGE];
      wire [HOP_CNT_W-1:0]      x_hop_cnt_w  = x_header_w[`HOP_CNT_RANGE];

      wire                      x_vc_chan_alloc_w [OUT_M-1:0];
      for (gj=0; gj<OUT_M; gj=gj+1) begin
        wire [IN_N-1:0] x_alloc_chan_sel  = alloc_chan_alloc_w[gj];
        assign x_vc_chan_alloc_w[gj]      = x_alloc_chan_sel[gi];
      end

      // INPUT VIRTUAL CHANNELS (for WORMHOLE act as Physical Channels)
      virtual_channel
      #(
        .VC_DEPTH_W(BUFFER_DEPTH_W),
        .DATA_W(`FLIT_W),
        .ID_W(gi)
        )
      x_vc
      (
        .clk_i(clk_i),
        .rst_ni(rst_ni),
        .data_i(x_data_in_w),
        .wr_en_i(in_chan_data_vld_i[gi]),
        .chan_alloc_i(x_vc_chan_alloc_w[x_vc_route_res_w]),            // from allocator
        .chan_rdy_i(alloc_buffer_space_available_w[x_vc_route_res_w]), // from allocator
        .header_o(x_header_w),
        .data_o(x_data_out_w),
        .rdy_o(in_chan_rdy_o[gi])
        );

      assign vc_data_out_w[(`FLIT_W*(gi+1))-1 : `FLIT_W*gi]    = x_data_out_w;
      assign vc_hop_cnt_w[(HOP_CNT_W*(gi+1))-1: gi*HOP_CNT_W ] = x_hop_cnt_w;
      assign flit_type_w[(FLIT_ID_W*(gi+1))-1 : FLIT_ID_W*gi]  = x_data_out_w[`FLIT_W-1:`FLIT_W-FLIT_ID_W];

      // ROUTERS tied to VCs
      wire [$clog2(OUT_M)-1:0]  x_vc_route_res_w;

      xy_router
      # (
          .COL_CORD(COL_CORD),
          .ROW_CORD(ROW_CORD),
          .PACKET_ADDR_COL_W(COL_ADDR_W),
          .PACKET_ADDR_ROW_W(ROW_ADDR_W),
          .OUTPUT_N_W($clog2(OUT_M))
          )
      x_router
        (
          .col_addr_i(x_row_addr_w),
          .row_addr_i(x_col_addr_w),
          .out_chan_sel_o(x_vc_route_res_w)
          );

      assign vc_route_res_w[($clog2(OUT_M)*(gi+1))-1 : $clog2(OUT_M)*gi]  = x_vc_route_res_w;
    end

    for(gi=0; gi<OUT_M; gi=gi+1) begin

      wire [IN_N-1:0]         x_chan_alloc_w;
      wire                    x_buffer_space_available_w;
      wire [$clog2(IN_N)-1:0] x_alloc_sel_w;

      allocator
      #(
        .IN_N(IN_N),
        .OUT_M(OUT_M),
        .FLIT_ID_W(FLIT_ID_W),
        .HOP_CNT_W(HOP_CNT_W),
        .OUT_CHAN_ID(gi),
        )
      x_alloc
      (
        .clk_i(clk_i),
        .rst_ni(rst_ni),
        .rtr_res_i(vc_route_res_w),
        .hop_count_i(vc_hop_cnt_w),
        .flit_id_i(flit_type_w),
        .backpressure_fifo_full_i(~out_chan_rdy_i[gi]),
        .sel_o(x_alloc_sel_w),
        .buffer_space_available_o(x_buffer_space_available_w),  // to VCs
        .chan_alloc_o(x_chan_alloc_w) // to VCs
        );

        assign sel_w[($clog2(IN_N)*(gi+1))-1 : $clog2(IN_N)*gi] = x_alloc_sel_w;
        assign alloc_chan_alloc_w[gi]                           = x_chan_alloc_w;
        assign alloc_buffer_space_available_w[gi]               = x_buffer_space_available_w;
    end

    nxn_parrallel_crossbar
    #(
      .IN_N(IN_N),
      .OUT_M(OUT_M),
      .DATA_W(`FLIT_W)
      )
    crossbar
    (
      .data_i(vc_data_out_w),
      .sel_i(sel_w),
      .data_o(out_chan_data_o) //TODO: this is okay in the case when we don't set VLD_o, not how we want
      );

  endgenerate
endmodule // mesh_wormhole_node
