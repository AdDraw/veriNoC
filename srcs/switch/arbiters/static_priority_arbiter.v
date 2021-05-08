/*
  Adam Drawc @2021
  Description:
  Arbiter that uses static priority encoding.
  This in turn allows to choose which input has priority in the case when inputs
  are competing for the same channel and other arbitration doesn't provide a
  clear result.
*/
`timescale 1ns / 1ps
`define result_range $clog2(IN_N)-1:0
module static_priority_arbiter
# (
    parameter IN_N = 5 // this should be 5 right now
    )
  (
    input   [IN_N - 1 : 0]  vld_input_i,
    output  [`result_range] arb_res_o
    );
    reg [`result_range] arb_res_w;
    always @(*)
    begin
      if (|vld_input_i)
      begin
        if      (vld_input_i[4])  arb_res_w = 4;
        else if (vld_input_i[3])  arb_res_w = 3;
        else if (vld_input_i[2])  arb_res_w = 2;
        else if (vld_input_i[1])  arb_res_w = 1;
        else if (vld_input_i[0])  arb_res_w = 0;
        else                      arb_res_w = 0;
      end
    end
    assign arb_res_o = arb_res_w;
endmodule
