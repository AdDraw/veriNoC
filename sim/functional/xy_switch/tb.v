module tb
  # (
    parameter X_CORD = 0,
    parameter Y_CORD = 0,
    parameter PORT_N = 5, // 1 is minimum cause RESOURCE,
    parameter IN_FIFO_DEPTH_W = 3,
    parameter PCKT_XADDR_W = 4,
    parameter PCKT_YADDR_W = 4,
    parameter PCKT_DATA_W = 8,
    parameter PCKT_W = PCKT_XADDR_W + PCKT_YADDR_W + PCKT_DATA_W
    )
  (

    // GLOBAL
    input clk_i,
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
      $display("XCORD %d", X_CORD);
      $display("YCORD %d", Y_CORD);
    end

    xy_switch
    #(
      .X_CORD(X_CORD),
      .Y_CORD(Y_CORD),
      .PORT_N(PORT_N),
      .IN_FIFO_DEPTH_W(IN_FIFO_DEPTH_W),
      .PCKT_XADDR_W(PCKT_XADDR_W),
      .PCKT_YADDR_W(PCKT_YADDR_W),
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
