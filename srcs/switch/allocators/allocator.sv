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
    - static priority based ( inputs have priority that is static and should be chosen based on the ROUTING algo)
    - FIFO fullness (requires fifo_pressure input signal)

  output:
  - selector for the input ( chooses which packet to pass to the output)
  - info that let's us read the data from the VC (there is a possiblity to make it a single signal)
    - channel_alloc info (let's VCs know when it's ok to read data (1 bit from each outchan goes to each in_chan))
    - backpressure info for VCs to know when it's okay to read data
*/
`timescale 1ns / 1ps
module allocator #(
  parameter IN_N = 5,  // to specify from how many inputs we should choose
  parameter FLIT_ID_W = 2,  // how many bits are taken for ID in each FLIT
  parameter OUT_CHAN_ID = 0,  // which output channel is this Alloc assigned to
  parameter ARB_TYPE = 0,  // what type of arbitration should be used (0 - matrix, 1 - round robin, 2 - static_priority)
  parameter TAIL_ID = 2'b11
) (
  input                  clk_i,
  input                  rst_ni,
  // Requests & grants
  input  wire [IN_N-1:0] req_i,
  output wire [IN_N-1:0] grant_o,
  // output channel allocation
  input  wire [IN_N-1:0] flit_id_is_tail_i,
  input  wire [IN_N-1:0] data_vld_i,
  // Backpressure (information from the forward node connected to the channel)
  input  wire            oc_rdy_i,
  output wire            oc_vld_o
);
  reg  [IN_N-1:0] grant_d;
  wire [IN_N-1:0] grant_w;
  wire [IN_N-1:0] req_w;
  assign req_w = req_i & data_vld_i & ~grant_d;

  always @(posedge clk_i or negedge rst_ni) begin
    if (!rst_ni) begin
      grant_d <= {IN_N{1'b0}};
    end else begin
      if (|grant_d) begin
        if (flit_id_is_tail_i & oc_rdy_i) begin
          grant_d <= {IN_N{1'b0}};
        end
      end else grant_d <= grant_w;
    end
  end

  generate
    if (ARB_TYPE == 0) begin  //matrix arb
      matrix_arbiter #(
        .IN_N(IN_N)
      ) arb (
        .clk_i  (clk_i),
        .rst_ni (rst_ni),
        .req_i  (req_w),
        .grant_o(grant_w)
      );
    end else if (ARB_TYPE == 1) begin
      round_robin_arbiter #(
        .IN_N(IN_N)
      ) arb (
        .clk_i  (clk_i),
        .rst_ni (rst_ni),
        .req_i  (req_w),
        .grant_o(grant_w)
      );
    end else if (ARB_TYPE == 2) begin
      static_priority_arbiter #(
        .IN_N(IN_N)
      ) arb (
        .req_i  (req_w),
        .grant_o(grant_w)
      );
    end else begin
      initial $error("Wrong Arbitration Type, possible options 0,1,2");
    end
  endgenerate

  // Allocation of VC
  assign sel_o    = grant_d;
  assign oc_vld_o = &(grant_d & data_vld_i &{IN_N{oc_rdy_i}});

endmodule  // allocator
