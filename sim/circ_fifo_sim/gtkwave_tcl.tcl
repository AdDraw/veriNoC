set def [list]
lappend def "top.fifo.clk_i"
lappend def "top.fifo.rst_ni"
lappend def "top.fifo.data_i"
lappend def "top.fifo.wr_en_i"
lappend def "top.fifo.rd_en_i"
lappend def "top.fifo.empty_o"
lappend def "top.fifo.full_o"
lappend def "top.fifo.underflow_o"
lappend def "top.fifo.overflow_o"
lappend def "top.fifo.wr_ptr_v"
lappend def "top.fifo.rd_ptr_v"
lappend def "top.fifo.data_o"
for {set i 0} {$i < 10} {incr i} {

   puts "$i"
   lappend def "top.fifo.fifo_v($i)"
}

puts "$def"

set num_added [gtkwave::addSignalsFromList $def]

puts "added waves"
