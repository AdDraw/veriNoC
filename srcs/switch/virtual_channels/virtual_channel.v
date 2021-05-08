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
module virtual_channel
  # (
      `ifdef YS_VC_TOP
      parameter FIFO_DEPTH_W  = `YS_FIFO_DEPTH_W, // 4 flit buffer (for now)
      parameter DATA_W        = `YS_DATA_W,
      parameter ID_W          = `YS_ID_W
      `else
      parameter FIFO_DEPTH_W  = 2, // 4 flit buffer (for now)
      parameter DATA_W        = 10,
      parameter ID_W          = 2
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

      // FIFO based output
      output                rdy_o         // backpressure signal
      );

  // FSM
  localparam  IDLE    = 0; // no data in the FIFO
  localparam  WAITING = 1; // waiting for a channel
  localparam  ACTIVE  = 2; // sends the data over an allocated channel
  reg [$clog2(ACTIVE):0] fsm_state;

  reg [DATA_W-1:0] current_header;
  reg rd_en;

  // Wires
  wire empty_w;
  wire full_w;

  always @ ( posedge(clk_i), negedge(rst_ni) )begin
    if (!rst_ni)
    begin
      fsm_state       <= IDLE;
      rd_en           <= 1'b0;
      current_header  <= 0;
    end
    else begin
      case (fsm_state)
        IDLE    : begin
                    current_header <= 0;
                    rd_en <= 1'b0;
                    if (!empty_w && !rd_en) begin // when it's not empty and rd_en is not HIGH
                      rd_en <= 1'b1;
                    end
                    else begin
                      if (data_o[DATA_W-1: DATA_W-ID_W] == `HEADER_ID) begin
                        current_header  <= data_o;
                        fsm_state       <= WAITING;
                        rd_en           <= 1'b0;
                      end
                      else begin
                        fsm_state <= IDLE; //in case of problem drop this signal
                      end
                    end
                  end
        WAITING : begin // wait for allocator to allocate channel
                    rd_en <= 1'b0;
                    if (chan_alloc_i && chan_rdy_i) begin
                      fsm_state <= ACTIVE;
                      rd_en     <= 1'b1;
                    end
                  end
        ACTIVE  : begin // Data should be read from the FIFO untill TAIL flit has arrived
                    rd_en <= !empty_w & chan_rdy_i;
                    if (data_o[DATA_W-1: DATA_W-ID_W] == `TAIL_ID) begin
                      fsm_state       <= IDLE;
                      current_header  <= 0;
                      rd_en           <= 1'b0;
                    end
                  end
        default : fsm_state <= IDLE;
      endcase
    end
  end

  // Circular FIFO
  circ_fifo
    #(
      .DATA_W(DATA_W),
      .FIFO_DEPTH_W(FIFO_DEPTH_W)
      )
  buffer
    (
      .clk_i( clk_i ),
      .rst_ni( rst_ni ),
      .wr_en_i( wr_en_i ),
      .rd_en_i( rd_en ),
      .data_i( data_i ),
      .data_o( data_o ),
      .full_o( full_w ),
      .empty_o( empty_w )               // empty is used internally and indicates data to be routed
      );

  assign rdy_o = ~full_w;

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
