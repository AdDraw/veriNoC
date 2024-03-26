// Adam Drawc 2021-2024
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
  parameter HEADER_ID   = 2'b10,
  parameter TAIL_ID     = 2'b11,
  parameter FLIT_W      = FLIT_DATA_W + FLIT_ID_W
) (
  input  wire              clk_i,
  input  wire              rst_ni,
  // FIFO based input
  input  wire [FLIT_W-1:0] data_i,
  input  wire              wr_en_i,
  output wire              rdy_o,
  // Output Channel
  output wire [ OUT_M-1:0] oc_req_o,      // Output Channel Request
  output wire              oc_flit_id_is_tail_o,
  input  wire              oc_granted_i, // HEADER won the competition info
  output wire [FLIT_W-1:0] oc_data_o,
  output wire              oc_data_vld_o,
  input  wire              oc_rdy_i     // BUFFER on the other side is not full
);
  // FSM
  enum {
      IDLE,
      WAITING,
      ACTIVE
  } fsm_state, fsm_state_nxt;

  // Header
  reg  [ FLIT_ID_W-1:0] hdr_id;
  reg  [COL_ADDR_W-1:0] hdr_col_addr;
  reg  [ROW_ADDR_W-1:0] hdr_row_addr;

  reg  [ FLIT_ID_W-1:0] hdr_id_nxt;
  reg  [COL_ADDR_W-1:0] hdr_col_addr_nxt;
  reg  [ROW_ADDR_W-1:0] hdr_row_addr_nxt;

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
      fsm_state    <= IDLE;
      hdr_id       <= {FLIT_ID_W{1'b0}};
      hdr_col_addr <= {COL_ADDR_W{1'b0}};
      hdr_row_addr <= {ROW_ADDR_W{1'b0}};
      data_vld         <= 0;
    end else begin
      fsm_state    <= fsm_state_nxt;
      hdr_id       <= hdr_id_nxt;
      hdr_col_addr <= hdr_col_addr_nxt;
      hdr_row_addr <= hdr_row_addr_nxt;
      data_vld     <= data_vld_nxt;
    end
  end

  // Finite State Machine
  always @(*) begin : FSM_COMBO
    case (fsm_state)
      IDLE:
      if (data_w[FLIT_W-1-:FLIT_ID_W] == HEADER_ID) fsm_state_nxt <= WAITING;
      else fsm_state_nxt <= IDLE;
      WAITING:
      if (oc_granted_i && oc_rdy_i) fsm_state_nxt <= ACTIVE;
      else fsm_state_nxt <= WAITING;
      ACTIVE:
      if (data_w[FLIT_W-1-:FLIT_ID_W] == TAIL_ID && oc_rdy_i) fsm_state_nxt <= IDLE;
      else fsm_state_nxt <= ACTIVE;
      default: fsm_state_nxt <= IDLE;
    endcase
  end

  // RD_EN & CURRENT_HEADER CONTROL
  always @(*) begin : LOGIC_COMBO
    case (fsm_state_nxt)
      IDLE: begin
        rd_en_nxt          = ~empty_w & ~data_vld & !underflow_w;
        hdr_id_nxt       = hdr_id;
        hdr_col_addr_nxt = hdr_col_addr;
        hdr_row_addr_nxt = hdr_row_addr;
      end
      WAITING: begin
        rd_en_nxt          = 1'b0;
        hdr_id_nxt       = data_w[ROW_ADDR_W+COL_ADDR_W+:FLIT_ID_W];
        hdr_col_addr_nxt = data_w[ROW_ADDR_W+:COL_ADDR_W];
        hdr_row_addr_nxt = data_w[0+:ROW_ADDR_W];
      end
      ACTIVE: begin
        rd_en_nxt          = ~empty_w & oc_rdy_i & !underflow_w;
        hdr_id_nxt       = hdr_id;
        hdr_col_addr_nxt = hdr_col_addr;
        hdr_row_addr_nxt = hdr_row_addr;
      end
      default: begin
        rd_en_nxt          = 1'b0;
        hdr_id_nxt       = {FLIT_ID_W{1'b0}};
        hdr_col_addr_nxt = {COL_ADDR_W{1'b0}};
        hdr_row_addr_nxt = {ROW_ADDR_W{1'b0}};
      end
    endcase
  end

  always @(*) begin
    case (fsm_state)
      IDLE:    data_vld_nxt <= 1'b0;
      WAITING: data_vld_nxt <= 1'b1;
      ACTIVE:  if (!oc_rdy_i && data_vld) data_vld_nxt <= 1'b1;
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
    .rd_en_i    (rd_en_nxt),
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
    .col_addr_i(hdr_col_addr),
    .row_addr_i(hdr_row_addr),
    .oc_sel_o  (oc_req_o)
  );

  // Change routing to requests
  assign oc_data_o             = (fsm_state != IDLE) ? data_w : 0;
  assign rdy_o                 = ~full_w;
  assign oc_data_vld_o         = (oc_rdy_i) ? data_vld : 1'b0;
  assign oc_flit_id_is_tail_o  = (data_w[FLIT_W-1-:FLIT_ID_W] == TAIL_ID);

endmodule  // virtual_channel
