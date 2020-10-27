/*
  Circular FIFO made with ZipCPU FIFO Guide
*/
`timescale 1ns / 1ps
// `define ALMOST_THRESHOLD

module fifo
  #(
    `ifdef ALMOST_THRESHOLD
    parameter ALMOST_EMPTY_LEVEL = 2,
    parameter ALMOST_FULL_LEVEL = 10,
    `endif
    parameter DATA_WIDTH = 8,
    parameter FIFO_DEPTH_WIDTH = 2
    )
  (
    input clk_i,
    input rst_ni,
    input wr_en_i,
    input rd_en_i,
    input [DATA_WIDTH-1 : 0] data_i,
    output [DATA_WIDTH-1 : 0] data_o,
    output full_o,
    output empty_o,
    `ifdef ALMOST_THRESHOLD
    output almost_empty_o,
    output almmost_full_o,
    `endif
    output overflow_o,
    output underflow_o
    );
    localparam FIFO_DEPTH = 2**FIFO_DEPTH_WIDTH;

	initial begin
		$display("Verilog: FIFO_DEPTH_WIDTH %d",FIFO_DEPTH_WIDTH);
		$display("Verilog: DATA_WIDTH\t%d", DATA_WIDTH);
	end
    
    // Registers
    integer i;
    reg [DATA_WIDTH-1 : 0] data_v;
    reg [DATA_WIDTH-1 : 0] fifo_v [FIFO_DEPTH-1 : 0];
    reg [FIFO_DEPTH_WIDTH-1 : 0] wr_ptr_v, rd_ptr_v;
    reg overflow_v, underflow_v;

    // Wires
    wire full_w, empty_w;
    assign full_w   = (wr_ptr_v + 1'b1 == rd_ptr_v) ? 1'b1 : 1'b0;
    assign empty_w  = (wr_ptr_v == rd_ptr_v) ? 1'b1 : 1'b0;

    `ifdef ALMOST_THRESHOLD
    wire almost_empty_w, almmost_full_w;
    wire [FIFO_DEPTH_WIDTH-1 :0] val_in_fifo_w;
    assign val_in_fifo_w = (wr_ptr_v >= rd_ptr_v) ? wr_ptr_v - rd_ptr_v : FIFO_DEPTH - rd_ptr_v + wr_ptr_v;
    assign almost_empty_w = (val_in_fifo_w >= ALMOST_EMPTY_LEVEL) ? 1'b1 : 1'b0;
    assign almmost_full_w = (val_in_fifo_w <= ALMOST_EMPTY_LEVEL) ? 1'b1 : 1'b0;
    `endif


    // FIFO WRITE
    always @ ( posedge clk_i or negedge rst_ni ) begin
      if (!rst_ni) begin
		for (i=0; i < FIFO_DEPTH; i=i+1) begin
			fifo_v[i] <= 0;
		end
        overflow_v  <= 1'b0;
        wr_ptr_v    <= 0;
      end
      else begin
        if (wr_en_i ) begin
          if (!full_w || rd_en_i) begin
            fifo_v[wr_ptr_v]  <= data_i;
            wr_ptr_v          <= wr_ptr_v + 1'b1;
            overflow_v        <= 1'b0;
          end
          else begin
            overflow_v        <= 1'b1;
            wr_ptr_v          <= wr_ptr_v;
          end
        end
      end
    end

    //FIFO READ
    always @ ( posedge clk_i or negedge rst_ni ) begin
      if (!rst_ni) begin
        data_v      <= 0;
        underflow_v <= 1'b0;
        rd_ptr_v    <= 0;
      end
      else begin
        if (rd_en_i) begin
          if (!empty_w) begin
            data_v      <= fifo_v[rd_ptr_v];
            rd_ptr_v    <= rd_ptr_v + 1'b1;
            underflow_v <= 1'b0;
          end
          else begin
            underflow_v <= 1'b1;
            rd_ptr_v    <= rd_ptr_v;
          end
        end
      end
    end

    // Output Assignments
    assign data_o       = data_v;
    assign full_o       = full_w;
    assign empty_o      = empty_w;
    assign underflow_o  = underflow_v;
    assign overflow_o   = overflow_v;

    `ifdef ALMOST_THRESHOLD
    assign almost_empty_o = almost_empty_w;
    assign almmost_full_o = almmost_full_w;
    `endif
endmodule
