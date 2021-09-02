/*
  Adam Drawc
  cocotb simulation Testbench wrapper for Virtual Channel module
*/
`timescale 1ns / 1ps
`define CHAN_SEL_W  $clog2(IN_N)
`define RTR_RES_W   $clog2(OUT_M)
module tb
  # (
      parameter IN_N        = 5,  // to specify from how many inputs we should choose
      parameter OUT_M       = 5,  // for route result inputs
      parameter FLIT_ID_W   = 2,  // how many bits are taken for ID in each FLIT
      parameter HOP_CNT_W   = 4,  // for hopcount
      parameter OUT_CHAN_ID = 0,  // which output channel is this Alloc assigned to
      parameter CLK_PERIOD  = 10
      )
    (
      input                           rst_ni,
      // Routing result (states which signals want to use this output channel)
      input [(IN_N*`RTR_RES_W)-1 : 0] rtr_res_i,    // this could be a 1 bit signal that simply states that an
      input [(IN_N*`RTR_RES_W)-1 : 0] rtr_res_vld_i,
      //input wants to use this output
      // input [(IN_N*HOP_CNT_W)-1:0]    hop_count_i,  // used to decide initial priority
      input [(IN_N*FLIT_ID_W)-1 : 0]  flit_id_i,
      input [IN_N-1:0]                data_vld_i,
      // Select the input to route
      output [`CHAN_SEL_W-1 : 0]      sel_o,     // answers which input (based on the input arbitration)
      output                          out_vld_o,
      // output out_vld_o,                       //answers when the data is being routed(can be routed) (based on backpressure)
      // Data to send to VCs (Virtual Channel)
      output                          forward_node_rdy_i,
      output [IN_N-1:0 ]              chan_alloc_o
      );

    initial begin
      $display("TB SETUP: Allocator");
      $display("\t- IN_N        %0d", IN_N);
      $display("\t- OUT_M       %0d", OUT_M);
      $display("\t- FLIT_ID_W   %0d", FLIT_ID_W);
      $display("\t- HOP_CNT_W   %0d", HOP_CNT_W);
      $display("\t- OUT_CHAN_ID %0d", OUT_CHAN_ID);
    end

    reg clk_i = 1'b0;
    always #(CLK_PERIOD/2) clk_i <= ~clk_i;

    allocator
    #(
      .IN_N(IN_N),
      .OUT_M(OUT_M),
      .FLIT_ID_W(FLIT_ID_W),
      .HOP_CNT_W(HOP_CNT_W),
      .OUT_CHAN_ID(OUT_CHAN_ID)
      )
    x_alloc
    (
      .clk_i(clk_i),
      .rst_ni(rst_ni),
      .rtr_res_i(rtr_res_i),
      .rtr_res_vld_i(rtr_res_vld_i),
      .hop_count_i(0),
      .flit_id_i(flit_id_i),
      .data_vld_i(data_vld_i),  //From VC
      .forward_node_rdy_i(forward_node_rdy_i),
      .sel_o(sel_o),
      .out_vld_o(out_vld_o),
      .chan_alloc_o(chan_alloc_o)                           // to VCs
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
