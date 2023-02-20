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
`timescale 1ns / 1ps
module nxn_parrallel_crossbar #(
  parameter DATA_W = 10,  //(2 bits for flit ID, 8 bits for the flit payload)
  parameter IN_N   = 5,
  parameter OUT_M  = 5
) (  //N inputs N outputs
  input  [        (IN_N*DATA_W)-1:0] data_i,  // data from input channels
  input  [(OUT_M*$clog2(OUT_M))-1:0] sel_i,   // controlled by routing & Flow Control
  output [       (OUT_M*DATA_W)-1:0] data_o   // data that goes into output channels
);

  genvar gi;
  // M muxes each N inputs
  generate
    wire [       DATA_W-1 : 0] mux_in [ IN_N];
    wire [$clog2(OUT_M)-1 : 0] mux_sel[OUT_M];

    // Inputs packaging
    for (gi = 0; gi < IN_N; gi = gi + 1) begin
      assign mux_in[gi] = data_i[`UNPACK(gi, DATA_W)];
    end

    for (gi = 0; gi < OUT_M; gi = gi + 1) begin
      // SEL packaging
      assign mux_sel[gi]                 = sel_i[`UNPACK(gi, $clog2(IN_N))];
      // Output assignment
      assign data_o[`UNPACK(gi, DATA_W)] = mux_in[mux_sel[gi]];
    end
  endgenerate

endmodule  // n_parrallel_crossbar
