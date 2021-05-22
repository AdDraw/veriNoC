/* Adam Drawc 2021

  Description:
    Allocator should know when it should allocate resources for the packet at
    the input.

    This is an implementation of a simple PER OUTPUT CHANNEL ALLOCATOR
    (simple since it will work only for minimal-routing)

    Resources:
      - output channel bandwidth
      - forward node buffer space

    Answers questions:
    - is it okay to route the packet?
      - Requires backpressure that gives information about:
        - forward buffer space availability
        - Channel bandwidth availability
          (if a packet is being routed in 10 flits it means that for 10 cycles
           channel bandwidth is used up by this packet and nothing else can be
           routed)
    - which packet to choose in case of packets competing for resources
      - Arbitration needs to be done based on:
        - hop count (how long is the packet in the network already)
        - In case of buffers > packet size, which FIFO is fuller (holds more data)
        - static priority Arbitration( helpful when 2 packets have same values -> useful to prevent deadlock)

  It should work for Flitized packets (split into flits)
  HEADER FLITS compete for resources.
  When one HEADER FLIT wins it allocates the channel for the whole packet size.
  When a tail-flit from this packet arrives it deallocates the channel which allows
  other channels that are waiting to compete again.

  Inputs should be:
  - routing results
  - hop_count(if it was included)
  - backpressure info (im assuming flit-based flow control )
    - fifo full signal (indicates that the buffer cannot take in the )
    - fifo packet space left(for packet-based Flow control)
  - FLIT ID needs to be present

  Internal state
  - IDLE - waits for inputs
  - ALLOCATED - resources were allocated, deallocation through a TAIL flit
    - no other packet allocate the output when ALLOCATOR allocats the output

  Internal signals
  - arbitration result
    - hop_count based (needs the info about hop_count & when header is passed we need to increment it)
    - static priority based ( inputs have priority that is static and should be chosen based on the ROUTING algo)
    - FIFO fullness (requires fifo_pressure input signal)

  output:
  - selector for the input ( chooses which packet to pass to the output)
  - info that let's us read the data from the VC (there is a possiblity to make it a single signal)
    - channel_alloc info (let's VCs know when it's ok to read data (1 bit from each outchan goes to each in_chan))
    - backpressure info for VCs to know when it's okay to read data
*/
`timescale 1ns / 1ps
module allocator
  #(
    `ifdef YS_ALLOCATOR_TOP
    parameter IN_N        = `YS_IN_N,
    parameter OUT_M       = `YS_OUT_M,
    parameter FLIT_ID_W   = `YS_FLIT_ID_W,
    parameter HOP_CNT_W   = `YS_HOP_CNT_W,
    parameter OUT_CHAN_ID = `YS_OUT_CHAN_ID
    `else
    parameter IN_N        = 5,  // to specify from how many inputs we should choose
    parameter OUT_M       = 5,  // for route result inputs
    parameter FLIT_ID_W   = 2,  // how many bits are taken for ID in each FLIT
    parameter HOP_CNT_W   = 4,  // for hopcount
    parameter OUT_CHAN_ID = 0   // which output channel is this Alloc assigned to
    `endif
    )
   (
    input                           clk_i,
    input                           rst_ni,
    // Routing result (states which signals want to use this output channel)
    input [(IN_N*`RTR_RES_W)-1 : 0] rtr_res_i,    // this could be a 1 bit signal that simply states that an input
    input [IN_N-1:0]                rtr_res_vld_i,

    // wants to use this output
    input [(IN_N*HOP_CNT_W)-1:0]    hop_count_i,  // used to decide initial priority
    input [(IN_N*FLIT_ID_W)-1 : 0]  flit_id_i,
    input [IN_N-1:0]                data_vld_i,
    // Backpressure (information from the forward node connected to the channel)
    input                           forward_node_rdy_i,
    // Select the input to route
    output [`CHAN_SEL_W-1 : 0]      sel_o,     // answers which input (based on the input arbitration)
    output                          out_vld_o,
    // output out_vld_o,                       //answers when the data is being routed(can be routed) (based on backpressure)
    // Data to send to VCs (Virtual Channel)
    output [IN_N-1:0]               chan_alloc_o
    );

  // REGS
  reg [IN_N-1:0 ]         chan_alloc;
  reg [`CHAN_SEL_W-1 : 0] sel;

  // WIRES
  wire [IN_N-1:0]         vld_input_hop_w;
  wire [IN_N-1:0]         vld_input_stat_w;
  wire                    not_conclusive_w;
  wire [$clog2(IN_N)-1:0] static_arb_res_w;
  wire [$clog2(IN_N)-1:0] hop_arb_res_w;        //specifies which input to choose
  wire [FLIT_ID_W-1:0]    flit_id_w [IN_N-1:0];
  wire [IN_N-1:0]         rtr_res_w;            // transformed to 1bit ENABLE signals
  genvar gi;
  generate
    for(gi=0; gi<IN_N; gi=gi+1)
    begin
      assign flit_id_w[gi] = flit_id_i[FLIT_ID_W*(gi+1)-1   : FLIT_ID_W*gi];
      assign rtr_res_w[gi] = (rtr_res_i[`RTR_RES_W*(gi+1)-1 : `RTR_RES_W*gi] == OUT_CHAN_ID) ? rtr_res_vld_i[gi] : 1'b0;
    end
  endgenerate

  assign vld_input_hop_w = rtr_res_w & data_vld_i;

  always @ ( posedge(clk_i), negedge(rst_ni) ) begin
    if (!rst_ni) begin
      chan_alloc  <= 0;
      sel         <= 0;
    end
    else begin
      if (|chan_alloc) begin
        if (flit_id_w[sel] == `TAIL_ID) begin
          chan_alloc <= 0;
        end
      end
      else begin
        if (|vld_input_hop_w && forward_node_rdy_i) begin
          chan_alloc <= 0;
          if (not_conclusive_w) begin                 // static priority arbiter
            chan_alloc[static_arb_res_w]  <= 1'b1;
            sel                           <= static_arb_res_w;
          end
          else begin                                  // hop cnt arbiter
            chan_alloc[hop_arb_res_w]     <= 1'b1;
            sel                           <= hop_arb_res_w;
          end
        end
      end
    end
  end

  // Input Arbitration in case of COMPETING INPUTs
  hop_cnt_arbiter //initial arbitration based on hop_cnt values
  #(
      .IN_N(IN_N),
      .HOP_CNT_W(HOP_CNT_W)
      )
  hop_arb
    (
      .vld_input_i(vld_input_hop_w),
      .hop_cnt_i(hop_count_i),
      .vld_input_o(vld_input_stat_w),
      .arb_res_o(hop_arb_res_w),
      .not_conclusive_o(not_conclusive_w)
      );

  static_priority_arbiter // secondary arbitration if primary arb is not conclusive
  #(
      .IN_N(IN_N)
      )
  priority_arb
    (
      .vld_input_i(vld_input_stat_w),
      .arb_res_o(static_arb_res_w)
      );

  // Allocation of VC
  assign chan_alloc_o = chan_alloc;
  assign sel_o        = sel;
  assign out_vld_o    = chan_alloc[sel] & data_vld_i[sel] & forward_node_rdy_i;

endmodule // allocator
