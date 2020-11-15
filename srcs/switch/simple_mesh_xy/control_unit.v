/*
  Author: Adam Drawc
  Module Name: Control Unit that will be used for controlling which packet to route and if the output is ready for it
*/

module control_unit
# (
    parameter INPUT_N = 4
    )
  (
    input clk_i,
    input rst_ni,
    // Processing Input Requests
    // If there are packets ready choose the one to read
    input  [INPUT_N - 1 : 0] empty_i,
    output [INPUT_N - 1 : 0] rd_en_o,
    output [INPUT_N - 1 : 0] vld_input_o,

    // Processing output
    input  [INPUT_N - 1 : 0] full_i,
    output [INPUT_N - 1 : 0] wr_en_o,
    output [INPUT_N -1  : 0] vld_output_o,

    // Router Input
    input [$clog2(INPUT_N)-1 : 0] mux_in_sel_i,
    input [$clog2(INPUT_N)-1 : 0] mux_out_sel_i

    );

    reg [INPUT_N-1 : 0] vld_input_v;
    reg [INPUT_N-1 : 0] vld_output_v;

    wire [INPUT_N-1 : 0] rd_en_w = ~( empty_i | vld_input_v );
    wire [INPUT_N - 1 : 0] wr_en_w = vld_output_v & ~(full_i);

    // Read while HOT
    // rd_en control
    // vld_input_o control
    always @(posedge clk_i or posedge rst_ni)
    begin
      if (!rst_ni)
      begin
        vld_input_v <= 0;
      end
      else
      begin
        // if one is not empty and at least 1 is not vld
        vld_input_v <= (rd_en_w | vld_input_v);
        if (vld_output_v[mux_out_sel_i] == 0)
        begin
          vld_input_v[mux_in_sel_i] <= 1'b0;
        end
      end
    end

    // vld_output_o control
    always @(posedge clk_i or posedge rst_ni)
    begin
      if (!rst_ni)
      begin
        vld_output_v <= 0;
      end
      else
      begin
        vld_output_v[mux_out_sel_i] <= 1'b1;
        vld_output_v <= wr_en_w ^ vld_output_v;
      end
    end

    assign rd_en_o      = rd_en_w;
    assign vld_input_o  = vld_input_v;
    assign vld_output_o = vld_output_v;

endmodule
