module grant_with_carry (
  input  req_i,
  input  carry_i,
  output carry_o,
  output grant_o
);

  assign grant_o = ~carry_i & req_i;
  assign carry_o = carry_i | req_i;

endmodule
