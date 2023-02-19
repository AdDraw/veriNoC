/*
  Adam Drawc
  cocotb simulation Testbench wrapper for Virtual Channel module
*/
// `define FLIT_W (FLIT_DATA_W+FLIT_ID_W)
// `define FLIT_ID_RANGE `FLIT_W-1:`FLIT_W-FLIT_ID_W
`timescale 1ns / 1ps
module tb #(
  parameter VC_DEPTH_W  = 2,     // 4 flit buffer (for now)
  parameter FLIT_DATA_W = 8,
  parameter COL_CORD    = 4'd1,
  parameter FLIT_ID_W   = 2,
  parameter ROW_CORD    = 4'd1,
  parameter OUT_N_W     = 3,
  parameter COL_ADDR_W  = 2,
  parameter ROW_ADDR_W  = 2,
  parameter HOP_CNT_W   = 4,
  parameter CLK_PERIOD  = 10
) (
  input                rst_ni,
  // FIFO based input (data & wr_enable)
  input  [`FLIT_W-1:0] data_i,
  input                wr_en_i,
  // Allocator info input
  input                chan_alloc_i,    // HEADER won the competition info
  input                chan_rdy_i,      // BUFFER on the other side is not full
  // To Route
  output [`FLIT_W-1:0] data_o,
  output               data_vld_o,
  output [`FLIT_W-1:0] header_o,
  output [OUT_N_W-1:0] route_res_o,
  output               route_res_vld_o,

  // FIFO based output
  output rdy_o  // backpressure signal
);

  initial begin
    $display("TB SETUP:");
    $display("\t- FLIT_DATA_W %0d", FLIT_DATA_W);
    $display("\t- VC_DEPTH_W  %0d", VC_DEPTH_W);
    $display("\t- FLIT_ID_W   %0d", FLIT_ID_W);
    $display("\t- OUT_N_W     %0d", OUT_N_W);
    $display("\t- HOP_CNT_W   %0d", HOP_CNT_W);
    $display("\t- ROW_CORD    %0d", ROW_CORD);
    $display("\t- COL_CORD    %0d", COL_CORD);
    $display("\t- ROW_ADDR_W  %0d", ROW_ADDR_W);
    $display("\t- COL_ADDR_W  %0d", COL_ADDR_W);
    $display("\t- CLK_PERIOD  %0d", CLK_PERIOD);

  end

  reg clk_i = 1'b0;
  always #(CLK_PERIOD / 2) clk_i <= ~clk_i;

  virtual_channel #(
    .VC_DEPTH_W (VC_DEPTH_W),
    .FLIT_DATA_W(FLIT_DATA_W),
    .FLIT_ID_W  (FLIT_ID_W),
    .COL_CORD   (COL_CORD),
    .ROW_CORD   (ROW_CORD),
    .COL_ADDR_W (COL_ADDR_W),
    .ROW_ADDR_W (ROW_ADDR_W),
    .OUT_N_W    (OUT_N_W),
    .HOP_CNT_W  (HOP_CNT_W)
  ) vc_inst (
    .clk_i          (clk_i),
    .rst_ni         (rst_ni),
    .data_i         (data_i),
    .wr_en_i        (wr_en_i),
    .chan_alloc_i   (chan_alloc_i),
    .chan_rdy_i     (chan_rdy_i),
    .route_res_o    (route_res_o),
    .header_o       (header_o),
    .route_res_vld_o(route_res_vld_o),
    .data_o         (data_o),
    .data_vld_o     (data_vld_o),
    .rdy_o          (rdy_o)
  );

  // the "macro" to dump signals
`ifdef COCOTB_SIM
  initial begin
    $dumpfile("dump.vcd");
    $dumpvars(0, tb);
    #1;
  end
`endif

endmodule  //
