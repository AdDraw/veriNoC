yosys -import
set std_lib $::env(STD_LIB)

read_liberty $std_lib

write_verilog ./cmos_cells.v
