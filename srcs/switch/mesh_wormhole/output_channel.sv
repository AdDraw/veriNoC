/*
  AdamDrawc@2024
  Combines the Allocator & Mux Nx1 as the Output Channel
*/
`default_nettype none
module output_channel #(
  parameter IN_N = 5,
  parameter ARB_TYPE = 0,
  parameter DATA_W = 10
)(
  input  wire clk_i,
  input  wire rst_ni,
  input  wire [IN_N-1:0] req_i,
  output wire [IN_N-1:0] grant_o,
  input  wire [IN_N-1:0] data_vld_i,
  input  wire [IN_N-1:0] flit_id_is_tail_i,
  input  wire oc_rdy_i,
  input  wire oc_vld_o,
  input  wire [IN_N-1:0][DATA_W-1:0] ic_data_i,
  output wire [DATA_W-1:0] oc_data_o
);

  wire [IN_N-1:0] mux_sel;

  allocator #(
    .IN_N       (IN_N),
    .ARB_TYPE   (ARB_TYPE)
  ) x_alloc (
    .clk_i             (clk_i),
    .rst_ni            (rst_ni),
    .req_i             (req_i),
    .grant_o           (mux_sel),
    .flit_id_is_tail_i (flit_id_is_tail_i),
    .oc_rdy_i          (oc_rdy_i),
    .data_vld_i        (data_vld_i),
    .oc_vld_o          (oc_vld_o)
  );

  mux_Nx1 # (
    .IN_N(IN_N),
    .DATA_W(DATA_W)
  ) x_mux_Nx1 (
    .data_i(ic_data_i),
    .sel_i(mux_sel),
    .data_o(oc_data_o)
  );


endmodule
`default_nettype wire