/*
  Adam Drawc @2020/2021

  Dimension-ordering Router
  - only supports 2D dimension ordering (XY)
  - first sends the data in X dimension -> Y dimension

  Right now it's good only for the MESH network (Torus might not work)
    indicated by the col row signal names
*/

`timescale 1ns / 1ps
module xy_router
# (
    `ifdef YS_ROUTER_TOP
    parameter COL_CORD    = `YS_COL_CORD,
    parameter ROW_CORD    = `YS_ROW_CORD,
    parameter COL_ADDR_W  = `YS_COL_ADDR_W,
    parameter ROW_ADDR_W  = `YS_ROW_ADDR_W,
    parameter OUT_N_W     = `YS_OUT_N_W
    `else
    parameter COL_CORD    = 4'd0,
    parameter ROW_CORD    = 4'd0,
    parameter COL_ADDR_W  = 4,
    parameter ROW_ADDR_W  = 4,
    parameter OUT_N_W     = 3
    `endif
    )
  (
    input  [COL_ADDR_W-1 : 0]  col_addr_i,
    input  [ROW_ADDR_W-1 : 0]  row_addr_i,
    output [OUT_N_W-1 : 0]     out_chan_sel_o
    );

    // Dimension-order / XY routing algorithm
    /*
      first X movement (at X = X_addr move in Y axis)
      next Y movement (stop at Y=Y_addr)
    */
    reg  [OUT_N_W-1 : 0]    out_chan_sel_v; //wire (indicated by _v)
    // For YOSYS to truncate the values
    wire [COL_ADDR_W-1 : 0] col_cord_w = COL_CORD;
    wire [ROW_ADDR_W-1 : 0] row_cord_w = ROW_CORD;

    // mapped Directions to PORT IDs
    wire  [OUT_N_W-1 : 0]   RESOURCE = 0;
    wire  [OUT_N_W-1 : 0]   LEFT     = 1;
    wire  [OUT_N_W-1 : 0]   UP       = 2;
    wire  [OUT_N_W-1 : 0]   RIGHT    = 3;
    wire  [OUT_N_W-1 : 0]   DOWN     = 4;

    always @(*) begin
      if (col_addr_i == col_cord_w) begin
        // X movement Finished, start in Y dimension
        if (row_addr_i == row_cord_w) begin
        // Y movement Finished, route to Resource
          out_chan_sel_v = RESOURCE;
        end
        else if (row_addr_i < row_cord_w) begin
          out_chan_sel_v = UP;
        end
        else begin
          out_chan_sel_v = DOWN;
        end
      end
      else begin
        if (col_addr_i > col_cord_w) begin
          // X movement not finished
          out_chan_sel_v = RIGHT;
        end
        else begin
          out_chan_sel_v = LEFT;
        end
      end
    end

    assign out_chan_sel_o = out_chan_sel_v;

    `ifdef LOG_DEBUG
      initial begin
        $display("OUT_N_W %d", OUT_N_W);
        $display("LEFT    %d", LEFT);
        $display("UP      %d", UP);
        $display("RIGHT   %d", RIGHT);
        $display("DOWN    %d", DOWN);
      end
    `endif
endmodule
