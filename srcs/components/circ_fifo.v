/*
  Circular FIFO made with ZipCPU FIFO Guide

  - Asynchronous Resets
  - utilizes N-1 spaces

*/
`timescale 1ns / 1ps

module circ_fifo
  #(
    parameter DATA_W        = 8,
    parameter FIFO_DEPTH_W  = 2,
    parameter ID            = 0
    )
  (
    input   clk_i,
    input   rst_ni,
    input   wr_en_i,
    input   rd_en_i,
    input   [DATA_W-1 : 0] data_i,
    output  [DATA_W-1 : 0] data_o,
    output  full_o,
    output  empty_o,
    output  overflow_o,
    output  underflow_o
    );
    localparam FIFO_DEPTH = 2**FIFO_DEPTH_W;

  `ifdef LOG_DEBUG
	initial begin
		$display("Verilog: FIFO%d -FIFO_DEPTH_W %d",ID, FIFO_DEPTH_W);
		$display("Verilog: FIFO%d -DATA_W\t%d",ID, DATA_W);
	end
  `endif

  // Registers
  integer i;
  reg [DATA_W-1 : 0]        data_v;
  reg [DATA_W-1 : 0]        fifo_v [FIFO_DEPTH-1 : 0];
  reg [FIFO_DEPTH_W-1 : 0]  wr_ptr_v, rd_ptr_v;
  reg                       overflow_v, underflow_v;

  // Wires
  wire full_w, empty_w;
  assign full_w   = (wr_ptr_v + 1'b1 == rd_ptr_v) ? 1'b1 : 1'b0;
  assign empty_w  = (wr_ptr_v == rd_ptr_v)        ? 1'b1 : 1'b0;

  // FIFO WRITE
  always @ ( posedge clk_i or negedge rst_ni) begin
    if (!rst_ni) begin
      wr_ptr_v    <= 0;
      overflow_v  <= 1'b0;
    end
    else begin
      if (wr_en_i) begin
        if (!full_w || rd_en_i) begin
          fifo_v[wr_ptr_v]  <= data_i;
          wr_ptr_v          <= wr_ptr_v + 1'b1;
          overflow_v        <= 1'b0;
        end
        else begin
          wr_ptr_v          <= wr_ptr_v;
          overflow_v        <= 1'b1;
        end
      end
      else begin
        if (!full_w) overflow_v <= 1'b0;
      end
    end
  end

  //FIFO READ
  always @ ( posedge clk_i or negedge rst_ni) begin
    if (!rst_ni) begin
      data_v      <= 0;
      rd_ptr_v    <= 0;
      underflow_v <= 1'b0;
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
      else begin
        if (!empty_w) underflow_v <= 1'b0;
      end
    end
  end

  // Output Assignments
  assign data_o       = data_v;
  assign full_o       = full_w;
  assign empty_o      = empty_w;

  `ifdef COCOTB_SIM
  initial begin
    $dumpfile ("dump.vcd");
    $dumpvars (0, circ_fifo);
    #1;
  end
  `endif

  `ifdef COCOTB_SIM
  initial begin
    $dumpfile ("dump.vcd");
    $dumpvars (0, circ_fifo);
    #1;
  end
  `endif

  `ifdef COCOTB_SIM
  initial begin
    $dumpfile ("dump.vcd");
    $dumpvars (0, circ_fifo);
    #1;
  end
  `endif

  `ifdef FORMAL
    initial assume(!rst_ni);

    always @(*) begin
      if (rst_ni)
      begin
        // Full & Empty checks
        assert (!(empty_o && full_o));
        // Underflow check
        if (full_o == 1'b0) assert (!overflow_o);
        // Underflow check
        if (empty_o == 1'b0) assert (!underflow_o);
        if (wr_ptr_v == rd_ptr_v) assert (empty_o);
        if (wr_ptr_v + 1'b1 == rd_ptr_v) assert(full_o);
      end
      else $display("BADBAD");
    end
  `endif
endmodule
