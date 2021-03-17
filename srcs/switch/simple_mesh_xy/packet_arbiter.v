`timescale 1ns / 1ps
module arbiter
# (
    parameter PORT_N = 5
    )
  (
    input [PORT_N - 1 : 0]         vld_input_i,
    output [$clog2(PORT_N)-1 : 0]  mux_in_sel_o
    );

    reg [$clog2(PORT_N)-1 : 0]  mux_in_sel_w;

    generate
      if (PORT_N == 5) begin
        always @(*)
        begin
          if (|vld_input_i)
          begin
            if (vld_input_i[4])
            begin
              mux_in_sel_w = 4;
            end

            else if ( vld_input_i[3])
            begin
              mux_in_sel_w = 3;
            end

            else if (vld_input_i[2])
            begin
              mux_in_sel_w = 2;
            end

            else if (vld_input_i[1])
            begin
              mux_in_sel_w = 1;
            end

            else if (vld_input_i[0])
            begin
              mux_in_sel_w = 0;
            end
            else
            begin
              mux_in_sel_w = 0;
            end
          end
        end
      end
      else if (PORT_N == 4) begin
        always @(*)
        begin
          if ( vld_input_i[3])
          begin
            mux_in_sel_w = 3;
          end

          else if (vld_input_i[2])
          begin
            mux_in_sel_w = 2;
          end

          else if (vld_input_i[1])
          begin
            mux_in_sel_w = 1;
          end

          else if (vld_input_i[0])
          begin
            mux_in_sel_w = 0;
          end
          else
          begin
            mux_in_sel_w = 0;
          end
        end
      end
      else if (PORT_N == 3) begin
        always @(*)
        begin
          if (|vld_input_i)
          begin
            if (vld_input_i[2])
            begin
              mux_in_sel_w = 2;
            end

            else if (vld_input_i[1])
            begin
              mux_in_sel_w = 1;
            end

            else if (vld_input_i[0])
            begin
              mux_in_sel_w = 0;
            end
            else
            begin
              mux_in_sel_w = 0;
            end
          end
        end
      end
    endgenerate

    assign mux_in_sel_o = mux_in_sel_w;

    `ifdef FORMAL
      always @(*) begin
          // Full & Empty checks
        if (PORT_N == 3) assert(mux_in_sel_i != 4 || mux_in_sel_i != 3);
        else if (PORT_N == 4) assert(mux_in_sel_i != 4);
      end
    `endif
endmodule
