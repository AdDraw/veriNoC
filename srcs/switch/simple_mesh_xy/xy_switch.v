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
   |  ROW_addr    | [`PCKT_DATA_W + `ROW_ADDR_W + `COL_ADDR_W - 1 : `PCKT_DATA_W + `ROW_ADDR_W ]
   |  COLUMN_addr | [`PCKT_DATA_W + `PCKT_YADDR_W - 1 : `PCKT_DATA_W ]
   |  DATA        | [`PCKT_DATA_W - 1 : 0 ]

*/
`timescale 1ns / 1ps
module xy_switch #(
  parameter COL_CORD     = 0,
  parameter ROW_CORD     = 0,
  parameter PORT_N       = 5,                                     // 1 is minimum because of connection to RESOURCE,
  parameter FIFO_DEPTH_W = 3,
  parameter COL_ADDR_W   = 4,
  parameter ROW_ADDR_W   = 4,
  parameter PCKT_DATA_W  = 8,
  parameter ARB_TYPE     = 0,
  parameter PCKT_W       = COL_ADDR_W + ROW_ADDR_W + PCKT_DATA_W
) (

  // GLOBAL
  input clk_i,
  input rst_ni,

  // SWITCH INPUT BUFFER ports
  input  [         PORT_N - 1 : 0] wr_en_sw_i,
  input  [PCKT_W * PORT_N - 1 : 0] pckt_sw_i,
  output [         PORT_N - 1 : 0] in_fifo_full_o,
  output [         PORT_N - 1 : 0] in_fifo_overflow_o,

  // SWITCH OUTPUT BUFFER ports
  input  [         PORT_N - 1 : 0] nxt_fifo_full_i,
  input  [         PORT_N - 1 : 0] nxt_fifo_overflow_i,
  output [         PORT_N - 1 : 0] wr_en_sw_o,
  output [PCKT_W * PORT_N - 1 : 0] pckt_sw_o
);

  // Wires
  wire [          PORT_N -1 : 0]                                                                   vld_input_w;
  wire [ $clog2(PORT_N) - 1 : 0]                                                                   mux_in_sel_w;
  wire                                                                                             mux_in_sel_vld_w;
  wire [ $clog2(PORT_N) - 1 : 0]                                                                   mux_out_sel_w;
  wire [PCKT_W * PORT_N - 1 : 0]                                                                   data_out_w;
  wire [         PCKT_W - 1 : 0]                                                                   pckt_in_chosen_w;

  // Wires assignments
  wire [     ROW_ADDR_W - 1 : 0] row_addr_w = pckt_in_chosen_w[PCKT_W-1 : PCKT_DATA_W+COL_ADDR_W];
  wire [     COL_ADDR_W - 1 : 0] col_addr_w = pckt_in_chosen_w[PCKT_W-ROW_ADDR_W-1 : PCKT_DATA_W];

  // Module Instantatiation
  // Input BUFFERS
  genvar i;
  generate
    // INTERNAL Signals
    wire [PCKT_W * PORT_N - 1 : 0] fifo_data_out_w;
    wire [         PORT_N - 1 : 0] rd_en_w;
    wire [         PORT_N - 1 : 0] empty_w;
    wire [         PORT_N - 1 : 0] underflow_w;

    for (i = 0; i < PORT_N; i = i + 1) begin : genfifo
      wire [PCKT_W -1 : 0] x_pckt_in_w = pckt_sw_i[PCKT_W*(i+1)-1 : PCKT_W*i];
      wire [PCKT_W -1 : 0]                                                     x_pckt_out_w;

      circ_fifo #(
        .DATA_W      (PCKT_W),
        .FIFO_DEPTH_W(FIFO_DEPTH_W),
        .ID          (i)
      ) x_input_fifo (
        .clk_i      (clk_i),
        .rst_ni     (rst_ni),
        // comes from the outside if this fifo is not full
        .wr_en_i    (wr_en_sw_i[i]),
        // comes from the indside when we want to route the packet inside this FIFO
        .rd_en_i    (rd_en_w[i]),
        // data to go into FIFO
        .data_i     (x_pckt_in_w),
        // data to go out of FIFO
        .data_o     (x_pckt_out_w),
        // if this fifo is full, pass it on to the Switch connected to you
        .full_o     (in_fifo_full_o[i]),
        // empty is used internally and indicates data to be routed
        .empty_o    (empty_w[i]),
        .overflow_o (in_fifo_overflow_o[i]),  // might be nice
        .underflow_o(underflow_w[i])          // might be nice to have
      );

      assign fifo_data_out_w[PCKT_W*(i+1)-1 : PCKT_W*i] = x_pckt_out_w;
    end
  endgenerate

  // ARBITER - chooses input port
  generate
    if (ARB_TYPE == 0) begin  //matrix arb
      matrix_arbiter #(
        .IN_N(PORT_N)
      ) arb (
        .clk_i      (clk_i),
        .rst_ni     (rst_ni),
        .req_i      (vld_input_w),
        .grant_o    (mux_in_sel_w),
        .grant_vld_o(mux_in_sel_vld_w)
      );
    end else if (ARB_TYPE == 1) begin
      round_robin_arbiter #(
        .IN_N(PORT_N)
      ) arb (
        .clk_i      (clk_i),
        .rst_ni     (rst_ni),
        .req_i      (vld_input_w),
        .grant_o    (mux_in_sel_w),
        .grant_vld_o(mux_in_sel_vld_w)
      );
    end else if (ARB_TYPE == 2) begin
      static_priority_arbiter #(
        .IN_N(PORT_N)
      ) arb (
        .req_i      (vld_input_w),
        .grant_o    (mux_in_sel_w),
        .grant_vld_o(mux_in_sel_vld_w)
      );
    end else begin
      initial $error("Wrong Arbitration Type, possible options 0,1,2");
    end
  endgenerate

  // ROUTER - chooses output port
  xy_router #(
    .COL_CORD  (COL_CORD),
    .ROW_CORD  (ROW_CORD),
    .COL_ADDR_W(COL_ADDR_W),
    .ROW_ADDR_W(ROW_ADDR_W),
    .OUT_N_W   ($clog2(PORT_N))
  ) router (
    .col_addr_i    (col_addr_w),
    .row_addr_i    (row_addr_w),
    .out_chan_sel_o(mux_out_sel_w)
  );

  // CONTROL UNIT
  control_unit #(
    .PORT_N(PORT_N)
  ) control_u (
    .clk_i           (clk_i),
    .rst_ni          (rst_ni),
    // do we have FIFOs that will be full? IF yes this channel is blocked and we cant route the data to it
    .full_i          (nxt_fifo_full_i),
    // look at the input FIFOs and check if any has data to be routed
    .empty_i         (empty_w),
    // if there is data, pass the correct MUXINSEL value to the input MUX of the crossbar
    .mux_in_sel_i    (mux_in_sel_w),
    .mux_in_sel_vld_i(mux_in_sel_vld_w),
    .mux_out_sel_i   (mux_out_sel_w),
    .rd_en_o         (rd_en_w),
    .wr_en_o         (wr_en_sw_o),
    .vld_input_o     (vld_input_w)
  );

  // CROSSBAR
  nxn_single_crossbar #(
    .DATA_W(PCKT_W),
    .PORT_N(PORT_N)
  ) crossbar (
    .data_i          (fifo_data_out_w),
    .in_sel_i        (mux_in_sel_w),
    .out_sel_i       (mux_out_sel_w),
    .data_o          (data_out_w),
    .pckt_in_chosen_o(pckt_in_chosen_w)
  );

  assign pckt_sw_o = (|vld_input_w) ? data_out_w : 0;

endmodule
