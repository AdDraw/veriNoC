module tb
  # (
    parameter COL_CORD = 0,
    parameter ROW_CORD = 0,
    parameter PORT_N = 5, // 1 is minimum cause RESOURCE,
    parameter IN_FIFO_DEPTH_W = 3,
    parameter PACKET_COL_ADDR_W = 4,
    parameter PACKET_ROW_ADDR_W = 4,
    parameter PACKET_DATA_W = 8,
    parameter ARB_TYPE = 0,
    parameter PACKET_W = PACKET_COL_ADDR_W + PACKET_ROW_ADDR_W + PACKET_DATA_W
    )
  (

    // GLOBAL
    // input clk_i,
    input rst_ni,

    // SWITCH INPUT BUFFER ports
    input   [PORT_N - 1 : 0]            wr_en_sw_i,
    input   [PACKET_W * PORT_N - 1 : 0] pckt_sw_i,
    output  [PORT_N - 1 : 0]            in_fifo_full_o,
    output  [PORT_N - 1 : 0]            in_fifo_overflow_o,

    // SWITCH OUTPUT BUFFER ports
    input   [PORT_N - 1 : 0]            nxt_fifo_full_i,
    input   [PORT_N - 1 : 0]            nxt_fifo_overflow_i,
    output  [PORT_N - 1 : 0]            wr_en_sw_o,
    output  [PACKET_W * PORT_N - 1 : 0] pckt_sw_o
    );

    initial begin
      $display("TB SETUP:");
      $display("COL_CORD %d", COL_CORD);
      $display("ROW_CORD %d", ROW_CORD);
    end

    reg clk_i = 1'b0;
    always #5 clk_i <= ~clk_i;

    xy_switch #(
      .COL_CORD(COL_CORD),
      .ROW_CORD(ROW_CORD),
      .PORT_N(PORT_N),
      .IN_FIFO_DEPTH_W(IN_FIFO_DEPTH_W),
      .PCKT_COL_ADDR_W(PACKET_COL_ADDR_W),
      .PCKT_ROW_ADDR_W(PACKET_ROW_ADDR_W),
      .PCKT_DATA_W(PACKET_DATA_W),
      .PCKT_W(PACKET_W),
      .ARB_TYPE(ARB_TYPE)
    ) xy_switch_inst (
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
