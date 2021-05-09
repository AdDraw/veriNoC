// Adam Drawc 2021
/*
  Description:
    Buffer + State that dictates how data should be read from the buffer

  Implemented as Circular FIFO + State & read control

  States:
  - IDLE    - fifo is empty, when it's not empty read 1 value and
              check if it's the header flit and change state to WAIT
  - WAIT    - waiting for resources because header flit came (no reading) waits
              for allocator to allocate resources
  - ACTIVE  - read the data when fifo is not empty, Tail flit that comes changes
              the state to idle because it deallocates the resources

  If header flit appears in a state other then IDLE there was a problem because
  there was an error

  Inputs:
  - FIFO signals so that the input channel can write data to it
  - CLK / RST (global signals)
  - Allocator INFO (channel resources grant!)

  Internal:
  - FIFO read signals
  - VIRTUAL CHANNEL STATE (IDLE, WAIT, ACTIVE)
  - HEADER reg (to store the HEADER)

  Outputs:
  - FIFO full output signal for the backward node (when it can send data)


  // TODO: Move Rd_en to a wire/combinatorial assignment because it is too slow
  // in reacting to empty_w

*/
`timescale 1ns / 1ps
// `include "../constants.v"
module virtual_channel
  # (
      `ifdef YS_VC_TOP
      parameter VC_DEPTH_W  = `YS_VC_DEPTH_W, // 4 flit buffer (for now)
      parameter DATA_W      = `YS_DATA_W,
      parameter ID_W        = `YS_ID_W
      `else
      parameter VC_DEPTH_W  = 2, // 4 flit buffer (for now)
      parameter DATA_W      = 10,
      parameter ID_W        = 2
      `endif
      )
    (
      input                 clk_i,
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

  // FSM
  localparam  IDLE    = 0; // no data in the FIFO
  localparam  WAITING = 1; // waiting for a channel
  localparam  ACTIVE  = 2; // sends the data over an allocated channel
  reg [$clog2(ACTIVE):0] fsm_state;

  reg [DATA_W-1:0] nxt_header_v, cur_header;
  reg rd_en_v, rd_en;

  // Wires
  wire empty_w;
  wire full_w;

  reg [$clog2(ACTIVE):0] cur_fsm_state;
  reg [$clog2(ACTIVE):0] nxt_fsm_state_v;

  // updater
  always @ ( posedge(clk_i), negedge(rst_ni) )begin
    if (!rst_ni)
    begin
      cur_fsm_state <= IDLE;
      cur_header    <= 0;
      rd_en         <= 0;
    end
    else begin
      cur_fsm_state <= nxt_fsm_state_v;
      cur_header    <= nxt_header_v;
      rd_en         <= rd_en_v;
    end
  end

  // Finite State Machine
  always @(*) begin
    nxt_fsm_state_v <= cur_fsm_state;
    case (cur_fsm_state)
      IDLE    : begin
                  // when do we switch from IDLE?
                  // when HEADER FLIT appeared on the data_o port
                  if (data_o[DATA_W-1: DATA_W-ID_W] == `HEADER_ID) begin
                    nxt_fsm_state_v <= WAITING;
                  end
                end
      WAITING : begin
                  if (chan_alloc_i && chan_rdy_i) begin
                    nxt_fsm_state_v <= ACTIVE;
                  end
                end
      ACTIVE  : begin
                  if (data_o[DATA_W-1: DATA_W-ID_W] == `TAIL_ID) begin
                    nxt_fsm_state_v <= IDLE;
                  end
                end
      default: nxt_fsm_state_v <= IDLE;
    endcase
  end

  // RD_EN & CURRENT_HEADER CONTROL
  always @ ( * ) begin
    rd_en_v       <= rd_en;
    nxt_header_v  <= cur_header;
    case (nxt_fsm_state_v)
      IDLE    : begin
                  if (!empty_w && !rd_en) rd_en_v <= 1'b1;
                  else                    rd_en_v <= 1'b0;
                  nxt_header_v  <= 0;
                end
      WAITING : begin
                  rd_en_v       <= 1'b0;
                  nxt_header_v  <= data_o;
                end
      ACTIVE  : begin
                  rd_en_v <= ~empty_w & chan_rdy_i;
                end
      default : begin
                  rd_en_v <= 1'b0;
                  nxt_header_v <= 0;
                end
    endcase
  end


  // always @ ( posedge(clk_i), negedge(rst_ni) )begin
  //   if (!rst_ni)
  //   begin
  //     fsm_state       <= IDLE;
  //     rd_en           <= 1'b0;
  //     cur_header  <= 0;
  //   end
  //   else begin
  //     case (fsm_state)
  //       IDLE    : begin
  //                   cur_header  <= 0;
  //                   if (data_o[DATA_W-1: DATA_W-ID_W] != `HEADER_ID) begin
  //                     fsm_state <= IDLE;
  //                     rd_en     <= 1'b0;
  //                     if (!empty_w && !rd_en) begin // when it's not empty and rd_en is not HIGH
  //                       rd_en <= 1'b1;
  //                     end
  //                   end
  //                   else begin
  //                     cur_header  <= data_o;
  //                     fsm_state       <= WAITING;
  //                     rd_en           <= 1'b0;
  //                   end
  //                 end
  //       WAITING : begin // wait for allocator to allocate channel
  //                   rd_en <= 1'b0;
  //                   if (chan_alloc_i && chan_rdy_i) begin
  //                     fsm_state <= ACTIVE;
  //                     rd_en     <= 1'b1;
  //                   end
  //                 end
  //       ACTIVE  : begin // Data should be read from the FIFO untill TAIL flit has arrived
  //                   rd_en <= ~empty_w & chan_rdy_i;
  //                   if (data_o[DATA_W-1: DATA_W-ID_W] == `TAIL_ID) begin
  //                     fsm_state       <= IDLE;
  //                     cur_header  <= 0;
  //                     rd_en           <= 1'b0;
  //                   end
  //                 end
  //       default : fsm_state <= IDLE;
  //     endcase
  //   end
  // end

  // Circular FIFO
  circ_fifo
    #(
      .DATA_W(DATA_W),
      .FIFO_DEPTH_W(VC_DEPTH_W)
      )
  buffer
    (
      .clk_i( clk_i ),
      .rst_ni( rst_ni ),
      .wr_en_i( wr_en_i ),
      .rd_en_i( rd_en_v ),
      .data_i( data_i ),
      .data_o( data_o ),
      .full_o( full_w ),
      .empty_o( empty_w )               // empty is used internally and indicates data to be routed
      );

  assign rdy_o      = ~full_w;
  assign header_o   = nxt_header_v; //cur_header;
  assign data_vld_o = rd_en;

  `ifdef FORMAL
    initial assume(!rst_ni); // inital RESET!

    always @(posedge(clk_i)) begin
      if (rst_ni) begin // RST not active

        assert(fsm_state == IDLE || fsm_state == WAITING || fsm_state == ACTIVE);

        if (fsm_state == WAITING) begin
          assert(rd_en == 1'b0);
        end
      end
    end
  `endif

endmodule // virtual_channel
