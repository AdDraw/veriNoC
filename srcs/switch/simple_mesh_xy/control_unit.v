/*
  Author: Adam Drawc
  Module Name: Control Unit that will be used for controlling which packet to route and if the output is ready for it
*/
`timescale 1ns / 1ps
module control_unit
# (
    parameter PORT_N = 5
    )
  (
    input clk_i,
    input rst_ni,
    // Processing Input Requests
    // If there are packets ready choose the one to read
    input  [PORT_N - 1 : 0] empty_i,
    output [PORT_N - 1 : 0] rd_en_o,
    output [PORT_N - 1 : 0] vld_input_o,

    // Processing output
    input  [PORT_N - 1 : 0] full_i,
    output [PORT_N - 1 : 0] wr_en_o,

    // Router Input
    input [$clog2(PORT_N)-1 : 0] mux_in_sel_i,
    input [$clog2(PORT_N)-1 : 0] mux_out_sel_i

    );

    reg   [PORT_N-1 : 0]    vld_input_v;
    integer i;

    wire  [PORT_N-1 : 0]    rd_en_w = ~( empty_i | vld_input_v );
    wire  [PORT_N - 1 : 0]  wr_en_w = (|vld_input_v) ? (1 << mux_out_sel_i) & (~full_i) : 0;

    // Read while HOT
    // rd_en control
    // vld_input_o control
    always @(posedge clk_i or negedge rst_ni)
    begin
      if (!rst_ni)
      begin
        vld_input_v <= 0;
      end
      else
      begin
        // if one is not empty and at least 1 is not vld
        vld_input_v <= (rd_en_w | vld_input_v);
        if ( |wr_en_w )
        begin
          for (i = 0; i < PORT_N; i = i + 1) begin
            if ( i == mux_in_sel_i )
            begin
              vld_input_v[i] <= 1'b0; // CLEAN !
            end
            else
            begin
              vld_input_v[i] <= rd_en_w[i] | vld_input_v[i];
            end
          end
        end
      end
    end


    // when to update the output regs
    assign rd_en_o      = rd_en_w;
    assign vld_input_o  = vld_input_v;
    assign wr_en_o      = wr_en_w;


    `ifdef FORMAL

      integer fi = 0;

      always @(*) begin
        if (rst_ni) begin
          for (fi=0; fi < PORT_N; fi++) begin
            assert(!(vld_input_v[fi] && rd_en_w[fi]));
            if (empty_i[fi]) assert(!rd_en_w[fi]);
            if (full_i[fi]) assert(!wr_en_w[fi]);
          end
        end
      end
    `endif

endmodule
