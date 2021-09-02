/*
  Adam Drawc @2021
  Description:
  Arbiter that uses round_robin arbitration.
  Provides STRONG Fairness

  When request has been served it's priority drops to the lowest possible.
  In matrix Rows and Colums depict req_i (requestors).
  Row 0 is for requestor 0 and etc.
  When there matrix[i][j] = 1, it means that requestor i has priority above
  requestor j. When req 0 gets a grant, it then clears it's row with 0's,
  this indicates that it does no longer hold priority above other requestors.
  At the same time, column i should be filled with 1's indicating that every
  other requestor has priority above req i.

  TODO: reduce number of flip flops in the matrix, because only 1 triangular
  part of the matrix needs to be maintained
*/
`timescale 1ns / 1ps

module matrix_arb
  #(
    parameter IN_N = 4 // this should be 5 right now
    )
  (
    input                     clk_i,
    input                     rst_ni,
    input  [IN_N-1:0]         req_i,
    output [$clog2(IN_N)-1:0] grant_o
  );

  // Last granted requested moves to the end of the que
  reg   [IN_N-1:0]  p_matrix [IN_N-1:0];
  wire  [IN_N-1:0]  grant_w;

  // MATRIX UPDATE CIRC
  integer i,j;
  always @(posedge clk_i, negedge rst_ni) begin
    if (!rst_ni) begin
      for (i = 0; i < IN_N; i = i + 1) begin
        for (j = 0; j < IN_N; j = j + 1) begin
          if (j > i)  p_matrix [i][j] <= 1'b1;
          else        p_matrix [i][j] <= 1'b0;
        end
      end
    end
    else begin
      for (i=0; i < IN_N; i=i+1) begin // row
        for (j=0; j < IN_N ; j = j + 1) begin // col
          if (grant_w[i] == 1'b1) begin
            p_matrix[i][j] <= 1'b0;
            p_matrix[j][i] <= 1'b1;
          end
        end
      end
    end
  end

  // GRANT CIRCUIT
  genvar gj, gi;
  generate
    for (gi = 0; gi < IN_N; gi = gi + 1) begin // col
      wire [IN_N-1:0] dis_w;
      for (gj = 0; gj < IN_N; gj = gj + 1) begin // row
        if (gj != gi) begin
          assign dis_w[gj] = req_i[gj] & p_matrix[gj][gi];
        end
        else
          assign dis_w[gj] = 1'b0;
      end
      assign grant_w[gi] =  req_i[gi] & ~(|dis_w);
    end
  endgenerate

  // from ONEHOT to DECIMAL
  reg [$clog2(IN_N)-1:0] grant_v;
  always @ ( * ) begin
    for (i = 0; i< IN_N; i = i + 1) begin
      if (grant_w[i] == 1'b1) grant_v <= i;
    end
  end

  assign grant_o = grant_v;

endmodule // round_robin_arb
