/*
  Adam Drawc @2021
  Description:
  Arbiter that uses round_robin arbitration.
  Provides STRONG Fairness

  When request has been served it lands on the end of the q

*/
`timescale 1ns / 1ps

module round_robin_arb
  #(
    parameter IN_N = 5 // this should be 5 right now
    )
  (
    input                  clk_i,
    input   [IN_N - 1 : 0] req_i,
    output  [IN_N - 1 : 0] grant_o
  );

  // Last granted requested moves to the end of the que
  reg [IN_N -1 : 0] grant;

  always (posedge clk_i) begin : grant_circ
    grant <=
  end





endmodule // round_robin_arb
