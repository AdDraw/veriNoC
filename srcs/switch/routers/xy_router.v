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
`default_nettype none
module xy_router #(
  parameter COL_CORD   = 4'd0,
  parameter ROW_CORD   = 4'd0,
  parameter COL_ADDR_W = 4,
  parameter ROW_ADDR_W = 4,
  parameter OUT_M      = 5
) (
  input  wire [COL_ADDR_W-1:0] col_addr_i,
  input  wire [ROW_ADDR_W-1:0] row_addr_i,
  output wire [     OUT_M-1:0] oc_sel_o
);
  // mapped Directions to PORT IDs
  localparam RESOURCE = 0;
  localparam LEFT = 1;
  localparam NORTH = 2;
  localparam RIGHT = 3;
  localparam SOUTH = 4;

  reg  [     OUT_M-1:0] oc_sel;
  wire [COL_ADDR_W-1:0] col_cord_w = COL_CORD;
  wire [ROW_ADDR_W-1:0] row_cord_w = ROW_CORD;

  always @(*) begin
    oc_sel = {OUT_M{1'b0}};
    if (col_addr_i == col_cord_w) begin
      // X movement Finished, start in Y dimension
      if (row_addr_i == row_cord_w) begin
        // Y movement Finished, route to resource_id
        oc_sel[RESOURCE] = 1'b1;
      end else if (row_addr_i < row_cord_w) begin
        oc_sel[NORTH] = 1'b1;
      end else begin
        oc_sel[SOUTH] = 1'b1;
      end
    end else begin
      if (col_addr_i > col_cord_w) begin
        // X movement not finished
        oc_sel[RIGHT] = 1'b1;
      end else begin
        oc_sel[LEFT] = 1'b1;
      end
    end
  end

  assign oc_sel_o = oc_sel;

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
`default_nettype wire