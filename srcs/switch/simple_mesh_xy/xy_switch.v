/*
  Author: Adam Drawc
  Module Name: Switch usng XY algorithm for packet routing in a MESH NoC

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

`define PACKET_ADDR_X_W 4
`define PACKET_ADDR_Y_W 4
`define PACKET_DATA_W 8
`define PACKET_HOP_CNT_W 4
`define PACKET_W (`PACKET_ADDR_X_W + `PACKET_ADDR_Y_W + `PACKET_DATA_W)

`define LEFT 0
`define TOP 1
`define RIGHT 2
`define BOT 3

/*
  PACKET
  |  X_Addr  |  Y_addr  |   DATA   |
*/

module xy_switch
# (
    parameter X_CORD = 0,
    parameter Y_CORD = 0,
    parameter NEIGHBOURS_N = 4
    )
  (
    // GLOBAL
    input clk_i,
    input rst_ni,

    output busy_o,

    // SWITCH INPUTS
    input [NEIGHBOURS_N-1 : 0] pckt_vld_sw_i,
    input [`PACKET_W * NEIGHBOURS_N - 1 : 0] pckt_sw_i,
    // SWITCH OUTPUTS
    output [NEIGHBOURS_N-1 : 0] pckt_rd_sw_o,
    output [NEIGHBOURS_N-1 : 0] pckt_vld_sw_o,
    output [`PACKET_W * NEIGHBOURS_N - 1 : 0] pckt_sw_o,

    // RESOURCE INPUT
    input pckt_vld_r_i,
    input [`PACKET_W - 1 : 0] pckt_r_i,
    output pckt_rd_r_o,
    // RESOURCE OUTPUT

    output pckt_vld_r_o,
    output [`PACKET_W - 1 : 0] pckt_r_o
    );

    // Wires
    wire busy_w = (|{pckt_vld_sw_i, pckt_vld_r_i} == 1'b1) ? 1'b1 : 1'b0;
    reg [`PACKET_W - 1 : 0] tmp_pckt_w;
    wire [`PACKET_ADDR_X_W - 1 : 0] x_addr = tmp_pckt_w[`PACKET_W-1 : `PACKET_W - `PACKET_ADDR_X_W];
    wire [`PACKET_ADDR_Y_W - 1 : 0] y_addr = tmp_pckt_w[`PACKET_W - `PACKET_ADDR_X_W - 1 : `PACKET_DATA_W];

    wire [`PACKET_W -1 : 0 ] pckt_sw_i_w [NEIGHBOURS_N - 1 : 0];
    genvar i;
    generate
      for (i=0; i < NEIGHBOURS_N; i = i + 1) begin
        assign pckt_sw_i_w[i] = pckt_sw_i[(i+1)*`PACKET_W -1 : i*`PACKET_W ];
      end
    endgenerate


    // Registers
    reg [`PACKET_W - 1 : 0] pckt_r_v;
    reg pckt_vld_r_v;
    reg [`PACKET_W - 1 : 0] pckt_sw_v [NEIGHBOURS_N - 1 : 0] ;
    reg [NEIGHBOURS_N-1 : 0] pckt_vld_sw_v;

    // Vars
    integer iter;

    // Input Data Arbiter
    /*
      Chooses which packet should be routed

      v0.5 - simple and with/ justice
       - LEFT has most priority
       - after that TOP
       - after that RIGHT
       - after that BOTTOm
       - after that RESOURCE

      v1.0 - RoundRobin + hopcounts (not yet done)

    */
    always @(*) begin
      if (|{pckt_vld_sw_i, pckt_vld_r_i}) begin
        casez ({pckt_vld_sw_i[3:0], pckt_vld_r_i})
          5'b1????: tmp_pckt_w = pckt_sw_i_w[0]; // LEFT always has priority
          5'b01???: tmp_pckt_w = pckt_sw_i_w[1];
          5'b001??: tmp_pckt_w = pckt_sw_i_w[2];
          5'b0001?: tmp_pckt_w = pckt_sw_i_w[3];
          5'b00001: tmp_pckt_w = pckt_r_i;
          default : tmp_pckt_w = 'h0;
        endcase
      end
      else begin
        tmp_pckt_w = 'h0;
      end
    end

    // XY algorithm
    /*
      first X movement (at X = X_addr move in Y axis)
      next Y movement (stop at Y=Y_addr)

    */
    always @(posedge clk_i or negedge rst_ni) begin

      if (!rst_ni) begin
        pckt_r_v <= 'b0;
        pckt_vld_r_v <= 1'b0;

        for (iter=0; iter < NEIGHBOURS_N; iter = iter + 1) begin
          pckt_sw_v[iter] <= 'b0;
          pckt_vld_sw_v[iter] <= 'b0 ;
        end
      end
      else begin
        if (x_addr == X_CORD ) begin
          // X movement Finished, start ELEVATION or DEELEVATION
          // NEIGHBOUR 0 - left
          // NEIGHBOUR 1 - top
          // NEIGHBOUR 2 - right
          // NEIGHBOUR 3 - bottom
          if (y_addr == Y_CORD) begin
          // Y movement Finished, route to Resource
            pckt_r_v <= tmp_pckt_w;
            pckt_vld_r_v <= 1'b1;
          end
          else if (y_addr > Y_CORD) begin
            //Y movement not finished
            pckt_sw_v[`BOT] <= tmp_pckt_w;
            pckt_vld_sw_v[`BOT] <= 1'b1;
          end
          else begin
            pckt_sw_v[`TOP] <= tmp_pckt_w;
            pckt_vld_sw_v[`TOP] <= 1'b1;
          end
        end
        else begin
          if (x_addr > X_CORD) begin
            //Y movement not finished
            pckt_sw_v[`RIGHT] <= tmp_pckt_w;
            pckt_vld_sw_v[`RIGHT] <= 1'b1;
          end
          else begin
            pckt_sw_v[`LEFT] <= tmp_pckt_w;
            pckt_vld_sw_v[`LEFT] <= 1'b1;
          end
        end
      end

    end

    generate
      for (i=0; i < NEIGHBOURS_N; i = i + 1) begin
        assign pckt_sw_o[(i+1)*`PACKET_W -1 : i*`PACKET_W ] = pckt_sw_v[i];
      end
    endgenerate

    assign pckt_vld_sw_o = pckt_vld_sw_v;
    assign busy_o = busy_w;

endmodule
