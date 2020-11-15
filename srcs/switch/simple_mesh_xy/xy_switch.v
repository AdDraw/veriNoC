/*
  Author: Adam Drawc
  Module Name: Switch using XY algorithm for packet routing in a MESH NoC

  Description:
   - NoC Structure: MESH
   - Sides: 2, 3, 4 (Depends on the placement of the switch in the mesh)
   - Resource and SW clocked with the same speed(for now)
   - 1->1, no broadcasting (1->N)

  Should be able to route packets from 1 input to 1 of the outputs.
  Using a simple XY algorithm based on the address.

  Q: How do 2 switches know their address and the addresses that is arround them?
  A: Well the switch knows it's address, the address always has to be greater than 0
     Switch knows that a switch to the next has either + 1/-1 in it's X and Y coordinates
     Through this it knows onto which output should it place the data

  Packets:
  1. Atomic - packet can be managed by a switch in a single cycle
  2. Have an XY address and the data

  Priorities:
  1. Hop count - in the packet there will be bits for this priority indicator
  2. We can have a stack with priority
     - When a packet is available it's ID is put on the stack
  3. MerryGoRound - you take from 1 input and then look at the input to the right(if the data is available)
*/

`include "crossbar.v"
`include "router_xy.v"
`include "control_unit.v"
`include "../../components/fifo.v"
`include "packet_arbiter.v"


`define PACKET_ADDR_X_W 4
`define PACKET_ADDR_Y_W 4
`define PACKET_DATA_W 8
`define PACKET_HOP_CNT_W 4
`define PACKET_W (`PACKET_ADDR_X_W + `PACKET_ADDR_Y_W + `PACKET_DATA_W)

`define INPUT_FIFO_DEPTH_WIDTH 3

/*
  PACKET
  |  X_Addr  |  Y_addr  |   DATA   |
*/

module xy_switch
# (
    parameter X_CORD = 0,
    parameter Y_CORD = 0,
    parameter NEIGHBOURS_N = 5 // 1 is minimum cause RESOURCE
    )
  (
    // GLOBAL
    input clk_i,
    input rst_ni,

    // SWITCH INPUTS
    input   [NEIGHBOURS_N - 1 : 0] wr_en_sw_i,
    input   [`PACKET_W * NEIGHBOURS_N - 1 : 0] pckt_sw_i,
    output  [NEIGHBOURS_N - 1 : 0] in_fifo_full_o,
    output  [NEIGHBOURS_N - 1 : 0] in_fifo_overflow_o,

    // SWITCH OUTPUTS
    input   [NEIGHBOURS_N - 1 : 0] nxt_fifo_full_i,
    input   [NEIGHBOURS_N - 1 : 0] nxt_fifo_overflow_i,
    output  [NEIGHBOURS_N - 1 : 0] wr_en_sw_o,
    output  [`PACKET_W * NEIGHBOURS_N - 1 : 0] pckt_sw_o
    );

    // Wires
    wire [$clog2(NEIGHBOURS_N) - 1 : 0] mux_in_sel_w;
    wire [$clog2(NEIGHBOURS_N) - 1 : 0] mux_out_sel_w;
    wire [NEIGHBOURS_N -1 : 0]          vld_output_w;
    wire [NEIGHBOURS_N -1 : 0]          vld_input_w;
    wire [`PACKET_W * NEIGHBOURS_N - 1 : 0] data_out_w;

    // Module Instantatiation
    // Input BUFFERS
    genvar i;
    generate
      // INTERNAL Signals
      wire [`PACKET_W * NEIGHBOURS_N - 1 : 0] fifo_data_out_w;
      wire [NEIGHBOURS_N - 1 : 0] rd_en_w;
      wire [NEIGHBOURS_N - 1 : 0] empty_w;
      wire [NEIGHBOURS_N - 1 : 0] underflow_w;
      wire [`PACKET_W-1 : 0] pckt_in_chosen_w;
      wire [NEIGHBOURS_N - 1 : 0] vld_input_w;
      wire [`PACKET_ADDR_X_W - 1 : 0] x_addr_w = pckt_in_chosen_w[ `PACKET_W - 1 : `PACKET_DATA_W + `PACKET_ADDR_Y_W ];
      wire [`PACKET_ADDR_Y_W - 1 : 0] y_addr_w = pckt_in_chosen_w[ `PACKET_W - `PACKET_ADDR_X_W - 1 : `PACKET_DATA_W ];

      for (i=0; i < NEIGHBOURS_N; i = i + 1)
      begin
        wire [`PACKET_W -1 : 0] x_pckt_in_w = pckt_sw_i[(i+1)*`PACKET_W -1 : i*`PACKET_W ];
        wire [`PACKET_W -1 : 0] x_pckt_out_w  ;

        fifo
          #(
            .DATA_WIDTH(`PACKET_W),
            .FIFO_DEPTH_WIDTH(`INPUT_FIFO_DEPTH_WIDTH)
            )
          x_input_fifo (
            .clk_i( clk_i ),
            .rst_ni( rst_ni ),
            .wr_en_i( wr_en_sw_i[i] ),
            .rd_en_i( rd_en_w[i] ),
            .data_i( x_pckt_in_w ),
            .data_o( x_pckt_out_w ),
            .full_o( in_fifo_full_o[i] ),
            .empty_o( empty_w[i] ),
            .overflow_o( in_fifo_overflow_o[i] ),
            .underflow_o( underflow_w[i] )
            );

        assign fifo_data_out_w [(i+1)*`PACKET_W -1 : i*`PACKET_W]  = x_pckt_out_w;
      end
    endgenerate

    // ARBITER - chooses input port
    arbiter
    # (
        .INPUT_N(NEIGHBOURS_N)
        )
    arb (
        .vld_input_i(vld_input_w),
        .mux_in_sel_o(mux_in_sel_w)
        );

    // ROUTER - chooses output port
    xy_router
    # (
        .X_CORD(X_CORD),
        .Y_CORD(Y_CORD),
        .PACKET_ADDR_X_W(`PACKET_ADDR_X_W),
        .PACKET_ADDR_Y_W(`PACKET_ADDR_Y_W),
        .OUTPUT_N_W($clog2(NEIGHBOURS_N))
        )
    router
      (
        .x_addr(x_addr_w),
        .y_addr(y_addr_w),
        .mux_out_sel_o(mux_out_sel_w)
        );

    // CONTROL UNIT
    control_unit
    # (
        .INPUT_N(NEIGHBOURS_N)
        )
    control_u
      (
        .clk_i(clk_i),
        .rst_ni(rst_ni),
        .full_i(nxt_fifo_full_i),
        .empty_i(empty_w),
        .mux_in_sel_i(mux_in_sel_w),
        .mux_out_sel_i(mux_out_sel_w),
        .rd_en_o(rd_en_w),
        .wr_en_o(wr_en_sw_o),
        .vld_output_o(vld_output_w),
        .vld_input_o(vld_input_w)
        );

    // CROSSBAR
    n_to_n_crossbar
    # (
        .DATA_WIDTH(`PACKET_W),
        .PORT_N(NEIGHBOURS_N)
        )
    crossbar
      (
        .clk_i(clk_i),
        .rst_ni(rst_ni),
        .data_i(fifo_data_out_w),
        .mux_in_sel_i(mux_in_sel_w),
        .vld_output_i(vld_output_w),
        .mux_out_sel_i(mux_out_sel_w),
        .data_o(data_out_w),
        .pckt_in_chosen_o(pckt_in_chosen_w)
        );

    // Vars
    integer iter;
    generate
      for (i=0; i < NEIGHBOURS_N; i = i + 1) begin
        assign pckt_sw_o[(i+1)*`PACKET_W -1 : i*`PACKET_W ] = data_out_w[(i+1)*`PACKET_W -1 : i*`PACKET_W ];
      end
    endgenerate

endmodule
