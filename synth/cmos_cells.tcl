yosys -import
set std_lib std_libs/osu18_std.lib
#read_liberty ~/opt/yosys/examples/cmos/cmos_cells.lib
read_liberty $std_lib

write_verilog ./cmos_cells.v
