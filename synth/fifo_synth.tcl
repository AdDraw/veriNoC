yosys -import

set top_module fifo
# Set parameter values (values taken from EnvVars set by yosys_wrapper.sh)
set params(0) FIFO_DEPTH_WIDTH
set params(1) DATA_WIDTH

#default values for synth
set values(0) 4
set values(1) 8

chparam -list
for { set index 0 }  { $index < [array size params] }  { incr index } {
   log "params($index) : $params($index)"
   if { [info exists ::env($params($index))] } {
     set values($index) $::env($params($index))
   }
}

read_verilog  -DYS_FIFO_TOP=1 \
              -DYS_$params(0)=$values(0) \
              -DYS_$params(1)=$values(1) \
              ../srcs/components/fifo.v

# elaborate design hierarchy
hierarchy -check -top $top_module

# the high-level stuff
procs; opt; fsm; opt; memory; opt

# mapping to internal cell library
techmap; opt

# cleanup
clean

show  -enum -width -colors 3 $top_module
json -o $::env(JSON_PATH)/$top_module-.json
write_verilog ../srcs/components/fifo_synth.v
