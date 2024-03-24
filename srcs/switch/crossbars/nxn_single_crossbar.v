/*
  Adam Drawc 2020
  Single NtoN Crossbar

  Simple Mux -> Demux Logic
  that given mux in and mux_out selectors chooses the
  from which in port to which out port route the data

  Only 1 data packet at a time
  Output Demux has registers.

  Inputs and outputs passed as "inlined" arrays of atomic packets.
*/
`timescale 1ns / 1ps
module nxn_single_crossbar #(
  parameter DATA_W = 8,
  parameter PORT_N = 5
) (
  input [(PORT_N * DATA_W) - 1 : 0] data_i,
  input [   $clog2(PORT_N) - 1 : 0] in_sel_i,
  input [   $clog2(PORT_N) - 1 : 0] out_sel_i,

  output [           DATA_W - 1 : 0] pckt_in_chosen_o,
  output [(PORT_N * DATA_W) - 1 : 0] data_o
);

  reg [DATA_W - 1 : 0] mux_out_data_v[PORT_N-1:0];

  genvar gi;
  generate
    wire [DATA_W - 1 : 0] mux_in[PORT_N-1:0];
    // Input data unroll
    for (gi = 0; gi < PORT_N; gi = gi + 1) begin
      assign mux_in[gi] = data_i[gi*DATA_W+:DATA_W];
    end
    // INPUT MUX
    wire [DATA_W - 1 : 0] mux_in_data_chosen_w = mux_in[in_sel_i];
  endgenerate

  integer i;
  // OUTPUT MUX, with wires
  always @(*) begin
    for (i = 0; i < PORT_N; i = i + 1) begin
      mux_out_data_v[i] = 0;
    end
    mux_out_data_v[out_sel_i] = mux_in_data_chosen_w;
  end

  // Wrapping data_o
  generate
    for (gi = 0; gi < PORT_N; gi = gi + 1) begin
      assign data_o[gi*DATA_W+:DATA_W] = mux_out_data_v[gi];
    end
  endgenerate
  assign pckt_in_chosen_o = mux_in_data_chosen_w;

endmodule
