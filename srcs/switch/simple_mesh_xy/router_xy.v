// `include "./switch_params.v"

module xy_router
# (
    parameter X_CORD          = 4'd0,
    parameter Y_CORD          = 4'd0,
    parameter PACKET_ADDR_X_W = 4,
    parameter PACKET_ADDR_Y_W = 4,
    parameter OUTPUT_N_W      = 3,
    parameter SW_CONFIG       = `EDGE_LB
    )
  (
    input  [PACKET_ADDR_X_W-1 : 0] x_addr,
    input  [PACKET_ADDR_Y_W-1 : 0] y_addr,
    output [OUTPUT_N_W-1 : 0] mux_out_sel_o
    );

    // XY algorithm
    /*
      first X movement (at X = X_addr move in Y axis)
      next Y movement (stop at Y=Y_addr)

    */
    reg [OUTPUT_N_W-1 : 0] mux_out_sel_w;

    // For YOSYS to truncate the values
    wire [PACKET_ADDR_X_W-1 : 0] x_cord = X_CORD;
    wire [PACKET_ADDR_Y_W-1 : 0] y_cord = Y_CORD;

    // mapped Directions to PORT IDs
    // Packets that were incorrectly routed will land into Resource! (for now)
    // it's being done this way because SBY & Yosys have some weird problems
    // with a generate that sets localparam valus
    generate
      wire  [OUTPUT_N_W-1 : 0]   RESOURCE = 0;
      wire  [OUTPUT_N_W-1 : 0]   LEFT;
      wire  [OUTPUT_N_W-1 : 0]   UP;
      wire  [OUTPUT_N_W-1 : 0]   RIGHT;
      wire  [OUTPUT_N_W-1 : 0]   DOWN;

      case (SW_CONFIG)
        `CENTER: begin
          assign LEFT  = 1;
          assign UP    = 2;
          assign RIGHT = 3;
          assign DOWN  = 4;
        end
        `EDGE_RT: begin
          assign LEFT  = 1;
          assign UP    = 0;
          assign RIGHT = 0;
          assign DOWN  = 2;
        end
        `EDGE_LT: begin
          assign LEFT  = 0;
          assign UP    = 0;
          assign RIGHT = 1;
          assign DOWN  = 2;
        end
        `EDGE_RB: begin
          assign LEFT  = 1;
          assign UP    = 2;
          assign RIGHT = 0;
          assign DOWN  = 0;
        end
        `EDGE_LB: begin
          assign LEFT  = 0;
          assign UP    = 1;
          assign RIGHT = 2;
          assign DOWN  = 0;
        end
        `SIDE_R: begin
          assign LEFT  = 1;
          assign UP    = 2;
          assign RIGHT = 0;
          assign DOWN  = 3;
        end
        `SIDE_L: begin
          assign LEFT  = 0;
          assign UP    = 1;
          assign RIGHT = 2;
          assign DOWN  = 3;
        end
        `SIDE_T: begin
          assign LEFT  = 1;
          assign UP    = 0;
          assign RIGHT = 2;
          assign DOWN  = 3;
        end
        `SIDE_B: begin
          assign LEFT  = 1;
          assign UP    = 2;
          assign RIGHT = 3;
          assign DOWN  = 0;
        end
        default: begin
          assign LEFT  = 0;
          assign UP    = 0;
          assign RIGHT = 0;
          assign DOWN  = 0;
        end

      endcase
    endgenerate

    always @(*) begin
        /* verilator lint_off WIDTH */
        if (x_addr == x_cord) begin
          // X movement Finished, start ELEVATION or DEELEVATION
          if (y_addr == Y_CORD) begin
          // Y movement Finished, route to Resource
            mux_out_sel_w = RESOURCE;
          end
          else if (y_addr < y_cord) begin
            mux_out_sel_w = UP;
          end
          else begin
            mux_out_sel_w = DOWN;
          end
        end
        else begin
          if (x_addr > X_CORD) begin
            // X movement not finished
            mux_out_sel_w = RIGHT;
          end
          else begin
            mux_out_sel_w = LEFT;
          end
        end
        /* verilator lint_on WIDTH */
    end

    assign mux_out_sel_o = mux_out_sel_w;

    `ifdef SIMULATION
      initial begin
        $display("SW_CONF %d", SW_CONFIG);
        $display("PORT_N  %d", OUTPUT_N_W);
        $display("LEFT    %d", LEFT);
        $display("UP      %d", UP);
        $display("RIGHT   %d", RIGHT);
        $display("DOWN    %d", DOWN);
      end
    `endif

endmodule
