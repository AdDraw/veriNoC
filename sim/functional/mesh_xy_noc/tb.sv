`define PACKET_W (PCKT_DATA_W + $clog2(ROW_N) + $clog2(COL_M))
`define RSC_PCKT_RANGE (`PACKET_W * ROW_N * COL_M) - 1 : 0
`define CALC_PCKT_RANGE(ROW_IDX, COL_IDX) (((ROW_IDX*COL_M) + COL_IDX + 1) * `PACKET_W) - 1 : (((ROW_IDX*COL_M) + COL_IDX) * `PACKET_W)

module tb
  # (
    parameter ROW_N = 3,
    parameter COL_M = 3,
    parameter FIFO_DEPTH_W = 3,
    parameter PCKT_DATA_W = 8,
    parameter CLK_PERIOD = 10
    )
  (
    // GLOBAL
    //input clk_i,
    input rst_ni,

    // RESOURCE INPUT CHANNEL
    input  [`PACKET_W-1:0]          rsc_pckt_i [(ROW_N*COL_M)-1:0],
    input  [(ROW_N * COL_M) -1 : 0] rsc_wren_i,
    output [(ROW_N * COL_M) -1 : 0] noc_full_o,
    output [(ROW_N * COL_M) -1 : 0] noc_ovrflw_o,

    // RESOURCE OUTPUT CHANNEL
    output [`PACKET_W-1:0]          noc_pckt_o [(ROW_N*COL_M)-1:0],
    output [(ROW_N * COL_M) -1 : 0] noc_wren_o,
    input  [(ROW_N * COL_M) -1 : 0] rsc_full_i,
    input  [(ROW_N * COL_M) -1 : 0] rsc_ovrflw_i
    );

    initial begin
      $display("TB SETUP:");
      $display("ROW_N %d", ROW_N);
      $display("COL_M %d", COL_M);
      $display("FIFO_DEPTH_W %d", FIFO_DEPTH_W);
      $display("PCKT_DATA_W %d", PCKT_DATA_W);
    end

    reg clk_i = 1'b0;
    always #(CLK_PERIOD/2) clk_i <= ~clk_i;

    wire [`RSC_PCKT_RANGE] rsc_pckt_iw;
    wire [`RSC_PCKT_RANGE] noc_pckt_ow;

    genvar ri, ci;
    for (ri = 0; ri < ROW_N; ri=ri+1)
    begin
        for (ci = 0; ci < COL_M; ci=ci+1)
        begin
            assign rsc_pckt_iw[`CALC_PCKT_RANGE(ri,ci)] = rsc_pckt_i[ri*COL_M + ci];
            assign noc_pckt_o[ri*COL_M + ci] = noc_pckt_ow[`CALC_PCKT_RANGE(ri,ci)];
        end
    end

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

      .rsc_pckt_i(rsc_pckt_iw),
      .rsc_wren_i(rsc_wren_i),
      .noc_full_o(noc_full_o),
      .noc_ovrflw_o(noc_ovrflw_o),

      .noc_pckt_o(noc_pckt_ow),
      .noc_wren_o(noc_wren_o),
      .rsc_full_i(rsc_full_i),
      .rsc_ovrflw_i(rsc_ovrflw_i)
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
