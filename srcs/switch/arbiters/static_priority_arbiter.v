/*
  Adam Drawc @2021
  Description:
  Arbiter that uses static priority encoding.
  This in turn allows to choose which input has priority in the case when inputs
  are competing for the same channel and other arbitration doesn't provide a
  clear result.
  req_i LSB is at the lowest priority.
  req_i MSB is at the highest priority.
*/
`timescale 1ns / 1ps
module static_priority_arbiter #(
  parameter IN_N = 5
) (
  input  [IN_N-1:0] req_i,
  output [IN_N-1:0] grant_o
);

  wire [IN_N : 0] x_carry_w;
  assign x_carry_w[0] = 0;
  genvar gi;
  generate
    for (gi = 0; gi < IN_N; gi = gi + 1) begin
      grant_with_carry x_grant (
        .req_i  (req_i[IN_N-1-gi]),
        .carry_i(x_carry_w[gi]),
        .carry_o(x_carry_w[gi+1]),
        .grant_o(grant_o[IN_N-1-gi])
      );
    end
  endgenerate

endmodule
