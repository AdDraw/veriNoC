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
module mesh_wormhole_node #(
  `ifdef YS_MESH_WORMHOLE_NODE_TOP
    parameter IN_N            = `YS_IN_N,
    parameter OUT_M           = `YS_OUT_M,
    parameter FLIT_DATA_W     = `YS_FLIT_DATA_W,
    parameter FLIT_ID_W       = `YS_FLIT_ID_W,
    parameter ROW_ADDR_W      = `YS_ROW_ADDR_W,
    parameter COL_ADDR_W      = `YS_COL_ADDR_W,
    parameter ROW_CORD        = `YS_ROW_CORD,
    parameter COL_CORD        = `YS_COL_CORD,
    parameter BUFFER_DEPTH_W  = `YS_BUFFER_DEPTH_W,
    parameter ARB_TYPE        = `YS_ARB_TYPE
  `else
    parameter IN_N            = 5,
    parameter OUT_M           = 5,
    parameter FLIT_DATA_W     = 8,
    parameter FLIT_ID_W       = 2,
    parameter ROW_ADDR_W      = 2,
    parameter COL_ADDR_W      = 2,
    parameter ROW_CORD        = 1,
    parameter COL_CORD        = 1,
    parameter BUFFER_DEPTH_W  = 2,
    parameter ARB_TYPE        = 0
  `endif
  ) (
    input clk_i,
    input rst_ni,
    // INPUT CHANNEL signals
    input   [(IN_N*`FLIT_W)-1:0]   in_chan_data_i,  // data in
    input   [IN_N-1:0]             in_chan_vld_i,   // FIFO in wr_en
    output  [IN_N-1:0]             in_chan_rdy_o,   // FIFO in backpressure

    // Output channel Signals
    output  [(OUT_M*`FLIT_W)-1:0]  out_chan_data_o, // data out
    output  [OUT_M-1:0]            out_chan_vld_o,  // FIFO out wr_en
    input   [OUT_M-1:0]            out_chan_rdy_i   // FIFO out backpressure
  );

  wire [OUT_M-1:0]                out_chan_vld_w;
  wire [(OUT_M*`FLIT_W)-1:0]      out_chan_data_w;
  reg  [OUT_M-1:0]                out_chan_vld;
  reg  [(OUT_M*`FLIT_W)-1:0]      out_chan_data;
  // Wires
  wire [IN_N-1:0]                 vc_data_vld_w;
  wire [(`FLIT_W*IN_N)-1:0]       vc_data_out_w;      // sends Data from VCs to the crossbar
  wire [($clog2(OUT_M)*IN_N)-1:0] vc_route_res_w;     // sends Routing result from ROUTER to ALLOCATOR
  wire [IN_N-1:0]                 vc_route_res_vld_w;
  wire [(IN_N*FLIT_ID_W)-1:0]     flit_type_w;        // Sends FLIT_TYPE to ALLOCATOR from VC
  wire [(OUT_M*$clog2(IN_N))-1:0] sel_w;              // SEL from allocator to CROSSBAR
  wire [(OUT_M*IN_N)-1:0]         out_chan_alloc_w;   // FROM ALLOC to VC

  // Generate Blocks
  genvar gi, gj;
  generate
    for(gi=0; gi<IN_N; gi=gi+1)
    begin: GEN_INPUT_CHANNEL
      wire [`FLIT_W-1:0]        x_header_w;
      wire [`FLIT_W-1:0]        x_data_out_w;
      wire [$clog2(OUT_M)-1:0]  x_vc_route_res_w;
      wire                      x_vc_route_res_vld_w;

      wire [OUT_M-1:0]          x_vc_chan_alloc_w;
      for (gj=0; gj<OUT_M; gj=gj+1) // for each output channel
      begin: alloc_gen
        assign x_vc_chan_alloc_w[gj] = out_chan_alloc_w[gj*IN_N+gi]; // only take 1 bit that is for the current VC
      end

      // INPUT VIRTUAL CHANNELS (for WORMHOLE act as Physical Channels)
      virtual_channel #(
        .VC_DEPTH_W   (BUFFER_DEPTH_W),
        .FLIT_DATA_W  (FLIT_DATA_W),
        .FLIT_ID_W    (FLIT_ID_W),
        .COL_CORD     (COL_CORD),
        .ROW_CORD     (ROW_CORD),
        .COL_ADDR_W   (COL_ADDR_W),
        .ROW_ADDR_W   (ROW_ADDR_W),
        .OUT_N_W      ($clog2(OUT_M))
        )
      x_vc (
        .clk_i          (clk_i),
        .rst_ni         (rst_ni),
        .data_i         (in_chan_data_i[`UNPACK(gi, `FLIT_W)]),
        .wr_en_i        (in_chan_vld_i[gi]),
        .chan_alloc_i   (x_vc_chan_alloc_w[x_vc_route_res_w]),
        .chan_rdy_i     (out_chan_rdy_i[x_vc_route_res_w]),
        .data_vld_o     (vc_data_vld_w[gi]),
        .route_res_o    (x_vc_route_res_w),
        .header_o       (x_header_w),
        .route_res_vld_o(vc_route_res_vld_w[gi]),
        .data_o         (x_data_out_w),
        .rdy_o          (in_chan_rdy_o[gi])
        );

      assign vc_data_out_w[`UNPACK(gi, `FLIT_W)]        = x_data_out_w;
      assign flit_type_w[`UNPACK(gi, FLIT_ID_W)]        = x_data_out_w[`FLIT_ID_RANGE];
      assign vc_route_res_w[`UNPACK(gi, $clog2(OUT_M))] = x_vc_route_res_w;
    end

    for(gi=0; gi<OUT_M; gi=gi+1)
    begin: GEN_ALLOC
      wire [IN_N-1:0]         x_chan_alloc_w;
      wire [$clog2(IN_N)-1:0] x_alloc_sel_w;

      allocator #(
        .IN_N(IN_N),
        .OUT_M(OUT_M),
        .FLIT_ID_W(FLIT_ID_W),
        .OUT_CHAN_ID(gi),
        .ARB_TYPE(ARB_TYPE)
        )
      x_alloc (
        .clk_i(clk_i),
        .rst_ni(rst_ni),
        .rtr_res_i(vc_route_res_w),
        .rtr_res_vld_i(vc_route_res_vld_w),
        .flit_id_i(flit_type_w),
        .forward_node_rdy_i(out_chan_rdy_i[gi]),
        .data_vld_i(vc_data_vld_w),
        .sel_o(x_alloc_sel_w),
        .out_vld_o(out_chan_vld_o[gi]),
        .chan_alloc_o(x_chan_alloc_w)
        );

        assign sel_w[`UNPACK(gi, $clog2(IN_N))]    = x_alloc_sel_w;
        assign out_chan_alloc_w[`UNPACK(gi, IN_N)] = x_chan_alloc_w;
    end

    nxn_parrallel_crossbar #(
      .IN_N(IN_N),
      .OUT_M(OUT_M),
      .DATA_W(`FLIT_W)
      )
    crossbar (
      .data_i(vc_data_out_w),
      .sel_i(sel_w),
      .data_o(out_chan_data_o)
      );

  endgenerate
endmodule // mesh_wormhole_node
