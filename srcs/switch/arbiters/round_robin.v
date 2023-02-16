/*
  Adam Drawc @2021
  Description:
  Arbiter that uses priority_robin arbitration.
  
  Every cycle priority shift by 1
  If priority is high but req for that input is LOW, we lose a cycle
  Even though there are other requests HIGH.

*/
`timescale 1ns / 1ps

module round_robin_arb
  #(
    parameter IN_N = 5 // this should be 5 right now
  ) (
    input                      clk_i,
    input                      rst_ni,
    input   [IN_N-1 : 0]       req_i,  // N hot encoding
    output  [$clog2(IN_N)-1:0] grant_o,
    output                     grant_vld_o
  );

  reg [IN_N-1 : 0] priority_robin;
  wire [IN_N-1 : 0] grant_w = priority_robin & req_i;

  reg [$clog2(IN_N)-1:0] grant_bcd_w;
  always @(*) begin
    grant_bcd_w <= 0;
    for (integer i = 0; i < IN_N; i = i + 1) begin
      if (grant_w[i]) grant_bcd_w <= i;
    end
  end

  always @(posedge clk_i or negedge rst_ni) begin
    if (!rst_ni) begin
      priority_robin <= 1;
    end
    else begin
      priority_robin[0] <= priority_robin[IN_N-1];
      priority_robin[IN_N-1 : 1] <= priority_robin[IN_N-2 : 0];
    end
  end

  assign grant_o = grant_bcd_w;
  assign grant_vld_o = |grant_w;

endmodule