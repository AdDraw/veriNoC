module arbiter
# (
    parameter PORT_N = 5
    )
  (
    input [PORT_N - 1 : 0]         vld_input_i,
    output [$clog2(PORT_N)-1 : 0]  mux_in_sel_o
    );

    localparam RESOURCE = 0;
    localparam WEST     = 1;
    localparam EAST     = 2;
    localparam NORTH    = 3;
    localparam SOUTH    = 4;

    reg [$clog2(PORT_N)-1 : 0]  mux_in_sel_w;
    // Vertical priority
    // N > S > E > W > R
    always @(*)
    begin
      if (|vld_input_i)
      begin
        if (vld_input_i[NORTH])
        begin
          // TOP is valid
          // choose top packet
          mux_in_sel_w = NORTH;
        end

        else if ( vld_input_i[SOUTH])
        begin
          mux_in_sel_w = SOUTH;
        end

        else if (vld_input_i[EAST])
        begin
          mux_in_sel_w = EAST;
        end

        else if (vld_input_i[WEST])
        begin
          mux_in_sel_w = WEST;
        end

        else if (vld_input_i[RESOURCE])
        begin
          mux_in_sel_w = RESOURCE;
        end
        else
        begin
          mux_in_sel_w = 0;
        end
      end
    end

    assign mux_in_sel_o = mux_in_sel_w;

endmodule
