/*
  Adam Drawc 4.09.2021@PW

  Network on Chip
  - 2D mesh topology
  - Dimension Order Routing
  - Flit-Based Wormhole Flow control
  - matrix arbitration for competing packets
  - Each packet is split between N flits, Header, Body and Tail (2bit)
  - symmetric edge number on each node (constant radix of 5)

  LT switch = (0,0)
  RB switch = (N-1, M-1)

*/
`timescale 1ns / 1ps

`define RSC_RANGE (CHANNEL_W * ROW_N * COL_M) - 1 : 0
`define CALC_CHAN_RANGE(rid, cid) (((rid*COL_M)+cid+1)*CHANNEL_W)-1 : ((rid*COL_M)+cid)*CHANNEL_W
`define CHAN_RANGE(id) id*CHANNEL_W+:CHANNEL_W

`define TERM 0
`define LEFT 1
`define UP 2
`define RIGHT 3
`define DOWN 4

module mesh_wormhole_xy_noc #(
  parameter ROW_N               = 3,
  parameter COL_M               = 3,
  parameter NODE_RADIX          = 5,  // CONSTANT
  parameter CHANNEL_W           = 8,
  parameter FLIT_ID_W           = 2,  // HEAD, BODY, TAIL, NULL(not defined), CONSTANT
  parameter NODE_BUFFER_DEPTH_W = 4,
  parameter ARB_TYPE            = 0
) (
  // GLOBAL
  input                           clk_i,
  input                           rst_ni,
  // NETWORK INPUT CHANNELs
  input  [            `RSC_RANGE] ich_data_i,
  input  [(ROW_N * COL_M) -1 : 0] ich_vld_i,
  output [(ROW_N * COL_M) -1 : 0] ich_rdy_o,

  // NETWORK OUTPUT CHANNELs
  output [            `RSC_RANGE] och_data_o,
  output [(ROW_N * COL_M) -1 : 0] och_vld_o,
  input  [(ROW_N * COL_M) -1 : 0] och_rdy_i
);

  // GENERATE NOC
  genvar row_idx;  // row idx
  genvar col_idx;  // column idx
  genvar port_idx;

  generate
    wire [CHANNEL_W-1 : 0] ch_data_w[ROW_N][COL_M][NODE_RADIX-1];
    wire                   ch_vld_w [ROW_N][COL_M][NODE_RADIX-1];
    wire                   ch_rdy_w [ROW_N][COL_M][NODE_RADIX-1];

    // Iteration through ROWs
    for (row_idx = 0; row_idx < ROW_N; row_idx = row_idx + 1) begin : genrow
      // Iteration through COLUMNs
      for (col_idx = 0; col_idx < COL_M; col_idx = col_idx + 1) begin : gencol
        // inputs
        wire [(CHANNEL_W * NODE_RADIX)-1 : 0] x_ich_data_i;  // 5 inputs
        wire [            NODE_RADIX - 1 : 0] x_ich_vld_i;
        wire [            NODE_RADIX - 1 : 0] x_ich_rdy_o;
        wire [(CHANNEL_W * NODE_RADIX)-1 : 0] x_och_data_o;  // 5 outputs
        wire [            NODE_RADIX - 1 : 0] x_och_vld_o;
        wire [            NODE_RADIX - 1 : 0] x_och_rdy_i;

        // ICHAN VLD
        assign x_ich_vld_i[`TERM] = ich_vld_i[row_idx*COL_M+col_idx];
        assign x_ich_vld_i[`LEFT] = (col_idx > 0) ? ch_vld_w[row_idx][col_idx-1][`RIGHT-1] : 0;
        assign x_ich_vld_i[`UP] = (row_idx > 0) ? ch_vld_w[row_idx-1][col_idx][`DOWN-1] : 0;
        assign x_ich_vld_i[`RIGHT] = (col_idx < (COL_M - 1)) ? ch_vld_w[row_idx][col_idx+1][`LEFT-1] : 0;
        assign x_ich_vld_i[`DOWN] = (row_idx < (ROW_N - 1)) ? ch_vld_w[row_idx+1][col_idx][`UP-1] : 0;

        // ICHAN DATA
        assign x_ich_data_i[`CHAN_RANGE(`TERM)] = ich_data_i[`CALC_CHAN_RANGE(row_idx, col_idx)];
        assign x_ich_data_i[`CHAN_RANGE(`LEFT)] = (col_idx > 0) ? ch_data_w[row_idx][col_idx-1][`RIGHT-1] : 0;
        assign x_ich_data_i[`CHAN_RANGE(`UP)] = (row_idx > 0) ? ch_data_w[row_idx-1][col_idx][`DOWN-1] : 0;
        assign x_ich_data_i[`CHAN_RANGE(`RIGHT)] = (col_idx < (COL_M - 1)) ? ch_data_w[row_idx][col_idx+1][`LEFT-1] : 0;
        assign x_ich_data_i[`CHAN_RANGE(`DOWN)] = (row_idx < (ROW_N - 1)) ? ch_data_w[row_idx+1][col_idx][`UP-1] : 0;

        // OCHAN RDY_I
        assign x_och_rdy_i[`TERM] = och_rdy_i[row_idx*COL_M+col_idx];
        assign x_och_rdy_i[`LEFT] = (col_idx > 0) ? ch_rdy_w[row_idx][col_idx-1][`RIGHT-1] : 0;
        assign x_och_rdy_i[`UP] = (row_idx > 0) ? ch_rdy_w[row_idx-1][col_idx][`DOWN-1] : 0;
        assign x_och_rdy_i[`RIGHT] = (col_idx < (COL_M - 1)) ? ch_rdy_w[row_idx][col_idx+1][`LEFT-1] : 0;
        assign x_och_rdy_i[`DOWN] = (row_idx < (ROW_N - 1)) ? ch_rdy_w[row_idx+1][col_idx][`UP-1] : 0;

        mesh_wormhole_node #(
          .IN_N          (NODE_RADIX),
          .OUT_M         (NODE_RADIX),
          .FLIT_DATA_W   (CHANNEL_W - FLIT_ID_W),
          .FLIT_ID_W     (FLIT_ID_W),
          .ROW_ADDR_W    ($clog2(ROW_N)),
          .COL_ADDR_W    ($clog2(COL_M)),
          .ROW_CORD      (row_idx),
          .COL_CORD      (col_idx),
          .BUFFER_DEPTH_W(NODE_BUFFER_DEPTH_W),
          .ARB_TYPE      (ARB_TYPE)
        ) x_node (
          .clk_i          (clk_i),
          .rst_ni         (rst_ni),
          .in_chan_data_i (x_ich_data_i),
          .in_chan_vld_i  (x_ich_vld_i),
          .in_chan_rdy_o  (x_ich_rdy_o),
          .out_chan_data_o(x_och_data_o),
          .out_chan_vld_o (x_och_vld_o),
          .out_chan_rdy_i (x_och_rdy_i)
        );

        //outputs
        for (port_idx = 0; port_idx < NODE_RADIX; port_idx = port_idx + 1) begin
          if (port_idx == 0) begin
            assign och_vld_o[row_idx*COL_M+col_idx]               = x_och_vld_o[0];
            assign ich_rdy_o[row_idx*COL_M+col_idx]               = x_ich_rdy_o[0];
            assign och_data_o[`CALC_CHAN_RANGE(row_idx, col_idx)] = x_och_data_o[CHANNEL_W-1 : 0];
          end else begin
            assign ch_vld_w[row_idx][col_idx][port_idx-1]  = x_och_vld_o[port_idx];
            assign ch_rdy_w[row_idx][col_idx][port_idx-1]  = x_ich_rdy_o[port_idx];
            assign ch_data_w[row_idx][col_idx][port_idx-1] = x_och_data_o[`CHAN_RANGE(port_idx)];
          end
        end
      end
    end
  endgenerate
endmodule  // mesh_xy_noc
