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
`define CALC_CHANNEL_RANGE(rid, cid) (((rid*COL_M)+cid+1)*CHANNEL_W)-1 : ((rid*COL_M)+cid)*CHANNEL_W
`define CHANNEL_RANGE(id) `UNPACK(id, CHANNEL_W)

`define TERM  0
`define LEFT  1
`define UP    2
`define RIGHT 3
`define DOWN  4

module mesh_wormhole_xy_noc#(
  `ifdef YS_MESH_WH_XY_TOP
    parameter ROW_N               = `YS_ROW_N,
    parameter COL_M               = `YS_COL_M,
    parameter NODE_RADIX          = `YS_NODE_RADIX, // CONSTANT
    parameter CHANNEL_W           = `YS_CHANNEL_W,
    parameter FLIT_ID_W           = `YS_FLIT_ID_W,
    parameter NODE_BUFFER_DEPTH_W = `YS_NODE_BUFFER_DEPTH_W
  `else
    parameter ROW_N               = 3,
    parameter COL_M               = 3,
    parameter NODE_RADIX          = 5, // CONSTANT
    parameter CHANNEL_W           = 8,
    parameter FLIT_ID_W           = 2, // HEAD, BODY, TAIL, NULL(not defined), CONSTANT
    parameter NODE_BUFFER_DEPTH_W = 4
  `endif
  ) (
    // GLOBAL
    input                           clk_i,
    input                           rst_ni,
    // NETWORK INPUT CHANNELs
    input  [`RSC_RANGE]             ichan_data_i,
    input  [(ROW_N * COL_M) -1 : 0] ichan_vld_i,
    output [(ROW_N * COL_M) -1 : 0] ichan_rdy_o,

    // NETWORK OUTPUT CHANNELs
    output [`RSC_RANGE]             ochan_data_o,
    output [(ROW_N * COL_M) -1 : 0] ochan_vld_o,
    input  [(ROW_N * COL_M) -1 : 0] ochan_rdy_i
  );

  // GENERATE NOC
  genvar row_idx; // row idx
  genvar col_idx; // column idx
  genvar port_idx;

  generate
    wire [CHANNEL_W-1 : 0]  chan_data_w  [ROW_N-1:0][COL_M-1:0][NODE_RADIX-2:0];
    wire                    chan_vld_w   [ROW_N-1:0][COL_M-1:0][NODE_RADIX-2:0];
    wire                    chan_rdy_w   [ROW_N-1:0][COL_M-1:0][NODE_RADIX-2:0];

    // Iteration through ROWs
    for (row_idx = 0; row_idx < ROW_N; row_idx = row_idx + 1)
    begin : genrow
      // Iteration through COLUMNs
      for (col_idx = 0; col_idx < COL_M; col_idx = col_idx + 1)
      begin : gencol
        // inputs
        wire [(CHANNEL_W * NODE_RADIX)-1 : 0] x_ichan_data_i; // 5 inputs
        wire [NODE_RADIX - 1 : 0]             x_ichan_vld_i;
        wire [NODE_RADIX - 1 : 0]             x_ichan_rdy_o;
        wire [(CHANNEL_W * NODE_RADIX)-1 : 0] x_ochan_data_o; // 5 outputs
        wire [NODE_RADIX - 1 : 0]             x_ochan_vld_o;
        wire [NODE_RADIX - 1 : 0]             x_ochan_rdy_i;

        // ICHAN VLD
        assign x_ichan_vld_i[`TERM]  =                           ichan_vld_i[row_idx * COL_M + col_idx];
        assign x_ichan_vld_i[`LEFT]  = (col_idx > 0)           ? chan_vld_w[row_idx][col_idx-1][`RIGHT-1]: 0;
        assign x_ichan_vld_i[`UP]    = (row_idx > 0)           ? chan_vld_w[row_idx-1][col_idx][`DOWN-1] : 0;
        assign x_ichan_vld_i[`RIGHT] = (col_idx < (COL_M - 1)) ? chan_vld_w[row_idx][col_idx+1][`LEFT-1] : 0;
        assign x_ichan_vld_i[`DOWN]  = (row_idx < (ROW_N - 1)) ? chan_vld_w[row_idx+1][col_idx][`UP-1]   : 0;

        // ICHAN DATA
        assign x_ichan_data_i[`CHANNEL_RANGE(`TERM)]  =                           ichan_data_i[`CALC_CHANNEL_RANGE(row_idx, col_idx)];
        assign x_ichan_data_i[`CHANNEL_RANGE(`LEFT)]  = (col_idx > 0)           ? chan_data_w[row_idx][col_idx-1][`RIGHT-1]: 0;
        assign x_ichan_data_i[`CHANNEL_RANGE(`UP)]    = (row_idx > 0)           ? chan_data_w[row_idx-1][col_idx][`DOWN-1] : 0;
        assign x_ichan_data_i[`CHANNEL_RANGE(`RIGHT)] = (col_idx < (COL_M - 1)) ? chan_data_w[row_idx][col_idx+1][`LEFT-1] : 0;
        assign x_ichan_data_i[`CHANNEL_RANGE(`DOWN)]  = (row_idx < (ROW_N - 1)) ? chan_data_w[row_idx+1][col_idx][`UP-1]   : 0;

        // OCHAN RDY_I
        assign x_ochan_rdy_i[`TERM]  =                           ochan_rdy_i[row_idx*COL_M + col_idx];
        assign x_ochan_rdy_i[`LEFT]  = (col_idx > 0)           ? chan_rdy_w[row_idx][col_idx-1][`RIGHT-1]: 0;
        assign x_ochan_rdy_i[`UP]    = (row_idx > 0)           ? chan_rdy_w[row_idx-1][col_idx][`DOWN-1] : 0;
        assign x_ochan_rdy_i[`RIGHT] = (col_idx < (COL_M - 1)) ? chan_rdy_w[row_idx][col_idx+1][`LEFT-1] : 0;
        assign x_ochan_rdy_i[`DOWN]  = (row_idx < (ROW_N - 1)) ? chan_rdy_w[row_idx+1][col_idx][`UP-1]   : 0;

        mesh_wormhole_node #(
          .IN_N           (NODE_RADIX),
          .OUT_M          (NODE_RADIX),
          .FLIT_DATA_W    (CHANNEL_W - FLIT_ID_W),
          .FLIT_ID_W      (FLIT_ID_W),
          .ROW_ADDR_W     ($clog2(ROW_N)),
          .COL_ADDR_W     ($clog2(COL_M)),
          .ROW_CORD       (row_idx),
          .COL_CORD       (col_idx),
          .BUFFER_DEPTH_W (NODE_BUFFER_DEPTH_W)
          )
        x_node (
          .clk_i            (clk_i),
          .rst_ni           (rst_ni),
          .in_chan_data_i   (x_ichan_data_i),
          .in_chan_vld_i    (x_ichan_vld_i),
          .in_chan_rdy_o    (x_ichan_rdy_o),
          .out_chan_data_o  (x_ochan_data_o),
          .out_chan_vld_o   (x_ochan_vld_o),
          .out_chan_rdy_i   (x_ochan_rdy_i)
        );

        //outputs
        for (port_idx = 0; port_idx < NODE_RADIX; port_idx = port_idx + 1)
        begin
          if (port_idx == 0) begin
            assign ochan_vld_o  [row_idx*COL_M + col_idx]            = x_ochan_vld_o[0];
            assign ichan_rdy_o  [row_idx*COL_M + col_idx]            = x_ichan_rdy_o[0];
            assign ochan_data_o [`CALC_CHANNEL_RANGE(row_idx, col_idx)] = x_ochan_data_o[CHANNEL_W - 1 : 0];
          end
          else begin
            assign chan_vld_w  [row_idx][col_idx][port_idx-1] = x_ochan_vld_o[port_idx];
            assign chan_rdy_w  [row_idx][col_idx][port_idx-1] = x_ichan_rdy_o[port_idx];
            assign chan_data_w [row_idx][col_idx][port_idx-1] = x_ochan_data_o[`CHANNEL_RANGE(port_idx)];
          end
        end
      end
    end
  endgenerate
endmodule // mesh_xy_noc
