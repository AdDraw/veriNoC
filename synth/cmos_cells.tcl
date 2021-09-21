yosys -import
#read_liberty ~/opt/yosys/examples/cmos/cmos_cells.lib
read_liberty osu18_std.lib

write_verilog ./cmos_cells.v
