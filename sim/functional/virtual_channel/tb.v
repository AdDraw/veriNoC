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
  parameter OUT_M       = 5,
  parameter COL_ADDR_W  = 2,
  parameter ROW_ADDR_W  = 2,
  parameter CLK_PERIOD  = 10,
  parameter FLIT_W      = FLIT_DATA_W + FLIT_ID_W
) (
  input                rst_ni,
  // FIFO based input (data & wr_enable)
  input  [FLIT_W-1:0]  data_i,
  input                wr_en_i,
  output               rdy_o,  // backpressure signal
  // Allocator info input
  input               oc_granted_i,  // HEADER won the competition info
  input               oc_rdy_i,      // BUFFER on the other side is not full
  // To Route
  output [FLIT_W-1:0] oc_data_o,
  output              oc_data_vld_o,
  output [OUT_M-1:0]  oc_req_o,
  output              oc_flit_id_is_tail_o
);

  initial begin
    $display("TB SETUP:");
    $display("\t- FLIT_DATA_W %0d", FLIT_DATA_W);
    $display("\t- VC_DEPTH_W  %0d", VC_DEPTH_W);
    $display("\t- FLIT_ID_W   %0d", FLIT_ID_W);
    $display("\t- OUT_M     %0d", OUT_M);
    $display("\t- ROW_CORD    %0d", ROW_CORD);
    $display("\t- COL_CORD    %0d", COL_CORD);
    $display("\t- ROW_ADDR_W  %0d", ROW_ADDR_W);
    $display("\t- COL_ADDR_W  %0d", COL_ADDR_W);
    $display("\t- CLK_PERIOD  %0d", CLK_PERIOD);

  end

  reg clk_i = 1'b0;
  always #(CLK_PERIOD / 2) clk_i <= ~clk_i;

  virtual_channel # (
    .VC_DEPTH_W(VC_DEPTH_W),
    .FLIT_DATA_W(FLIT_DATA_W),
    .COL_CORD(COL_CORD),
    .FLIT_ID_W(FLIT_ID_W),
    .ROW_CORD(ROW_CORD),
    .OUT_M(OUT_M),
    .COL_ADDR_W(COL_ADDR_W),
    .ROW_ADDR_W(ROW_ADDR_W)
  ) virtual_channel_inst (
    .clk_i(clk_i),
    .rst_ni(rst_ni),
    .data_i(data_i),
    .wr_en_i(wr_en_i),
    .rdy_o(rdy_o),
    .oc_req_o(oc_req_o),
    .oc_flit_id_is_tail_o(oc_flit_id_is_tail_o),
    .oc_granted_i(oc_granted_i),
    .oc_data_o(oc_data_o),
    .oc_data_vld_o(oc_data_vld_o),
    .oc_rdy_i(oc_rdy_i)
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
