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
*/

`timescale 1ns / 1ps
`define FLIT_W FLIT_ID_W + FLIT_DATA_W
`define ROW_ADDR_RANGE  `FLIT_W-FLIT_ID_W-1 : HOP_CNT_W + COL_ADDR_W
`define COL_ADDR_RANGE  HOP_CNT_W + COL_ADDR_W-1 : HOP_CNT_W
`define HOP_CNT_RANGE   HOP_CNT_W-1:0
module mesh_wormhole_node
  #(parameter IN_N            = 5,
    parameter OUT_M           = 5,
    parameter FLIT_DATA_W     = 8,
    parameter FLIT_ID_W       = 2,
    parameter HOP_CNT_W       = 4,
    parameter ROW_ADDR_W      = 2,
    parameter COL_ADDR_W      = 2,
    parameter ROW_CORD        = 0,
    parameter COL_CORD        = 0,
    parameter BUFFER_DEPTH_W  = 2
    )
  ( input clk_i,
    input rst_ni,

    // INPUT CHANNEL signals
    input   [(IN_N*`FLIT_W)-1:0]   in_chan_data_i;     // data in
    input   [IN_N-1:0]             in_chan_data_vld_i; // FIFO in wr_en
    output  [IN_N-1:0]             in_chan_rdy_o;      // FIFO in backpressure

    // Output channel Signals
    output  [(OUT_M*`FLIT_W)-1:0]  out_chan_data_o;     // data out
    output  [OUT_M-1:0]            out_chan_data_vld_o; // FIFO out wr_en
    input   [OUT_M-1:0]            out_chan_rdy_i;      // FIFO out backpressure
    );

    initial begin
      assert(FLIT_DATA_W == HOP_CNT_W+ROW_ADDR_W+COL_ADDR_W);
    end

    genvar gi;

    wire [(HOP_CNT_W*IN_N)-1:0]     vc_hop_cnt_w;
    wire [(`FLIT_W*IN_N)-1:0]       vc_data_out_w;
    wire [($clog2(OUT_M)*IN_N)-1:0] route_res_w;

    generate
      for(gi=0; gi<IN_N; gi=gi+1)
        wire [`FLIT_W-1:0]        x_data_in_w  = in_chan_data_i[`FLIT_W *(gi+1)-1 : `FLIT_W*gi]
        wire [`FLIT_W-1:0]        x_header_w;
        wire [ROW_ADDR_W-1:0]     x_row_addr_w = x_header_w[`ROW_ADDR_RANGE];
        wire [COL_ADDR_W-1:0]     x_col_addr_w = x_header_w[`COL_ADDR_RANGE];
        wire [HOP_CNT_W-1:0]      x_hop_cnt_w  = x_header_w[`HOP_CNT_RANGE];
        wire [$clog2(OUT_M)-1:0]  x_route_res_w;

        // INPUT VIRTUAL CHANNELS
        virtual_channel
        #(
          .FIFO_DEPTH_W(BUFFER_DEPTH_W),
          .DATA_W(`FLIT_W),
          .ID_W(gi)
          );
        x_vc
        (
          .clk_i(clk_i),
          .rst_ni(rst_ni),
          .data_i(vc_data_in_w[gi]),
          .wr_en_i(in_chan_data_vld_i[gi]),
          .chan_alloc_i(), // from allocator
          .chan_rdy_i(),   // from allocator
          .header_o(x_header_w),
          .data_o(vc_data_out_w[`FLIT_W *(gi+1)-1 : `FLIT_W*gi]),
          .rdy_o(in_chan_rdy_o[gi])
          );

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
            .out_chan_sel_o(route_res_w[gi])
            );
      end

      for(gi=0; gi<OUT_M; gi=gi+1)

        // ALLOCATOR
      end

      nxn_parrallel_crossbar
      #(
        .IN_N(IN_N),
        .OUT_M(OUT_M),
        .DATA_W(`FLIT_W)
        );
      (
        .data_i(vc_data_out_w),
        .sel_i(),
        .data_o(out_chan_data_o) //TODO: this is okay in the case when we don't set VLD_o, not how we want
        );

    endgenerate
endmodule // mesh_wormhole_node
