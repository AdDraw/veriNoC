module xy_router
# (
    parameter X_CORD = 0,
    parameter Y_CORD = 0,
    parameter PACKET_ADDR_X_W = 4,
    parameter PACKET_ADDR_Y_W = 4,
    parameter OUTPUT_N_W = 3
    )
  (
    input  [PACKET_ADDR_X_W-1 : 0] x_addr,
    input  [PACKET_ADDR_Y_W-1 : 0] y_addr,
    output [OUTPUT_N_W-1 : 0] mux_out_sel_o
    );

    localparam RESOURCE = 3'd0;
    localparam WEST     = 3'd1;
    localparam EAST     = 3'd2;
    localparam NORTH    = 3'd3;
    localparam SOUTH    = 3'd4;

    // XY algorithm
    /*
      first X movement (at X = X_addr move in Y axis)
      next Y movement (stop at Y=Y_addr)

    */
    reg [OUTPUT_N_W-1 : 0] mux_out_sel_w;

    always @(*) begin
        if (x_addr == X_CORD ) begin
          // X movement Finished, start ELEVATION or DEELEVATION
          if (y_addr == Y_CORD) begin
          // Y movement Finished, route to Resource
            mux_out_sel_w = RESOURCE;
          end
          else if (y_addr > Y_CORD) begin
            mux_out_sel_w = NORTH;
          end
          else begin
            mux_out_sel_w = SOUTH;
          end
        end
        else begin
          if (x_addr > X_CORD) begin
            // X movement not finished
            mux_out_sel_w = EAST;
          end
          else begin
            mux_out_sel_w = WEST;
          end
        end
    end

endmodule
