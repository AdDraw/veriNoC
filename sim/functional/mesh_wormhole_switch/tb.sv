/*
  Adam Drawc
  cocotb simulation Testbench wrapper for Virtual Channel module
*/
`timescale 1ns / 1ps
module tb
  #(
    parameter IN_N            = 5,
    parameter OUT_M           = 5,
    parameter FLIT_DATA_W     = 8,
    parameter FLIT_ID_W       = 2,
    parameter HOP_CNT_W       = 4,
    parameter ROW_ADDR_W      = 2,
    parameter COL_ADDR_W      = 2,
    parameter ROW_CORD        = 0,
    parameter COL_CORD        = 0,
    parameter BUFFER_DEPTH_W  = 2,
    parameter ARB_TYPE        = 0,
    parameter CLK_PERIOD      = 10
    )
  (
    input rst_ni,

    // INPUT CHANNEL signals
    input   [`FLIT_W-1:0]   in_chan_data_i  [IN_N-1:0],  // data in
    input   [IN_N-1:0]      in_chan_vld_i,               // FIFO in wr_en
    output  [IN_N-1:0]      in_chan_rdy_o,               // FIFO in backpressure

    // Output channel Signals
    output  [`FLIT_W-1:0]   out_chan_data_o [OUT_M-1:0], // data out
    output  [OUT_M-1:0]     out_chan_vld_o,              // FIFO out wr_en
    input   [OUT_M-1:0]     out_chan_rdy_i               // FIFO out backpressure
    );

  initial begin
    $display("TB SETUP: Node wormhole mesh xy");
    $display("\t- IN_N            %0d", IN_N);
    $display("\t- OUT_M           %0d", OUT_M);
    $display("\t- FLIT_ID_W       %0d", FLIT_ID_W);
    $display("\t- FLIT_DATA_W     %0d", FLIT_DATA_W);
    $display("\t- HOP_CNT_W       %0d", HOP_CNT_W);
    $display("\t- ROW_CORD        %0d", ROW_CORD);
    $display("\t- COL_CORD        %0d", COL_CORD);
    $display("\t- ROW_ADDR_W      %0d", ROW_ADDR_W);
    $display("\t- COL_ADDR_W      %0d", COL_ADDR_W);
    $display("\t- BUFFER_DEPTH_W  %0d", BUFFER_DEPTH_W);
    $display("\t- CLK_PERIOD      %0d", CLK_PERIOD);
  end

  reg clk_i = 1'b0;
  always #(CLK_PERIOD/2) clk_i <= ~clk_i;

  genvar in_i, out_i;
  wire [(IN_N*`FLIT_W)-1:0]  data_iw;
  wire [(OUT_M*`FLIT_W)-1:0] data_ow;
  generate
      for (in_i = 0; in_i < IN_N; in_i=in_i+1) begin
        assign data_iw[`CALC_DATA_RANGE(in_i)] = in_chan_data_i[in_i];
      end
      for (out_i = 0; out_i < OUT_M; out_i=out_i+1) begin
        assign out_chan_data_o[out_i] = data_ow[`CALC_DATA_RANGE(out_i)];
      end
  endgenerate

  mesh_wormhole_node
  #(
    .IN_N(IN_N),
    .OUT_M(OUT_M),
    .FLIT_DATA_W(FLIT_DATA_W),
    .FLIT_ID_W(FLIT_ID_W),
    .HOP_CNT_W(HOP_CNT_W),
    .ROW_ADDR_W(ROW_ADDR_W),
    .COL_ADDR_W(COL_ADDR_W),
    .ROW_CORD(ROW_CORD),
    .COL_CORD(COL_CORD),
    .BUFFER_DEPTH_W(BUFFER_DEPTH_W),
    .ARB_TYPE(ARB_TYPE)
    )
  dut_inst
  (
    .clk_i(clk_i),
    .rst_ni(rst_ni),
    .in_chan_data_i(data_iw),
    .in_chan_vld_i(in_chan_vld_i),
    .in_chan_rdy_o(in_chan_rdy_o),
    .out_chan_rdy_i(out_chan_rdy_i),
    .out_chan_data_o(data_ow),
    .out_chan_vld_o(out_chan_vld_o)
    );

  // the "macro" to dump signals
  `ifdef COCOTB_SIM
  initial begin
    $dumpfile ("dump.vcd");
    $dumpvars (0, tb);
    #1;
  end
  `endif

endmodule //
