yosys -import
read_liberty ~/opt/yosys/examples/cmos/cmos_cells.lib

write_verilog ./cmos_cells.v
