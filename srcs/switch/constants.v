// Flit IDs
`define HEADER_ID 2'b10
`define PAYLOAD_ID 2'b01
`define TAIL_ID 2'b11

// helper defines
`define FLIT_W (FLIT_ID_W+FLIT_DATA_W)
`define FLIT_ID_RANGE `FLIT_W-1:`FLIT_W-FLIT_ID_W
`define ROW_ADDR_RANGE (`FLIT_W-FLIT_ID_W)-1 : (`FLIT_W - FLIT_ID_W - ROW_ADDR_W)
`define COL_ADDR_RANGE (`FLIT_W - FLIT_ID_W - ROW_ADDR_W) -1 : (`FLIT_W - FLIT_ID_W - ROW_ADDR_W - COL_ADDR_W)
// `define UNPACK(i, w) (w*(i+1))-1:(w*i)
`define CHAN_SEL_W $clog2(IN_N)
`define RTR_RES_W $clog2(OUT_M)
`define CALC_DATA_RANGE(i) `FLIT_W*(i+1)-1:`FLIT_W*i
