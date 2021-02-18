/*
  Adam Drawc 2020
  NtoN Crossbar

  Simple Mux -> Demux Logic
  that given mux in and mux_out selectors chooses the
  from which in port to which out port route the data

  Only 1 data packet at a time
  Output Demux has registers.

  Inputs and outputs passed as "inlined" arrays of atomic packets.
*/

module n_to_n_crossbar
# (
    parameter DATA_WIDTH = 8,
    parameter PORT_N = 5
    )
  (
    input   clk_i,
    input   rst_ni,

    input   [(PORT_N * DATA_WIDTH) - 1 : 0] data_i,
    input   [$clog2(PORT_N) - 1 : 0]        mux_in_sel_i,
    input   [$clog2(PORT_N) - 1 : 0]        mux_out_sel_i,

    output  [DATA_WIDTH - 1 : 0]            pckt_in_chosen_o,
    output  [(PORT_N * DATA_WIDTH) - 1 : 0] data_o
    );

    reg [DATA_WIDTH - 1 : 0] mux_out_data_v [PORT_N - 1 : 0];
    // reg [DATA_WIDTH - 1 : 0] mux_in_data_chosen_w;

    genvar i;
    generate
      wire [DATA_WIDTH -1 : 0]  mux_in [PORT_N - 1 : 0];
      // Input data unroll
      for( i = 0; i < PORT_N; i = i + 1)
      begin
        assign mux_in[i] = data_i[DATA_WIDTH*(i+1) - 1 : DATA_WIDTH*i];
      end
      // INPUT MUX
      wire [DATA_WIDTH - 1 : 0] mux_in_data_chosen_w = mux_in[mux_in_sel_i];

    endgenerate

    // OUTPUT MUX, with registers
    always @(*)
    begin
      mux_out_data_v[mux_out_sel_i] = mux_in_data_chosen_w;
      for (i = 0; i < PORT_N; i = i + 1)
      begin
        mux_out_data_v[i] = mux_out_data_v[i];
      end
    end

    // Wrapping data_o
    generate
      for( i = 0; i < PORT_N; i = i + 1)
      begin
        assign data_o[DATA_WIDTH*(i+1) - 1 : DATA_WIDTH*i] = mux_out_data_v[i];
      end
    endgenerate
    assign pckt_in_chosen_o = mux_in_data_chosen_w;

endmodule
