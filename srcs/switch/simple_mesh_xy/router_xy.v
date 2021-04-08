// `include "./switch_params.v"
`timescale 1ns / 1ps
module xy_router
# (
    `ifdef YS_ROUTER_TOP
    parameter COL_CORD          = `YS_COL_CORD,
    parameter ROW_CORD          = `YS_ROW_CORD,
    parameter PACKET_ADDR_COL_W = `YS_PACKET_ADDR_COL_W,
    parameter PACKET_ADDR_ROW_W = `YS_PACKET_ADDR_ROW_W,
    parameter OUTPUT_N_W        = `YS_OUTPUT_N_W,
    parameter SW_CONFIG         = `YS_SW_CONFIG
    `else
    parameter COL_CORD          = 4'd0,
    parameter ROW_CORD          = 4'd0,
    parameter PACKET_ADDR_COL_W = 4,
    parameter PACKET_ADDR_ROW_W = 4,
    parameter OUTPUT_N_W        = 3,
    parameter SW_CONFIG         = `EDGE_LB
    `endif
    )
  (
    input  [PACKET_ADDR_COL_W-1 : 0] col_addr,
    input  [PACKET_ADDR_ROW_W-1 : 0] row_addr,
    output [OUTPUT_N_W-1 : 0] mux_out_sel_o
    );

    // XY algorithm
    /*
      first X movement (at X = X_addr move in Y axis)
      next Y movement (stop at Y=Y_addr)

    */
    reg [OUTPUT_N_W-1 : 0] mux_out_sel_w;

    // For YOSYS to truncate the values
    wire [PACKET_ADDR_COL_W-1 : 0] col_cord = COL_CORD;
    wire [PACKET_ADDR_ROW_W-1 : 0] row_cord = ROW_CORD;

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
        if (col_addr == col_cord) begin
          // X movement Finished, start ELEVATION or DEELEVATION
          if (row_addr == row_cord) begin
          // Y movement Finished, route to Resource
            mux_out_sel_w = RESOURCE;
          end
          else if (row_addr < row_cord) begin
            mux_out_sel_w = UP;
          end
          else begin
            mux_out_sel_w = DOWN;
          end
        end
        else begin
          if (col_addr > col_cord) begin
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

    `ifdef LOG_DEBUG
      initial begin
        $display("SW_CONF %d", SW_CONFIG);
        $display("OUTPUT_N_W %d", OUTPUT_N_W);
        $display("LEFT    %d", LEFT);
        $display("UP      %d", UP);
        $display("RIGHT   %d", RIGHT);
        $display("DOWN    %d", DOWN);
      end
    `endif

    `ifdef FORMAL
      always @(*) begin
        if (PORT_N == 3 || PORT_N == 4 || PORT_N == 5 )
          assert (mux_out_sel_o < PORT_N);
      end
    `endif
endmodule
