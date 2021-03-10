`define PACKET_W (PCKT_DATA_W + $clog2(ROW_N) + $clog2(COL_M))
`define RSC_PCKT_RANGE (`PACKET_W * ROW_N * COL_M) - 1 : 0
`define CALC_PCKT_RANGE(ROW_IDX, COL_IDX) (((ROW_IDX*ROW_N) + COL_IDX + 1) * `PACKET_W) - 1 : (((ROW_IDX*ROW_N) + COL_IDX) * `PACKET_W)

module tb
  # (
    parameter ROW_N = 3,
    parameter COL_M = 3,
    parameter FIFO_DEPTH_W = 3,
    parameter PCKT_DATA_W = 8
    )
  (
    // GLOBAL
    //input clk_i,
    input rst_ni,

    // RESOURCE INPUT CHANNEL
    input  [`RSC_PCKT_RANGE]          rsc_pckt_i,
    input  [(ROW_N * COL_M) -1 : 0]   rsc_wren_i,
    output [(ROW_N * COL_M) -1 : 0]   rsc_full_o,
    output [(ROW_N * COL_M) -1 : 0]   rsc_ovrflw_o,

    // RESOURCE OUTPUT CHANNEL
    output [`RSC_PCKT_RANGE]          rsc_pckt_o,
    output [(ROW_N * COL_M) -1 : 0]   rsc_wren_o,
    input  [(ROW_N * COL_M) -1 : 0]   rsc_full_i,
    input  [(ROW_N * COL_M) -1 : 0]   rsc_ovrflw_i
    );

    initial begin
      $display("TB SETUP:");
      $display("ROW_N %d", ROW_N);
      $display("COL_M %d", COL_M);
      $display("FIFO_DEPTH_W %d", FIFO_DEPTH_W);
      $display("PCKT_DATA_W %d", PCKT_DATA_W);
    end

    reg clk_i = 1'b0;
    always #5 clk_i <= ~clk_i;

    mesh_xy_noc
    #(
      .ROW_N(ROW_N),
      .COL_M(COL_M),
      .FIFO_DEPTH_W(FIFO_DEPTH_W),
      .PCKT_DATA_W(PCKT_DATA_W)
      )
    inst_mesh_xy_noc
    (
      .clk_i(clk_i),
      .rst_ni(rst_ni),

      .rsc_pckt_i(rsc_pckt_i),
      .rsc_wren_i(rsc_wren_i),
      .rsc_full_o(rsc_full_o),
      .rsc_ovrflw_o(rsc_ovrflw_o),

      .rsc_pckt_o(rsc_pckt_o),
      .rsc_wren_o(rsc_wren_o),
      .rsc_full_i(rsc_full_i),
      .rsc_ovrflw_i(rsc_ovrflw_i)
      );

    // the "macro" to dump signals
    `ifdef COCOTB_SIM
    initial begin
      $dumpfile ("dump.vcd");
      $dumpvars (0, inst_mesh_xy_noc);
      #1;
    end
    `endif

endmodule //
