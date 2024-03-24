// Adam Drawc 2021
/*
  Decription:
  Allows for N packets at once to be routed in parrallel
  Consists of N Nto1 muxes.

  Control:
    Each mux gets the SEL signal that indicates which input will
    be routed through this mux.
    Each mux output is hardwired to 1 physical output channel.
*/
`timescale 1ns / 1ps `default_nettype none
module nxn_parrallel_crossbar #(
  parameter DATA_W = 10,  //(2 bits for flit ID, 8 bits for the flit payload)
  parameter IN_N   = 5,
  parameter OUT_M  = 5
) (
  input  wire [ IN_N-1:0][DATA_W-1:0] data_i,  // data from input channels
  input  wire [OUT_M-1:0][  IN_N-1:0] sel_i,   // controlled by routing & Flow Control
  output wire [OUT_M-1:0][DATA_W-1:0] data_o   // data that goes into output channels
);
  genvar i;
  generate
    for (i = 0; i < OUT_M; i = i + 1) begin
      mux_Nx1 #(
        .IN_N  (IN_N),
        .DATA_W(DATA_W)
      ) muxX_inst (
        .data_i(data_i[i]),
        .sel_i (sel_i[i]),
        .data_o(data_o[i])
      );
    end
  endgenerate

endmodule
`default_nettype wire
