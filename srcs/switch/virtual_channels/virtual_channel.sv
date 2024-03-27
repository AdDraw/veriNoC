// Adam Drawc 2021-2024
/*
  Description:
    Buffer + State that dictates how data should be read from the buffer

  Implemented as Circular FIFO + State & read control

  States:
  - IDLE    - fifo is empty, when it's not empty read 1 value and
              check if it's the header flit and change state to WAIT
  - WAIT    - REQUESTING for resources because header flit came (no reading) waits
              for allocator to allocate resources
  - GRANTED  - read the data when fifo is not empty, Tail flit that comes changes
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
  - VIRTUAL CHANNEL STATE (IDLE, WAIT, GRANTED)
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
      REQUESTING,
      GRANTED
  } fsm_state, fsm_state_nxt;

  // Header
  reg  [ FLIT_ID_W-1:0] hdr_id;
  reg  [COL_ADDR_W-1:0] hdr_col_addr;
  reg  [ROW_ADDR_W-1:0] hdr_row_addr;

  reg  [ FLIT_ID_W-1:0] hdr_id_nxt;
  reg  [COL_ADDR_W-1:0] hdr_col_addr_nxt;
  reg  [ROW_ADDR_W-1:0] hdr_row_addr_nxt;

  // Router
  wire [OUT_M-1:0] oc_req_w;

  // FIFO signals
  wire [    FLIT_W-1:0] data_w;
  wire                  empty_w;
  wire                  buffer_has_data_w = ~empty_w;
  wire                  full_w;
  wire                  underflow_w;
  reg                   rd_en_nxt;
  reg rd_en;

  // updater
  always_ff @(posedge clk_i or negedge rst_ni) begin : SYNC_UPDATE
    if (!rst_ni) begin
      fsm_state    <= IDLE;
      hdr_id       <= {FLIT_ID_W{1'b0}};
      hdr_col_addr <= {COL_ADDR_W{1'b0}};
      hdr_row_addr <= {ROW_ADDR_W{1'b0}};
    end else begin
      fsm_state    <= fsm_state_nxt;
      hdr_id       <= hdr_id_nxt;
      hdr_col_addr <= hdr_col_addr_nxt;
      hdr_row_addr <= hdr_row_addr_nxt;
      rd_en        <= rd_en_nxt;
    end
  end

  // Finite State Machine
  always @(*) begin
    fsm_state_nxt = IDLE;
    case (fsm_state)
      IDLE:
      if (buffer_has_data_w) fsm_state_nxt = REQUESTING;
      else                   fsm_state_nxt = IDLE;
      REQUESTING:
      if (oc_granted_i && oc_rdy_i) fsm_state_nxt = GRANTED;
      else                          fsm_state_nxt = REQUESTING;
      GRANTED:
      if (data_w[FLIT_W-1-:FLIT_ID_W] == TAIL_ID && oc_rdy_i) fsm_state_nxt = IDLE;
      else                                                    fsm_state_nxt = GRANTED;
    endcase
  end

  // RD_EN & CURRENT_HEADER CONTROL
  always @(*) begin
    rd_en_nxt        = 1'b0;
    hdr_id_nxt       = {FLIT_ID_W{1'b0}};
    hdr_col_addr_nxt = {COL_ADDR_W{1'b0}};
    hdr_row_addr_nxt = {ROW_ADDR_W{1'b0}};
    case (fsm_state)
      IDLE: begin
        rd_en_nxt        = buffer_has_data_w & !underflow_w;
        hdr_id_nxt       = data_w[FLIT_W-1-:FLIT_ID_W];
        hdr_row_addr_nxt = data_w[FLIT_W-FLIT_ID_W-1-:ROW_ADDR_W];
        hdr_col_addr_nxt = data_w[FLIT_W-FLIT_ID_W-ROW_ADDR_W-1-:COL_ADDR_W];
      end
      REQUESTING: begin
        rd_en_nxt        = 1'b0;
        hdr_id_nxt       = data_w[FLIT_W-1-:FLIT_ID_W];
        hdr_row_addr_nxt = data_w[FLIT_W-FLIT_ID_W-1-:ROW_ADDR_W];
        hdr_col_addr_nxt = data_w[FLIT_W-FLIT_ID_W-ROW_ADDR_W-1-:COL_ADDR_W];
      end
      GRANTED: begin
        rd_en_nxt        = ~oc_flit_id_is_tail_o & buffer_has_data_w & oc_rdy_i & !underflow_w;
        hdr_id_nxt       = hdr_id;
        hdr_col_addr_nxt = hdr_col_addr;
        hdr_row_addr_nxt = hdr_row_addr;
      end
    endcase
  end

  // Circular FIFO
  circ_fifo #(
    .DATA_W      (FLIT_W),
    .FIFO_DEPTH_W(VC_DEPTH_W)
  ) buffer (
    .clk_i      (clk_i),
    .rst_ni     (rst_ni),
    .wr_en_i    (wr_en_i & ~full_w),
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
    .col_addr_i(hdr_col_addr_nxt),
    .row_addr_i(hdr_row_addr_nxt),
    .oc_sel_o  (oc_req_w)
  );

  // Change routing to requests
  assign oc_data_o             = (fsm_state == GRANTED) ? data_w : {FLIT_W{1'b0}};
  assign rdy_o                 = ~full_w;
  assign oc_req_o              = (fsm_state == REQUESTING) ? oc_req_w : {OUT_M{1'b0}};
  assign oc_data_vld_o         = (oc_rdy_i & fsm_state == GRANTED);
  assign oc_flit_id_is_tail_o  = (data_w[FLIT_W-1-:FLIT_ID_W] == TAIL_ID) & oc_granted_i;

endmodule  // virtual_channel
