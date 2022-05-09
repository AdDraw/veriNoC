/*
  Adam Drawc @2021
  Description:
  Arbiter that uses round_robin arbitration.
  Provides STRONG Fairness over time

  When request has been served it lands on the end of the que

  for every req, first to show up is the first one to be granted
  after grant, agent that got it moves to the bottom of the que
  every other agent moves up
  what if the initial state is uknown and at the same time, 2 req come
  then you choose the one with a smaller symbol

  BIG logic implementation
  if it's a round-robin we could do a que
  you number each input, and then with each grant you place the number corresponding to the granted input at the bottom of the que (LEFT shift & last granted number)

  Initial state, no history, que is blank
  first contender, you fill the que, at this point, whoever is not in the que has priority
  next contender comes, if he is not in the que, he gets priority aka grant
  etc etc
  que gets filled
  now if any grant comes, we have a known priority of grants!
  but still, let's assume, that at first que is initialized in an increasing order 
  this already gives us a bit of knowledge and we don't need to guess /fill the priority list
  then if 2 inputs come then we already know whch one should go first!

  Eventually you get to a point that
  in 0 and 3 want access
  now you need to decide which input will be granted  the access
  you have 2 things, your inputs, your table of priority

  each input here gets a numerical priority
  if 2 inputs come the one with the biggest priority should get access
  after that we could simply update priorities of everybody (add 1, lshift)

  priority depicted as the spot in the que
  each spot knows it's input id
  if we have our que, then every cycle we could 
  1. see if there are requests
  2. going from the start of the que, check which inputs are HIGH
  3. as soon as we decide which input currently holds the highest priority
  4. we look at his index, and we only shift up to his index, placing him at the end
  
  this sounds like a lot of dynamic stuff
  1. you either add / subtract  depending on the grant
  2. figure out who to move and do that

  reg [$clog2(IN_N)-1:0] last_grant, new_grant;
  reg [$clog2(IN_N)-1:0] p_que [IN_N-1 : 0];

*/
`timescale 1ns / 1ps

module round_robin_arb
  #(
    parameter IN_N = 5 // this should be 5 right now
    )
  (
    input                  clk_i,
    input                  rst_ni,
    input   [IN_N - 1 : 0] req_i,
    output  [IN_N - 1 : 0] grant_o
  );

  // Last granted requested moves to the end of the que
  reg [IN_N -1 : 0] grant;

  wire [IN_N-1 :0] new_p_table [IN_N-1 : 0];
  reg [IN_N-1 :0] p_table [IN_N-1 : 0];
  always @(posedge clk_i or negedge rst_ni) begin
    if (!rst_ni) begin
      for (integer i = 0; i < IN_N; i=i+1 ) begin
        p_table[i] <= 1 << i;
      end
    end
    else begin
      
    end
  end

  genvar i;
  generate
    wire [IN_N : 0] c_grant;
    
    assign c_grant[0] = 1'b0;
    for (i = 0; i < IN_N; i = i + 1) begin
      if (i == 0) begin
        granter_with_shifitng_p #(
          .REQ_N(IN_N),
          .INITIAL_PRIORITY( 1)
        ) x_grant (
          .clk_i      (clk_i),
          .rst_ni     (rst_ni),
          .c_grant_i  (c_grant[i]),
          .c_grant_o  (c_grant[i+1]),
          .ext_p_val_i(p_table[i]),
          .grant_o    (grant[i])
          .p_val_o    (),
        );
      end
      else if (i == IN_N - 1) begin
        granter_with_shifitng_p #(
          .REQ_N(IN_N),
          .INITIAL_PRIORITY( 1 << i)
        ) x_grant (
          .clk_i      (clk_i),
          .rst_ni     (rst_ni),
          .c_grant_i  (c_grant[i]),
          .c_grant_o  (c_grant[IN_N]),
          .ext_p_val_i(p_table[i]),
          .grant_o    (grant[i])
          .p_val_o    (),
        );
      end
      else begin
        granter_with_shifitng_p #(
          .REQ_N(IN_N),
          .INITIAL_PRIORITY(IN_N)
        ) x_grant (
          .clk_i      (clk_i),
          .rst_ni     (rst_ni),
          .c_grant_i  (c_grant[i]),
          .c_grant_o  (c_grant[i+1]),
          .ext_p_val_i(p_table[i]),
          .grant_o    (grant[i])
          .p_val_o    (new_p_table[i+1]),
        );
      end
    end
  endgenerate
endmodule // round_robin_arb

module granter_with_shifitng_p  #(
  parameter REQ_N = 5,
  parameter INITIAL_PRIORITY = 5'b00001 // has to be onehot
) (
  input               rst_ni,
  input               clk_i,
  input  [REQ_N-1: 0] req_i,
  input               c_grant_i,
  output              c_grant_o,
  input  [REQ_N-1 :0] ext_p_val_i,
  output [REQ_N-1:0]  p_val_o,
  output              grant_o
);

  reg [REQ_N-1:0] cur_p_val;
  reg [REQ_N-1:0] p_val;
  assign c_grant_o = c_grant_i | grant_o;
  assign grant_o   = (c_grant_i == 1'b0) ? |(req_i && cur_p_val): 1'b0; 

  always @(posedge clk_i or negedge rst_ni) begin
    if (rst_ni == 1'b0) begin
      cur_p_val <= INITIAL_PRIORITY; 
      p_val     <= INITIAL_PRIORITY;
    end
    else begin
      if (c_grant_o == 1'b1) begin
        cur_p_val <= ext_p_val_i;
        p_val   <= cur_p_val;
      end
    end
  end

  assign p_val_o = p_val;

endmodule
