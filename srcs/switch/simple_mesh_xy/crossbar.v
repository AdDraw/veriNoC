`define N_WIDTH 3

module n_to_n_crossbar
# (
    parameter DATA_WIDTH = 8,
    parameter PORT_N = 5
    )
  (
    input   [(PORT_N * DATA_WIDTH) - 1 : 0] data_i,
    input   [`N_WIDTH - 1 : 0] mux_in_sel_i,

    input clk_i,
    input rst_ni,
    input   [PORT_N - 1 : 0] vld_output_i,
    input   [`N_WIDTH - 1 : 0] mux_out_sel_i,

    output  [DATA_WIDTH - 1 : 0] pckt_in_chosen_o,
    output  [(PORT_N * DATA_WIDTH) - 1 : 0] data_o
    );

    reg [DATA_WIDTH - 1 : 0] mux_out_data_v [PORT_N - 1 : 0];
    reg [DATA_WIDTH - 1 : 0] mux_in_data_chosen_w;

    // INPUT MUX
    always @(*)
    begin
      case (mux_in_sel_i)
      `N_WIDTH'd0: mux_in_data_chosen_w = data_i[DATA_WIDTH - 1 : 0];
      `N_WIDTH'd1: mux_in_data_chosen_w = data_i[DATA_WIDTH*2 - 1 : DATA_WIDTH];
      `N_WIDTH'd2: mux_in_data_chosen_w = data_i[DATA_WIDTH*3 - 1 : DATA_WIDTH*2];
      `N_WIDTH'd3: mux_in_data_chosen_w = data_i[DATA_WIDTH*4 - 1 : DATA_WIDTH*3];
      `N_WIDTH'd4: mux_in_data_chosen_w = data_i[DATA_WIDTH*5 - 1 : DATA_WIDTH*4];
      default: mux_in_data_chosen_w = 0;
      endcase
    end

    // OUTPUT MUX, regged
    always @(posedge clk_i or negedge rst_ni)
    begin
      if (!rst_ni)
      begin
          for (i=0; i < 2**`N_WIDTH; i=i+1)
          begin
            mux_out_data_v[i] <= 0;
          end
      end
      else
      begin
        if (!vld_output_i[mux_out_sel_i]) // if the specified output is not vld then it's ok to write data to it :) if not then wait
        begin
          case (mux_out_sel_i)
            `N_WIDTH'd0: mux_out_data_v[0] <= mux_in_data_chosen_w;
            `N_WIDTH'd1: mux_out_data_v[1] <= mux_in_data_chosen_w;
            `N_WIDTH'd2: mux_out_data_v[2] <= mux_in_data_chosen_w;
            `N_WIDTH'd3: mux_out_data_v[3] <= mux_in_data_chosen_w;
            `N_WIDTH'd4: mux_out_data_v[4] <= mux_in_data_chosen_w;
            default: mux_out_data_v[0] <= 0;
          endcase
        end
      end
    end

    genvar i;
    generate
      for( i = 0; i < PORT_N; i = i + 1)
      begin
        assign data_o[DATA_WIDTH*(i+1) - 1 : DATA_WIDTH*i] = mux_out_data_v[i];
      end
    endgenerate

    assign pckt_in_chosen_o = mux_in_data_chosen_w; 

endmodule
