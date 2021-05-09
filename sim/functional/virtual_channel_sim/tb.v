/*
  Adam Drawc
  cocotb simulation Testbench wrapper for Virtual Channel module
*/

module tb
  # (
      parameter VC_DEPTH_W  = 2, // 4 flit buffer (for now)
      parameter DATA_W      = 10,
      parameter ID_W        = 2,
      parameter CLK_PERIOD  = 10
      )
    (
      input                 rst_ni,
      // FIFO based input (data & wr_enable)
      input   [DATA_W-1:0]  data_i,
      input                 wr_en_i,
      // Allocator info input
      input                 chan_alloc_i, // HEADER won the competition info
      input                 chan_rdy_i,   // BUFFER on the other side is not full
      // To Route
      output  [DATA_W-1:0]  data_o,
      output                data_vld_o,
      output  [DATA_W-1:0]  header_o,

      // FIFO based output
      output                rdy_o         // backpressure signal
      );

    initial begin
      $display("TB SETUP:");
      $display("\t- DATA_W     %0d", DATA_W);
      $display("\t- VC_DEPTH_W %0d", VC_DEPTH_W);
      $display("\t- ID_W       %0d", ID_W);
    end

    reg clk_i = 1'b0;
    always #(CLK_PERIOD/2) clk_i <= ~clk_i;

    virtual_channel
    #(
      .VC_DEPTH_W(VC_DEPTH_W),
      .DATA_W(DATA_W),
      .ID_W(ID_W)
      )
    vc_inst
    (
      .clk_i(clk_i),
      .rst_ni(rst_ni),
      .data_i(data_i),
      .wr_en_i(wr_en_i),
      .chan_alloc_i(chan_alloc_i),
      .chan_rdy_i(chan_rdy_i),
      .header_o(header_o),
      .data_o(data_o),
      .data_vld_o(data_vld_o),
      .rdy_o(rdy_o)
      );

    // the "macro" to dump signals
    `ifdef COCOTB_SIM
    initial begin
      $dumpfile ("dump.vcd");
      $dumpvars (0, tb);
      #1;
    end
    `endif

endmodule //
