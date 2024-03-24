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
              sends the data over an allocated channel

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
module virtual_channel #(
  parameter VC_DEPTH_W  = 2,
  parameter FLIT_DATA_W = 8,
  parameter COL_CORD    = 1,
  parameter FLIT_ID_W   = 2,
  parameter ROW_CORD    = 1,
  parameter OUT_M       = 5,
  parameter COL_ADDR_W  = 2,
  parameter ROW_ADDR_W  = 2,
  parameter HEADER_ID   = 0,
  parameter TAIL_ID     = 0,
  parameter FLIT_W      = 0
) (
  input                clk_i,
  input                rst_ni,
  // FIFO based input (data & wr_enable)
  input  [ FLIT_W-1:0] data_i,
  input                wr_en_i,
  // Allocator info input
  input                chan_alloc_i,     // HEADER won the competition info
  input                chan_rdy_i,       // BUFFER on the other side is not full
  // To Route
  output [ FLIT_W-1:0] data_o,
  output               data_vld_o,
  output [OUT_M-1:0]   req_o,
  // FIFO based output
  output               rdy_o             // backpressure signal
);

  // FSM
  localparam FSM_SIZE = 3;
  localparam IDLE = 3'b001;
  localparam WAITING = 3'b010;
  localparam ACTIVE = 3'b100;
  reg  [  FSM_SIZE-1:0] cur_fsm_state;
  reg  [  FSM_SIZE-1:0] nxt_fsm_state;

  // Header
  reg  [ FLIT_ID_W-1:0] cur_hdr_id;
  reg  [COL_ADDR_W-1:0] cur_hdr_col_addr;
  reg  [ROW_ADDR_W-1:0] cur_hdr_row_addr;

  reg  [ FLIT_ID_W-1:0] nxt_hdr_id;
  reg  [COL_ADDR_W-1:0] nxt_hdr_col_addr;
  reg  [ROW_ADDR_W-1:0] nxt_hdr_row_addr;

  // FIFO signals
  wire [    FLIT_W-1:0] data_w;
  wire                  empty_w;
  wire                  full_w;
  wire                  underflow_w;
  reg                   rd_en_nxt;
  reg                   data_vld;
  reg                   data_vld_nxt;

  // updater
  always @(posedge clk_i or negedge rst_ni) begin : SYNC_UPDATE
    if (!rst_ni) begin
      cur_fsm_state    <= IDLE;
      cur_hdr_id       <= {FLIT_ID_W{1'b0}};
      cur_hdr_col_addr <= {COL_ADDR_W{1'b0}};
      cur_hdr_row_addr <= {ROW_ADDR_W{1'b0}};
      data_vld         <= 0;
    end else begin
      cur_fsm_state    <= nxt_fsm_state;
      cur_hdr_id       <= nxt_hdr_id;
      cur_hdr_col_addr <= nxt_hdr_col_addr;
      cur_hdr_row_addr <= nxt_hdr_row_addr;
      data_vld         <= data_vld_nxt;
    end
  end

  // Finite State Machine
  always @(*) begin : FSM_COMBO
    case (cur_fsm_state)
      IDLE:
      if (data_w[FLIT_W-:FLIT_ID_W] == HEADER_ID) nxt_fsm_state <= WAITING;
      else nxt_fsm_state <= IDLE;
      WAITING:
      if (chan_alloc_i && chan_rdy_i) nxt_fsm_state <= ACTIVE;
      else nxt_fsm_state <= WAITING;
      ACTIVE:
      if (data_w[FLIT_W-:FLIT_ID_W] == TAIL_ID && chan_rdy_i) nxt_fsm_state <= IDLE;
      else nxt_fsm_state <= ACTIVE;
      default: nxt_fsm_state <= IDLE;
    endcase
  end

  // RD_EN & CURRENT_HEADER CONTROL
  always @(*) begin : LOGIC_COMBO
    case (nxt_fsm_state)
      IDLE: begin
        rd_en_nxt          = ~empty_w & ~data_vld & !underflow_w;
        nxt_hdr_id       = cur_hdr_id;
        nxt_hdr_col_addr = cur_hdr_col_addr;
        nxt_hdr_row_addr = cur_hdr_row_addr;
      end
      WAITING: begin
        rd_en_nxt          = 1'b0;
        nxt_hdr_id       = data_w[ROW_ADDR_W+COL_ADDR_W+:FLIT_ID_W];
        nxt_hdr_col_addr = data_w[ROW_ADDR_W+:COL_ADDR_W];
        nxt_hdr_row_addr = data_w[0+:ROW_ADDR_W];
      end
      ACTIVE: begin
        rd_en_nxt          = ~empty_w & chan_rdy_i & !underflow_w;
        nxt_hdr_id       = cur_hdr_id;
        nxt_hdr_col_addr = cur_hdr_col_addr;
        nxt_hdr_row_addr = cur_hdr_row_addr;
      end
      default: begin
        rd_en_nxt          = 1'b0;
        nxt_hdr_id       = {FLIT_ID_W{1'b0}};
        nxt_hdr_col_addr = {COL_ADDR_W{1'b0}};
        nxt_hdr_row_addr = {ROW_ADDR_W{1'b0}};
      end
    endcase
  end

  always @(*) begin
    case (cur_fsm_state)
      IDLE:    data_vld_nxt <= 1'b0;
      WAITING: data_vld_nxt <= 1'b1;
      ACTIVE:  if (!chan_rdy_i && data_vld) data_vld_nxt <= 1'b1;
               else data_vld_nxt <= rd_en_nxt;
      default: data_vld_nxt <= 0;
    endcase
  end

  // Circular FIFO
  circ_fifo #(
    .DATA_W      (FLIT_W),
    .FIFO_DEPTH_W(VC_DEPTH_W)
  ) buffer (
    .clk_i      (clk_i),
    .rst_ni     (rst_ni),
    .wr_en_i    (wr_en_i),
    .rd_en_i    (rd_en_v),
    .data_i     (data_i),
    .data_o     (data_w),
    .full_o     (full_w),
    .empty_o    (empty_w),
    .underflow_o(underflow_w),
    .overflow_o ()
  );

  // ROUTER per VC
  xy_router #(
    .COL_CORD  (COL_CORD),
    .ROW_CORD  (ROW_CORD),
    .COL_ADDR_W(COL_ADDR_W),
    .ROW_ADDR_W(ROW_ADDR_W),
    .OUT_M     (OUT_M)
  ) x_router (
    .col_addr_i(cur_hdr_col_addr),
    .row_addr_i(cur_hdr_row_addr),
    .oc_sel_o  (req_o)
  );

  // Change routing to requests
  assign data_o          = (cur_fsm_state != IDLE) ? data_w : 0;
  assign rdy_o           = ~full_w;
  assign route_res_vld_o = (cur_fsm_state == WAITING) ? 1'b1 : 1'b0;
  assign data_vld_o      = (chan_rdy_i) ? data_vld : 1'b0;

endmodule  // virtual_channel
