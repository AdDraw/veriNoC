/*
  Adam Drawc @2021
  Description:
  Arbiter that uses priority_robin arbitration.

  Every cycle priority shift by 1
  If priority is high but req for that input is LOW, we lose a cycle
  Even though there are other requests HIGH.

*/
`timescale 1ns / 1ps

module round_robin_arbiter #(
  parameter IN_N = 5  // this should be 5 right now
) (
  input               clk_i,
  input               rst_ni,
  input  [IN_N-1 : 0] req_i,   // N hot encoding
  output [  IN_N-1:0] grant_o
);
  reg  [IN_N-1 : 0]                                   priority_robin;
  wire [IN_N-1 : 0] grant_w = priority_robin & req_i;
  always @(posedge clk_i or negedge rst_ni) begin
    if (!rst_ni) begin
      priority_robin <= {{IN_N - 1{1'b0}}, 1'b1};
    end else begin
      priority_robin <= {priority_robin[IN_N-2 : 0], priority_robin[IN_N-1]};
    end
  end
  assign grant_o = grant_w;
endmodule
