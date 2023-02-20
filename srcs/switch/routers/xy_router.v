/*
  Adam Drawc @2020/2021

  Dimension-ordering Router
  - only supports 2D dimension ordering (XY)
  - first sends the data in X dimension -> Y dimension

  Right now it's good only for the MESH network (Torus might not work)
    indicated by the col row signal names

  Dimension-order / XY routing algorithm
    1. X movement (at X = X_addr move in Y axis)
    2. Y movement (stop at Y=Y_addr)
*/

`timescale 1ns / 1ps
module xy_router #(
  parameter COL_CORD   = 4'd0,
  parameter ROW_CORD   = 4'd0,
  parameter COL_ADDR_W = 4,
  parameter ROW_ADDR_W = 4,
  parameter OUT_N_W    = 3
) (
  input  [COL_ADDR_W-1 : 0] col_addr_i,
  input  [ROW_ADDR_W-1 : 0] row_addr_i,
  output [   OUT_N_W-1 : 0] out_chan_sel_o
);

  reg  [   OUT_N_W-1 : 0]                        out_chan_sel_v;

  // For YOSYS to truncate the values
  wire [COL_ADDR_W-1 : 0] col_cord_w = COL_CORD;
  wire [ROW_ADDR_W-1 : 0] row_cord_w = ROW_CORD;

  // mapped Directions to PORT IDs
  wire [   OUT_N_W-1 : 0] resource_id = 0;
  wire [   OUT_N_W-1 : 0] left_id = 1;
  wire [   OUT_N_W-1 : 0] up_id = 2;
  wire [   OUT_N_W-1 : 0] right_id = 3;
  wire [   OUT_N_W-1 : 0] down_id = 4;

  always @(*) begin
    if (col_addr_i == col_cord_w) begin
      // X movement Finished, start in Y dimension
      if (row_addr_i == row_cord_w) begin
        // Y movement Finished, route to resource_id
        out_chan_sel_v = resource_id;
      end else if (row_addr_i < row_cord_w) begin
        out_chan_sel_v = up_id;
      end else begin
        out_chan_sel_v = down_id;
      end
    end else begin
      if (col_addr_i > col_cord_w) begin
        // X movement not finished
        out_chan_sel_v = right_id;
      end else begin
        out_chan_sel_v = left_id;
      end
    end
  end

  assign out_chan_sel_o = out_chan_sel_v;

`ifdef LOG_DEBUG
  initial begin
    $display("OUT_N_W %d", OUT_N_W);
    $display("LEFT    %d", left_id);
    $display("UP      %d", up_id);
    $display("RIGHT   %d", right_id);
    $display("DOWN    %d", down_id);
  end
`endif
endmodule
