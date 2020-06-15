`timescale 1ns / 1ps

module counter_nbit
  #(
    parameter CNT_BITWIDTH = 8,
    parameter ENABLE_LOW_SAT = 1,
    parameter ENABLE_HIGH_SAT = 1,
    parameter ALMOST_EMPTY_LEVEL = 10,
    parameter ALMOST_FULL_LEVEL = 250)
  (
    input clk_i,
    input rst_ni,
    input dir_i,
    output [CNT_BITWIDTH-1 : 0] counter_o,
    output almost_full_o,
    output almost_empty_o);

    reg [CNT_BITWIDTH-1 : 0] counter_v;
    wire almost_full_w = (ENABLE_HIGH_SAT) ? ((counter_v >= ALMOST_FULL_LEVEL) ? 1'b1 : 1'b0) : 1'b0;
    wire almost_empty_w = (ENABLE_LOW_SAT) ? ((counter_v <= ALMOST_EMPTY_LEVEL) ? 1'b1 : 1'b0) : 1'b0;

    always @(posedge clk_i or negedge rst_ni)
    begin
    	if (~rst_ni)
      begin
  	     counter_v = 0;
  	  end
    	else
      begin
        if (dir_i)
        begin
          counter_v = counter_v + 1'b1;
        end
        else
        begin
          counter_v = counter_v - 1'b1;
        end
      end
    end

    assign counter_o = counter_v;
    assign almost_full_o = almost_full_w;
    assign almost_empty_o = almost_empty_w;

endmodule
