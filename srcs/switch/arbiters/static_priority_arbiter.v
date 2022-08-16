/*
  Adam Drawc @2021
  Description:
  Arbiter that uses static priority encoding.
  This in turn allows to choose which input has priority in the case when inputs
  are competing for the same channel and other arbitration doesn't provide a
  clear result.
*/
`timescale 1ns / 1ps
module static_priority_arbiter
  #(
    parameter IN_N = 5
  ) (
    input   [IN_N - 1 : 0]     req_i,
    output  [$clog2(IN_N)-1:0] grant_o
  );

  wire [IN_N-1 : 0]      grant_w;
  reg [$clog2(IN_N)-1:0] grant_bcd_w;
  always @(*) begin
    grant_bcd_w <= 0;
    for (integer i = 0; i < IN_N; i = i + 1) begin
      if (grant_w[i]) grant_bcd_w <= i;
    end
  end

  wire [IN_N : 0] x_carry_w;
  assign x_carry_w[0] = 0; 
  genvar gi;
  generate
    for ( gi = 0; gi < IN_N-1; gi = gi + 1) begin
      grant_with_carry x_grant (
        .req_i   (req_i[gi]),
        .carry_i (x_carry_w[gi]),
        .carry_o (x_carry_w[gi+1]),
        .grant_o (grant_w[gi])
      );
    end
  endgenerate 

  assign grant_o = grant_bcd_w;

endmodule

module grant_with_carry
(
  input req_i,
  input carry_i,
  output carry_o,
  output grant_o
);

  assign grant_o = ~carry_i & req_i;
  assign carry_o = carry_i | req_i;

endmodule