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

*/
`timescale 1ns / 1ps
`define FLIT_W (FLIT_DATA_W+FLIT_ID_W)
`define FLIT_ID_RANGE `FLIT_W-1:`FLIT_W-FLIT_ID_W
module virtual_channel
  # (
      `ifdef YS_VC_TOP
      parameter VC_DEPTH_W  = `YS_VC_DEPTH_W, // 4 flit buffer (for now)
      parameter FLIT_DATA_W = `YS_FLIT_DATA_W,
      parameter FLIT_ID_W   = `YS_FLIT_ID_W
      `else
      parameter VC_DEPTH_W  = 2, // 4 flit buffer (for now)
      parameter FLIT_DATA_W = 8,
      parameter FLIT_ID_W   = 2
      `endif
      )
    (
      input                 clk_i,
      input                 rst_ni,

      // FIFO based input (data & wr_enable)
      input   [`FLIT_W-1:0] data_i,
      input                 wr_en_i,

      // Allocator info input
      input                 chan_alloc_i, // HEADER won the competition info
      input                 chan_rdy_i,   // BUFFER on the other side is not full

      // To Route
      output  [`FLIT_W-1:0] data_o,
      output                data_vld_o,
      output  [`FLIT_W-1:0] header_o,

      // FIFO based output
      output                rdy_o,         // backpressure signal
      output                overflow_o
      );

  // FSM
  localparam  FSM_SIZE  = 3;
  localparam  IDLE      = 3'b001; // no data in the FIFO
  localparam  WAITING   = 3'b010; // waiting for a channel
  localparam  ACTIVE    = 3'b100; // sends the data over an allocated channel
  reg [FSM_SIZE-1:0]  cur_fsm_state;
  reg [FSM_SIZE-1:0]  nxt_fsm_state_v;

  // Header
  reg [`FLIT_W-1:0]   nxt_header_v, cur_header;
  // FIFO signals
  wire [`FLIT_W-1:0]  data_w;
  wire                empty_w;
  wire                full_w;
  wire                underflow_w;
  reg                 rd_en_v, rd_en;

  // updater
  always @ ( posedge(clk_i) or negedge(rst_ni))
  begin: SYNC_UPDATE
    if (!rst_ni) begin
      cur_fsm_state <= IDLE;
      cur_header    <= 0;
      rd_en         <= 1'b0;
    end
    else begin
      cur_fsm_state <= nxt_fsm_state_v;
      cur_header    <= nxt_header_v;
      rd_en         <= rd_en_v;
    end
  end

  // Finite State Machine
  always @( * )
  begin: FSM_COMBO
    nxt_fsm_state_v <= cur_fsm_state;
    case (cur_fsm_state)
      IDLE    : if (data_w[`FLIT_ID_RANGE] == `HEADER_ID) nxt_fsm_state_v <= WAITING;
      WAITING : if (chan_alloc_i && chan_rdy_i)           nxt_fsm_state_v <= ACTIVE;
      ACTIVE  : if (data_w[`FLIT_ID_RANGE] == `TAIL_ID)   nxt_fsm_state_v <= IDLE;
      default :                                           nxt_fsm_state_v <= IDLE;
    endcase
  end

  // RD_EN & CURRENT_HEADER CONTROL
  always @ ( * )
  begin: LOGIC_COMBO
    case (nxt_fsm_state_v)
      IDLE    : begin
                  rd_en_v       <= ~empty_w & ~rd_en & !underflow_w;
                  nxt_header_v  <= 0;
                end
      WAITING : begin
                  rd_en_v       <= 1'b0;
                  nxt_header_v  <= data_w;
                end
      ACTIVE  : begin
                  rd_en_v       <= ~empty_w & chan_rdy_i & !underflow_w;
                  nxt_header_v  <= cur_header;
                end
      default : begin
                  rd_en_v      <= 1'b0;
                  nxt_header_v <= 0;
                end
    endcase
  end

  // Circular FIFO
  circ_fifo
    #(
      .DATA_W(`FLIT_W),
      .FIFO_DEPTH_W(VC_DEPTH_W)
      )
  buffer
    (
      .clk_i( clk_i ),
      .rst_ni( rst_ni ),
      .wr_en_i( wr_en_i ),
      .rd_en_i( rd_en_v ),
      .data_i( data_i ),
      .data_o( data_w ),
      .full_o( full_w ),
      .empty_o( empty_w ),
      .underflow_o( underflow_w ),
      .overflow_o( overflow_o )
      );

  assign data_o     = data_w;
  assign rdy_o      = ~full_w;
  assign header_o   = nxt_header_v; //cur_header;
  assign data_vld_o = rd_en;

  // `ifdef FORMAL
  //   initial assume(!rst_ni); // inital RESET!
  //
  //   always @(posedge(clk_i)) begin
  //     if (rst_ni) begin // RST not active
  //
  //       assert(fsm_state == IDLE || fsm_state == WAITING || fsm_state == ACTIVE);
  //
  //       if (fsm_state == WAITING) begin
  //         assert(rd_en == 1'b0);
  //       end
  //     end
  //   end
  // `endif

endmodule // virtual_channel
