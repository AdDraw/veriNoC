/*
  Author: Adam Drawc
  Module Name: Switch using XY algorithm for packet routing in a MESH NoC

  Description:
   - NoC Structure: MESH
   - Sides: 2, 3, 4 (Depends on the placement of the switch in the mesh) -- not done yet
   - Resource and SW clocked with the same speed(for now) -- done
   - 1->1, no broadcasting (1->N) -- done

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
  1. Hop count - in the packet there will be bits for this priority indicator -- not used
  2. We can have a stack with priority -- not used
     - When a packet is available it's ID is put on the stack
  3. MerryGoRound - you take from 1 input and then look at the input to the right(if the data is available)
  4. Set priority
     - first Vertical then Horizontal packet movement


   PACKET :
   |  ROW_addr    | [`PCKT_DATA_W + `PCKT_ROW_ADDR_W + `PCKT_COL_ADDR_W - 1 : `PCKT_DATA_W + `PCKT_ROW_ADDR_W ]
   |  COLUMN_addr | [`PCKT_DATA_W + `PCKT_YADDR_W - 1 : `PCKT_DATA_W ]
   |  DATA        | [`PCKT_DATA_W - 1 : 0 ]

*/
`timescale 1ns / 1ps
module xy_switch
# (
    `ifdef YS_XY_SW_TOP // only For YOSYS parameter setting (it's not possible to override parameters for singular modules)
      parameter COL_CORD        = `YS_COL_CORD,
      parameter ROW_CORD        = `YS_ROW_CORD,
      parameter PORT_N          = `YS_PORT_N, // 1 is minimum because of connection to RESOURCE,
      parameter IN_FIFO_DEPTH_W = `YS_IN_FIFO_DEPTH_W,
      parameter PCKT_COL_ADDR_W = `YS_PCKT_COL_ADDR_W,
      parameter PCKT_ROW_ADDR_W = `YS_PCKT_ROW_ADDR_W,
      parameter PCKT_DATA_W     = `YS_PCKT_DATA_W,
    `else
      parameter COL_CORD = 0,
      parameter ROW_CORD = 0,
      parameter PORT_N = 5, // 1 is minimum because of connection to RESOURCE,
      parameter IN_FIFO_DEPTH_W = 3,
      parameter PCKT_COL_ADDR_W = 4,
      parameter PCKT_ROW_ADDR_W = 4,
      parameter PCKT_DATA_W = 8,
    `endif
    parameter PCKT_W = PCKT_COL_ADDR_W + PCKT_ROW_ADDR_W + PCKT_DATA_W
    )
  (

    // GLOBAL
    input clk_i,
    input rst_ni,

    // SWITCH INPUT BUFFER ports
    input   [PORT_N - 1 : 0]            wr_en_sw_i,
    input   [PCKT_W * PORT_N - 1 : 0]   pckt_sw_i,
    output  [PORT_N - 1 : 0]            in_fifo_full_o,
    output  [PORT_N - 1 : 0]            in_fifo_overflow_o,

    // SWITCH OUTPUT BUFFER ports
    input   [PORT_N - 1 : 0]            nxt_fifo_full_i,
    input   [PORT_N - 1 : 0]            nxt_fifo_overflow_i,
    output  [PORT_N - 1 : 0]            wr_en_sw_o,
    output  [PCKT_W * PORT_N - 1 : 0]   pckt_sw_o
    );

    // Wires
    wire [PORT_N -1 : 0]            vld_input_w;
    wire [$clog2(PORT_N) - 1 : 0]   mux_in_sel_w;
    wire [$clog2(PORT_N) - 1 : 0]   mux_out_sel_w;
    wire [PCKT_W * PORT_N - 1 : 0]  data_out_w;
    wire [PCKT_W - 1 : 0]           pckt_in_chosen_w;

    // Wires assignments
    wire [PCKT_ROW_ADDR_W - 1 : 0] row_addr_w = pckt_in_chosen_w[ PCKT_W - 1 : PCKT_DATA_W + PCKT_COL_ADDR_W ];
    wire [PCKT_COL_ADDR_W - 1 : 0] col_addr_w = pckt_in_chosen_w[ PCKT_W - PCKT_ROW_ADDR_W - 1 : PCKT_DATA_W ];

    // Module Instantatiation
    // Input BUFFERS
    genvar i;
    generate
      // INTERNAL Signals
      wire [PCKT_W * PORT_N - 1 : 0]  fifo_data_out_w;
      wire [PORT_N - 1 : 0]           rd_en_w;
      wire [PORT_N - 1 : 0]           empty_w;
      wire [PORT_N - 1 : 0]           underflow_w;

      for (i=0; i < PORT_N; i = i + 1)
      begin : genfifo
        wire [PCKT_W -1 : 0] x_pckt_in_w = pckt_sw_i[PCKT_W * ( i + 1 ) - 1 : PCKT_W * i];
        wire [PCKT_W -1 : 0] x_pckt_out_w;

        circ_fifo
          #(
            .DATA_W(PCKT_W),
            .FIFO_DEPTH_W(IN_FIFO_DEPTH_W),
            .ID(i)
            )
        x_input_fifo
          (
            .clk_i( clk_i ),
            .rst_ni( rst_ni ),
            .wr_en_i( wr_en_sw_i[i] ),            //comes from the outside if this fifo is not full
            .rd_en_i( rd_en_w[i] ),               // comes fro mthe indside when we want to route the packet inside this FIFO
            .data_i( x_pckt_in_w ),               // data to go into FIFO
            .data_o( x_pckt_out_w ),              //data to go out of FIFO
            .full_o( in_fifo_full_o[i] ),         //if this fifo is full, pass it on to the Switch connected to you
            .empty_o( empty_w[i] ),               // empty is used internally and indicates data to be routed
            .overflow_o( in_fifo_overflow_o[i] ), // might be nice
            .underflow_o( underflow_w[i] )        // might be nice to have
            );

        assign fifo_data_out_w [PCKT_W * ( i + 1 ) - 1 : PCKT_W * i]  = x_pckt_out_w;
      end
    endgenerate

    // ARBITER - chooses input port
    static_priority_arbiter
    # (
        .IN_N(PORT_N)
        )
    arb
      (
        .vld_input_i(vld_input_w),
        .arb_res_o(mux_in_sel_w)
        );

    // ROUTER - chooses output port
    xy_router
    # (
        .COL_CORD(COL_CORD),
        .ROW_CORD(ROW_CORD),
        .PACKET_ADDR_COL_W(PCKT_COL_ADDR_W),
        .PACKET_ADDR_ROW_W(PCKT_ROW_ADDR_W),
        .OUTPUT_N_W($clog2(PORT_N))
        )
    router
      (
        .col_addr_i(col_addr_w),
        .row_addr_i(row_addr_w),
        .out_chan_sel_o(mux_out_sel_w)
        );

    // CONTROL UNIT
    control_unit
    # (
        .PORT_N(PORT_N)
        )
    control_u
      (
        .clk_i(clk_i),
        .rst_ni(rst_ni),
        .full_i(nxt_fifo_full_i), // do we have FIFOs that will be full? IF yes this channel is blocked and we cant route the data to it
        .empty_i(empty_w), // look at the input FIFOs and check if any has data to be routed
        .mux_in_sel_i(mux_in_sel_w), // if there is data, pass the correct MUXINSEL value to the input MUX of the crossbar
        .mux_out_sel_i(mux_out_sel_w),
        .rd_en_o(rd_en_w),
        .wr_en_o(wr_en_sw_o),
        .vld_input_o(vld_input_w)
        );

    // CROSSBAR
    nxn_single_crossbar
    # (
        .DATA_W(PCKT_W),
        .PORT_N(PORT_N)
        )
    crossbar
      (
        .data_i(fifo_data_out_w),
        .in_sel_i(mux_in_sel_w),
        .out_sel_i(mux_out_sel_w),
        .data_o(data_out_w),
        .pckt_in_chosen_o(pckt_in_chosen_w)
        );

    assign pckt_sw_o = (|vld_input_w) ? data_out_w : 0;

endmodule
