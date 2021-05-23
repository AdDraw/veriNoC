module tb
  # (
    parameter COL_CORD = 0,
    parameter ROW_CORD = 0,
    parameter PORT_N = 5, // 1 is minimum cause RESOURCE,
    parameter FIFO_DEPTH_W = 3,
    parameter COL_ADDR_W = 4,
    parameter ROW_ADDR_W = 4,
    parameter PCKT_DATA_W = 8,
    parameter PCKT_W = COL_ADDR_W + ROW_ADDR_W + PCKT_DATA_W
    )
  (

    // GLOBAL
    // input clk_i,
    input rst_ni,

    // SWITCH INPUT BUFFER ports
    input   [PORT_N - 1 : 0]            wr_en_sw_i,
    input   [PCKT_W * PORT_N - 1 : 0]   pckt_sw_i,
    output  [PORT_N - 1 : 0]            in_fifo_full_o,
    output  [PORT_N - 1 : 0]            in_fifo_overflow_o,

    // SWITCH OUTPUT BUFFER ports
    input   [PORT_N - 1 : 0]            nxt_fifo_full_i,
    input   [PORT_N - 1 : 0]            nxt_fifo_overflow_i,
    output  [PORT_N - 1 : 0]            wr_en_sw_o,
    output  [PCKT_W * PORT_N - 1 : 0]   pckt_sw_o
    );

    initial begin
      $display("TB SETUP:");
      $display("COL_CORD %d", COL_CORD);
      $display("ROW_CORD %d", ROW_CORD);
    end

    reg clk_i = 1'b0;
    always #5 clk_i <= ~clk_i;

    xy_switch
    #(
      .COL_CORD(COL_CORD),
      .ROW_CORD(ROW_CORD),
      .PORT_N(PORT_N),
      .FIFO_DEPTH_W(FIFO_DEPTH_W),
      .COL_ADDR_W(COL_ADDR_W),
      .ROW_ADDR_W(ROW_ADDR_W),
      .PCKT_DATA_W(PCKT_DATA_W),
      .PCKT_W(PCKT_W)
      )
    xy_switch_inst
    (
      .clk_i(clk_i),
      .rst_ni(rst_ni),
      .wr_en_sw_i(wr_en_sw_i),
      .pckt_sw_i(pckt_sw_i),
      .in_fifo_full_o(in_fifo_full_o),
      .in_fifo_overflow_o(in_fifo_overflow_o),
      .nxt_fifo_full_i(nxt_fifo_full_i),
      .nxt_fifo_overflow_i(nxt_fifo_overflow_i),
      .wr_en_sw_o(wr_en_sw_o),
      .pckt_sw_o(pckt_sw_o)
      );

    // the "macro" to dump signals
    `ifdef COCOTB_SIM
    initial begin
      $dumpfile ("dump.vcd");
      $dumpvars (0, xy_switch_inst);
      #1;
    end
    `endif

endmodule //
