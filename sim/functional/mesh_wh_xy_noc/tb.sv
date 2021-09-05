`define RSC_PCKT_RANGE (CHANNEL_W * ROW_N * COL_M) - 1 : 0
`define CALC_PCKT_RANGE(ROW_IDX, COL_IDX) (((ROW_IDX*COL_M) + COL_IDX + 1) * CHANNEL_W) - 1 : (((ROW_IDX*COL_M) + COL_IDX) * CHANNEL_W)

module tb
  # (
    parameter ROW_N = 3,
    parameter COL_M = 3,
    parameter NODE_RADIX = 5,
    parameter FLIT_ID_W = 2,
    parameter NODE_BUFFER_DEPTH_W = 3,
    parameter CHANNEL_W = 10,
    parameter CLK_PERIOD = 10
    )
  (
    // GLOBAL
    //input clk_i,
    input rst_ni,

    // RESOURCE INPUT CHANNEL
    input  [CHANNEL_W-1:0]          in_chan_data_i [(ROW_N*COL_M)-1:0],
    input  [(ROW_N * COL_M) -1 : 0] in_chan_vld_i,
    output [(ROW_N * COL_M) -1 : 0] in_chan_rdy_o,

    // RESOURCE OUTPUT CHANNEL
    output [CHANNEL_W-1:0]          out_chan_data_o [(ROW_N*COL_M)-1:0],
    output [(ROW_N * COL_M) -1 : 0] out_chan_vld_o,
    input  [(ROW_N * COL_M) -1 : 0] out_chan_rdy_i
    );

    initial begin
      $display("TB SETUP:");
      $display("ROW_N %d", ROW_N);
      $display("COL_M %d", COL_M);
      $display("NODE_BUFFER_DEPTH_W %d", NODE_BUFFER_DEPTH_W);
      $display("CHANNEL_W %d", CHANNEL_W);
    end

    reg clk_i = 1'b0;
    always #(CLK_PERIOD/2) clk_i <= ~clk_i;

    wire [`RSC_PCKT_RANGE] in_chan_data_iw;
    wire [`RSC_PCKT_RANGE] out_chan_data_ow;

    genvar ri, ci;
    for (ri = 0; ri < ROW_N; ri=ri+1)
    begin
        for (ci = 0; ci < COL_M; ci=ci+1)
        begin
            assign in_chan_data_iw[`CALC_PCKT_RANGE(ri,ci)] = in_chan_data_i[ri*COL_M + ci];
            assign out_chan_data_o[ri*COL_M + ci] = out_chan_data_ow[`CALC_PCKT_RANGE(ri,ci)];
        end
    end

    mesh_wormhole_xy_noc #(
      .ROW_N(ROW_N),
      .COL_M(COL_M),
      .FLIT_ID_W(FLIT_ID_W),
      .NODE_RADIX(NODE_RADIX),
      .CHANNEL_W(CHANNEL_W),
      .NODE_BUFFER_DEPTH_W(NODE_BUFFER_DEPTH_W)
      )
    x_mesh_wh_xy_noc (
      .clk_i(clk_i),
      .rst_ni(rst_ni),

      .ichan_data_i(in_chan_data_iw),
      .ichan_vld_i(in_chan_vld_i),
      .ichan_rdy_o(in_chan_rdy_o),

      .ochan_data_o(out_chan_data_ow),
      .ochan_vld_o(out_chan_vld_o),
      .ochan_rdy_i(out_chan_rdy_i)
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
