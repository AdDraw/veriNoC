/*
  Adam Drawc 7.03.2021@PW

  Network on Chip
  - 2D mesh topology
  - Dimension Order Routing
  - Packet-Based Store& forward Flow control
  - static priority arbitration for competing packets
  - Each packet contains of a single unit of data that contains (Xaddr, Yaddr, Data)

  LT switch = (0,0)
  RB switch = (N-1, M-1)

*/
`timescale 1ns / 1ps

`define PACKET_W (PCKT_DATA_W + $clog2(ROW_N) + $clog2(COL_M))
`define RSC_PCKT_RANGE (`PACKET_W * ROW_N * COL_M) - 1 : 0
`define CALC_PCKT_RANGE(ROW_IDX, COL_IDX) (((ROW_IDX*COL_M) + COL_IDX + 1) * `PACKET_W) - 1 : (((ROW_IDX*COL_M) + COL_IDX) * `PACKET_W)

`define NUM_OF_EDGES (2*(ROW_N*COL_M) - (ROW_N + COL_M)) //assuming that each Switch can have up to 4 neighbouring switches in a mesh noc

`define LEFT  1
`define UP    2
`define RIGHT 3
`define DOWN  4

module mesh_xy_noc
  # (
      `ifdef YS_MESH_XY_TOP
      parameter ROW_N         = `YS_ROW_N,
      parameter COL_M         = `YS_COL_M,
      parameter PCKT_DATA_W   = `YS_PCKT_DATA_W,
      parameter FIFO_DEPTH_W  = `YS_FIFO_DEPTH_W
      `else
      parameter ROW_N         = 3,
      parameter COL_M         = 3,
      parameter PCKT_DATA_W   = 8,
      parameter FIFO_DEPTH_W  = 3
      `endif
      )
    (
      input clk_i,
      input rst_ni,

      // RESOURCE INPUT CHANNEL
      input  [`RSC_PCKT_RANGE]          rsc_pckt_i,
      input  [(ROW_N * COL_M) -1 : 0]   rsc_wren_i,
      output [(ROW_N * COL_M) -1 : 0]   noc_full_o,
      output [(ROW_N * COL_M) -1 : 0]   noc_ovrflw_o,

      // RESOURCE OUTPUT CHANNEL
      output [`RSC_PCKT_RANGE]          noc_pckt_o,
      output [(ROW_N * COL_M) -1 : 0]   noc_wren_o,
      input  [(ROW_N * COL_M) -1 : 0]   rsc_full_i,
      input  [(ROW_N * COL_M) -1 : 0]   rsc_ovrflw_i
      );

    function [3:0] sw_config;
      input [$clog2(ROW_N)-1:0] row_idx;
      input [$clog2(COL_M)-1:0] col_idx;
      begin
        if (row_idx == 0 && col_idx == 0)                                               sw_config = `EDGE_LT;
        else if (row_idx == 0 && col_idx == (COL_M - 1))                                sw_config = `EDGE_LB;
        else if (row_idx == (ROW_N - 1) && col_idx == (COL_M - 1))                      sw_config = `EDGE_RB;
        else if (row_idx == 0 && col_idx == (COL_M - 1))                                sw_config = `EDGE_RT;
        else if (((row_idx > 0) && (row_idx < (ROW_N - 1))) && col_idx == 0)            sw_config = `SIDE_L;
        else if (((row_idx > 0) && (row_idx < (ROW_N - 1))) && col_idx == (COL_M-1))    sw_config = `SIDE_R;
        else if (row_idx == 0 && ((col_idx > 0) && (col_idx < (COL_M - 1))))            sw_config = `SIDE_T;
        else if (row_idx == (ROW_N - 1) && ((col_idx > 0) && (col_idx < (COL_M - 1))))  sw_config = `SIDE_B;
        else                                                                            sw_config = `CENTER;
      end
    endfunction

    function [2 : 0] port_n;
      input [3 : 0] sw_config;
      begin
        case (sw_config)
          `EDGE_LB | `EDGE_LT | `EDGE_RT | `EDGE_RB: port_n = 3;
          `SIDE_L | `SIDE_R | `SIDE_T | `SIDE_B:     port_n = 4;
          `CENTER:                                   port_n = 5;
          default:                                   port_n = 5;
        endcase
      end
    endfunction

    // GENERATE NOC
    genvar row_idx; // row idx
    genvar col_idx; // column idx
    genvar port_idx;

    generate
      wire [`PACKET_W-1 : 0]  sw_pckt_w   [ROW_N-1:0][COL_M-1:0][3:0];
      wire                    sw_wren_w   [ROW_N-1:0][COL_M-1:0][3:0];
      wire                    sw_full_w   [ROW_N-1:0][COL_M-1:0][3:0];
      wire                    sw_ovrflw_w [ROW_N-1:0][COL_M-1:0][3:0];

      // Iteration through ROWs
      for (row_idx = 0; row_idx < ROW_N; row_idx = row_idx + 1)
      begin : genrow
        // Iteration through COLUMNs
        for (col_idx = 0; col_idx < COL_M; col_idx = col_idx + 1)
        begin : gencol

          // inputs
          wire [(`PACKET_W*port_n(`CENTER))-1 : 0]  x_sw_pckt_i; // 5 inputs
          wire [(`PACKET_W*port_n(`CENTER))-1 : 0]  x_sw_pckt_o; // 5 outputs
          wire [port_n(`CENTER)-1 : 0]              x_sw_wren_i;
          wire [port_n(`CENTER)-1 : 0]              x_sw_wren_o;
          wire [port_n(`CENTER)-1 : 0]              x_sw_full_i;
          wire [port_n(`CENTER)-1 : 0]              x_sw_full_o;
          wire [port_n(`CENTER)-1 : 0]              x_sw_ovrflw_i;
          wire [port_n(`CENTER)-1 : 0]              x_sw_ovrflw_o;

          // inputs
          assign x_sw_wren_i[0]         = rsc_wren_i[row_idx * COL_M + col_idx];
          assign x_sw_wren_i[`LEFT]     = (col_idx > 0)           ? sw_wren_w[row_idx][col_idx-1][`RIGHT-1]: 0;
          assign x_sw_wren_i[`UP]       = (row_idx > 0)           ? sw_wren_w[row_idx-1][col_idx][`DOWN-1] : 0;
          assign x_sw_wren_i[`RIGHT]    = (col_idx < (COL_M - 1)) ? sw_wren_w[row_idx][col_idx+1][`LEFT-1] : 0;
          assign x_sw_wren_i[`DOWN]     = (row_idx < (ROW_N - 1)) ? sw_wren_w[row_idx+1][col_idx][`UP-1]   : 0;

          assign x_sw_full_i[0]         = rsc_full_i[row_idx*COL_M + col_idx];
          assign x_sw_full_i[`LEFT]     = (col_idx > 0)           ? sw_full_w[row_idx][col_idx-1][`RIGHT-1]: 0;
          assign x_sw_full_i[`UP]       = (row_idx > 0)           ? sw_full_w[row_idx-1][col_idx][`DOWN-1] : 0;
          assign x_sw_full_i[`RIGHT]    = (col_idx < (COL_M - 1)) ? sw_full_w[row_idx][col_idx+1][`LEFT-1] : 0;
          assign x_sw_full_i[`DOWN]     = (row_idx < (ROW_N - 1)) ? sw_full_w[row_idx+1][col_idx][`UP-1]   : 0;

          assign x_sw_ovrflw_i[0]       = rsc_ovrflw_i[row_idx*COL_M + col_idx];
          assign x_sw_ovrflw_i[`LEFT]   = (col_idx > 0)           ? sw_ovrflw_w[row_idx][col_idx-1][`RIGHT-1]: 0;
          assign x_sw_ovrflw_i[`UP]     = (row_idx > 0)           ? sw_ovrflw_w[row_idx-1][col_idx][`DOWN-1] : 0;
          assign x_sw_ovrflw_i[`RIGHT]  = (col_idx < (COL_M - 1)) ? sw_ovrflw_w[row_idx][col_idx+1][`LEFT-1] : 0;
          assign x_sw_ovrflw_i[`DOWN]   = (row_idx < (ROW_N - 1)) ? sw_ovrflw_w[row_idx+1][col_idx][`UP-1]   : 0;

          assign x_sw_pckt_i[`PACKET_W-1 : 0] = rsc_pckt_i[`CALC_PCKT_RANGE(row_idx, col_idx)];
          assign x_sw_pckt_i[(`PACKET_W*(`LEFT+1))-1  : `PACKET_W*`LEFT]  = (col_idx > 0)           ? sw_pckt_w[row_idx][col_idx-1][`RIGHT-1]: 0;
          assign x_sw_pckt_i[(`PACKET_W*(`UP+1))-1    : `PACKET_W*`UP]    = (row_idx > 0)           ? sw_pckt_w[row_idx-1][col_idx][`DOWN-1] : 0;
          assign x_sw_pckt_i[(`PACKET_W*(`RIGHT+1))-1 : `PACKET_W*`RIGHT] = (col_idx < (COL_M - 1)) ? sw_pckt_w[row_idx][col_idx+1][`LEFT-1] : 0;
          assign x_sw_pckt_i[(`PACKET_W*(`DOWN+1))-1  : `PACKET_W*`DOWN]  = (row_idx < (ROW_N - 1)) ? sw_pckt_w[row_idx+1][col_idx][`UP-1]   : 0;

          xy_switch
          #(
            .COL_CORD(col_idx),
            .ROW_CORD(row_idx),
            .PORT_N(port_n(`CENTER)),
            .IN_FIFO_DEPTH_W(FIFO_DEPTH_W),
            .PCKT_COL_ADDR_W($clog2(COL_M)),
            .PCKT_ROW_ADDR_W($clog2(ROW_N)),
            .PCKT_DATA_W(PCKT_DATA_W),
            .PCKT_W(`PACKET_W)
            )
          x_sw
          (
            .clk_i(clk_i),
            .rst_ni(rst_ni),
            .wr_en_sw_i(x_sw_wren_i),
            .pckt_sw_i(x_sw_pckt_i),
            .in_fifo_full_o(x_sw_full_o),
            .in_fifo_overflow_o(x_sw_ovrflw_o),
            .nxt_fifo_full_i(x_sw_full_i),
            .nxt_fifo_overflow_i(x_sw_ovrflw_i),
            .wr_en_sw_o(x_sw_wren_o),
            .pckt_sw_o(x_sw_pckt_o)
            );

          //outputs
          assign noc_wren_o   [row_idx*COL_M + col_idx]             = x_sw_wren_o[0];
          assign noc_full_o   [row_idx*COL_M + col_idx]             = x_sw_full_o[0];
          assign noc_ovrflw_o [row_idx*COL_M + col_idx]             = x_sw_ovrflw_o[0];
          assign noc_pckt_o   [`CALC_PCKT_RANGE(row_idx, col_idx)]  = x_sw_pckt_o[`PACKET_W-1 : 0];

          for (port_idx = 1; port_idx < port_n(`CENTER); port_idx = port_idx + 1)
          begin
            assign sw_wren_w  [row_idx][col_idx][port_idx-1] = x_sw_wren_o    [port_idx];
            assign sw_full_w  [row_idx][col_idx][port_idx-1] = x_sw_full_o    [port_idx];
            assign sw_ovrflw_w[row_idx][col_idx][port_idx-1] = x_sw_ovrflw_o  [port_idx];
            assign sw_pckt_w  [row_idx][col_idx][port_idx-1] = x_sw_pckt_o    [(`PACKET_W*(port_idx+1))-1 : `PACKET_W*port_idx];
          end

        end
      end
    endgenerate
endmodule // mesh_xy_noc
