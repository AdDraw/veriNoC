`timescale 1ns / 100ps `default_nettype none
module mux_Nx1 #(
  parameter integer IN_N   = 8,
  parameter integer DATA_W = 64
) (
  input  wire  [IN_N-1:0][DATA_W-1:0] data_i,
  input  wire            [  IN_N-1:0] sel_i,
  output logic           [DATA_W-1:0] data_o
);

  always @(*) begin
    data_o = 'd0;  //default to Oth input to not create a latch
    for (integer i = 0; i < IN_N; i = i + 1) begin
      if (sel_i[i]) data_o = data_i[i];
    end
  end

endmodule
`default_nettype wire
