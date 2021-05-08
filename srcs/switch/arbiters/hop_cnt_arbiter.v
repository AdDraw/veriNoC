/*
  Adam Drawc @2021

  Description:
    Module that gives priority to packets that made more hops in the network.
    Priority for such packets is higher because they should leave the network asap.

  Comparison is done through a COMPARATOR-TREE to get the results in the same cycle.
  This makes this implementation area heavier but faster.

  Only problematic case here is the fact that with arbitrary number of inputs this could grow fast.
  Making this implmenetation not really efficient.
  Because we are targeting a MESH network that has max 5 inputs and hop_cnt
  width will not be bigger than 5 bits it should be okay.

  If the area will be a crucial factor this could be optimized.
  If speed and critical_path lenght will be problematic this design could be pipelined.

  // RIGHT NOW WE ONLY CONSIDER CASE WITH 5 inputs
  this results in 3 stages
  // 1 stage -> 2 comparators
  // 2 stage -> 1 comparators
  // 3 stage -> 1 comparator (5th input with result of 1&2 stage)

*/
`timescale 1ns / 1ps
module hop_cnt_arbiter
  #(
    `ifdef YS_HOP_CNT_ARB_TOP
    parameter IN_N      = `YS_IN_N,
    parameter HOP_CNT_W = `YS_HOP_CNT_W
    `else
    parameter IN_N      = 5,
    parameter HOP_CNT_W = 3
    `endif
    )
  ( input   [IN_N-1:0]                vld_input_i,
    input   [(IN_N*HOP_CNT_W)-1 : 0]  hop_cnt_i,
    output  [$clog2(IN_N)-1:0]        arb_res_o,
    output  [IN_N-1:0]                vld_input_o,      // required for further arbitration if needed
    output                            not_conclusive_o  // set to HIGH when there are 2(or more) inputs that have the same value of HOP_COUNT
    );

  reg [HOP_CNT_W-1:0]     comp_res_0_v;
  reg [HOP_CNT_W-1:0]     comp_res_1_v;
  reg [HOP_CNT_W-1:0]     comp_res_2_v;
  reg [HOP_CNT_W-1:0]     max_hop_cnt_v;
  reg [$clog2(IN_N)-1:0]  arb_res_v;
  reg                     not_conclusive_v;

  wire [IN_N-1:0]         vld_input_w;
  wire [HOP_CNT_W-1:0]    hop_cnt_w [IN_N - 1 : 0];
  genvar gi;
  generate // package
    for( gi = 0; gi < IN_N; gi = gi+ 1)
    begin
      assign hop_cnt_w[gi] = (vld_input_i[gi]) ? hop_cnt_i[HOP_CNT_W*(gi+1)-1 : HOP_CNT_W*gi] : 0;
    end
  endgenerate

  always @ ( * ) begin
    if (hop_cnt_w[0] > hop_cnt_w[1]) begin
      comp_res_0_v  <= hop_cnt_w[0];
    end else begin
      comp_res_0_v  <= hop_cnt_w[1];
    end

    if (hop_cnt_w[2] > hop_cnt_w[3]) begin
      comp_res_0_v  <= hop_cnt_w[2];
    end else begin
      comp_res_0_v  <= hop_cnt_w[3];
    end

    if (comp_res_0_v > comp_res_1_v) begin
      comp_res_2_v  <= comp_res_0_v;
    end else begin
      comp_res_2_v  <= comp_res_1_v;
    end

    if (comp_res_2_v > hop_cnt_w[4]) begin
      max_hop_cnt_v <= comp_res_2_v;
    end else begin
      max_hop_cnt_v <= hop_cnt_w[4];
    end
  end

  generate
    for( gi = 0; gi < IN_N; gi = gi+ 1)
    begin
      assign vld_input_w[gi] = (hop_cnt_w[gi] == max_hop_cnt_v) ? 1'b1 : 1'b0;
    end
  endgenerate

  // if we have 2 vld inputs -> unambigous :/ we need to choose in a different manner (static for example)
  // if we only have 1 vld output that's cool, this was successful.
  always @ ( * ) begin
    not_conclusive_v <= 1'b0;
    arb_res_v        <= 0;
    case (vld_input_w)
      5'b00001 : arb_res_v <= 0;
      5'b00010 : arb_res_v <= 1;
      5'b00100 : arb_res_v <= 2;
      5'b01000 : arb_res_v <= 3;
      5'b10000 : arb_res_v <= 4;
      default  : not_conclusive_v <= 1'b1;
    endcase
  end

  assign vld_input_o      = vld_input_i & vld_input_w;
  assign arb_res_o        = arb_res_v;
  assign not_conclusive_o = not_conclusive_v;

endmodule // hop_cnt_arbiter
