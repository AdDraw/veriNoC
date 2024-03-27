/*
  Adam Drawc
  cocotb simulation Testbench wrapper for Virtual Channel module
*/
`timescale 1ns / 1ps
module tb #(
  parameter NODE_RADIX     = 5,
  parameter FLIT_DATA_W    = 8,
  parameter FLIT_ID_W      = 2,
  parameter ROW_ADDR_W     = 2,
  parameter COL_ADDR_W     = 2,
  parameter ROW_CORD       = 0,
  parameter COL_CORD       = 0,
  parameter BUFFER_DEPTH_W = 2,
  parameter ARB_TYPE       = 0,
  parameter CLK_PERIOD     = 10,
  parameter FLIT_W         = FLIT_DATA_W + FLIT_ID_W
) (
  input rst_ni,

  // INPUT CHANNEL signals
  input  [FLIT_W-1:0] in_chan_data_i[NODE_RADIX-1:0],  // data in
  input  [   NODE_RADIX-1:0] in_chan_vld_i,             // FIFO in wr_en
  output [   NODE_RADIX-1:0] in_chan_rdy_o,             // FIFO in backpressure

  // Output channel Signals
  output [ FLIT_W-1:0] out_chan_data_o[NODE_RADIX-1:0],  // data out
  output [  NODE_RADIX-1:0] out_chan_vld_o,              // FIFO out wr_en
  input  [  NODE_RADIX-1:0] out_chan_rdy_i               // FIFO out backpressure
);

  initial begin
    $display("TB SETUP: Node wormhole mesh xy");
    $display("\t- NODE_RADIX      %0d", NODE_RADIX);
    $display("\t- FLIT_ID_W       %0d", FLIT_ID_W);
    $display("\t- FLIT_DATA_W     %0d", FLIT_DATA_W);
    $display("\t- ROW_CORD        %0d", ROW_CORD);
    $display("\t- COL_CORD        %0d", COL_CORD);
    $display("\t- ROW_ADDR_W      %0d", ROW_ADDR_W);
    $display("\t- COL_ADDR_W      %0d", COL_ADDR_W);
    $display("\t- BUFFER_DEPTH_W  %0d", BUFFER_DEPTH_W);
    $display("\t- CLK_PERIOD      %0d", CLK_PERIOD);
  end

  reg clk_i = 1'b0;
  always #(CLK_PERIOD / 2) clk_i <= ~clk_i;

  wire [NODE_RADIX-1:0][FLIT_W-1:0] idata_w;
  wire [NODE_RADIX-1:0][FLIT_W-1:0] odata_w;
  genvar i;
  generate
    for (i = 0; i < NODE_RADIX; i = i + 1) begin
      assign out_chan_data_o[i] = odata_w[i];
      assign idata_w[i] = in_chan_data_i[i];
    end
  endgenerate

  mesh_wormhole_node #(
    .IN_N          (NODE_RADIX),
    .OUT_M         (NODE_RADIX),
    .FLIT_DATA_W   (FLIT_DATA_W),
    .FLIT_ID_W     (FLIT_ID_W),
    .ROW_ADDR_W    (ROW_ADDR_W),
    .COL_ADDR_W    (COL_ADDR_W),
    .ROW_CORD      (ROW_CORD),
    .COL_CORD      (COL_CORD),
    .BUFFER_DEPTH_W(BUFFER_DEPTH_W),
    .ARB_TYPE      (ARB_TYPE)
  ) dut_inst (
    .clk_i          (clk_i),
    .rst_ni         (rst_ni),
    .in_chan_data_i (idata_w),
    .in_chan_vld_i  (in_chan_vld_i),
    .in_chan_rdy_o  (in_chan_rdy_o),
    .out_chan_rdy_i (out_chan_rdy_i),
    .out_chan_data_o(odata_w),
    .out_chan_vld_o (out_chan_vld_o)
  );

  // the "macro" to dump signals
`ifdef COCOTB_SIM
  initial begin
    // $dumpfile("dump.vcd");
    $dumpvars(0, tb);
    #1;
  end
`endif

endmodule  //
