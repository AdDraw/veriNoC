export PYTHON_BIN=/usr/bin/python3
export SHELL=/bin/bash

export TOPLEVEL_LANG ?= verilog
VER_DIR=$(shell pwd)/../../srcs/switch/simple_mesh_xy

# files
VERILOG_SOURCES += $(VER_DIR)/xy_switch.v
VERILOG_SOURCES += $(VER_DIR)/control_unit.v
VERILOG_SOURCES += $(VER_DIR)/packet_arbiter.v
VERILOG_SOURCES += $(VER_DIR)/crossbar.v
VERILOG_SOURCES += $(VER_DIR)/router_xy.v
VERILOG_SOURCES += $(VER_DIR)/../../components/fifo.v

# Specifies essentials of the DUT and the cocotb TB
TOPLEVEL := xy_switch
MODULE   := test
SIM ?= verilator

# PACKET
export PCKT_XADDR_W ?= "2"
export PCKT_YADDR_W	?= "2"
export PCKT_DATA_W 	?= "8"

__PCKT_W = PCKT_XADDR_W + PCKT_YADDR_W + PCKT_DATA_W
export PCKT_W			?= "$(__PCKT_W)"

# SWITCH
export PORT_N		 	?= "4"
export X_CORD			?= "2"
export Y_CORD			?= "2"
export IN_FIFO_DEPTH_W  ?= "3" # FIFO_DEPTH = 2^$(IN_FIFO_DEPTH_W)

ifeq ($(SIM), verilator)
		COCOTB_HDL_TIMEUNIT = 1ns
		COCOTB_HDL_TIMEPRECISION = 1ps
		# Trace dump
		EXTRA_ARGS += --trace --trace-structs
		COMPILE_ARGS += -O3
		EXTRA_ARGS += -GPORT_N=$(PORT_N)
		EXTRA_ARGS += -GX_CORD=$(X_CORD)
		EXTRA_ARGS += -GY_CORD=$(Y_CORD)
		EXTRA_ARGS += -GPCKT_W=$(PACKET_W)
		EXTRA_ARGS += -GPCKT_XADDR_W=$(PACKET_X_ADDR_W)
		EXTRA_ARGS += -GPCKT_YADDR_W=$(PACKET_Y_ADDR_W)
		EXTRA_ARGS += -GPCKT_DATA_W=$(PACKET_DATA_W)
		EXTRA_ARGS += -GIN_FIFO_DEPTH_W=$(IN_FIFO_DEPTH_W)
endif

#ifeq ($(SIM), icarus)
#		EXTRA_ARGS += -PDATA_WIDTH=$(DATA_WIDTH)
#		EXTRA_ARGS += -PFIFO_DEPTH_WIDTH=$(FIFO_DEPTH_WIDTH)
## 		EXTRA_ARGS += -PALMOST_FULL_LEVEL=$(ALMOST_FULL_LEVEL)
## 		EXTRA_ARGS += -PALMOST_EMPTY_LEVEL=$(ALMOST_EMPTY_LEVEL)
#endif

include $(shell cocotb-config --makefiles)/Makefile.sim
