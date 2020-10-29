export PYTHON_BIN=/usr/bin/python3
export SHELL=/bin/bash

export TOPLEVEL_LANG ?= verilog
VER_DIR=$(shell pwd)/../../srcs/switch/simple_mesh_xy

# files
VERILOG_SOURCES= $(VER_DIR)/xy_switch.v

# Specifies essentials of the DUT and the cocotb TB
TOPLEVEL := xy_switch
MODULE   := test
SIM ?= verilator

export X_CORD			?= "$(PACKET_X_ADDR_W)'d1"
export Y_CORD			?= "$(PACKET_Y_ADDR_W)'d1"
export PACKET_W			?= "16"
export PACKET_X_ADDR_W 	?= "4"
export PACKET_Y_ADDR_W	?= "4"
export PACKET_DATA_W 	?= "8"
export NEIGHBOURS_N 	?= "4"

ifeq ($(SIM), verilator)
		COCOTB_HDL_TIMEUNIT = 1ns
		COCOTB_HDL_TIMEPRECISION = 1ps
		# Trace dump
		EXTRA_ARGS += --trace --trace-structs
		COMPILE_ARGS += -O3
		EXTRA_ARGS += -GNEIGHBOURS_N=$(NEIGHBOURS_N)
		EXTRA_ARGS += -GX_CORD=$(X_CORD)
		EXTRA_ARGS += -GY_CORD=$(Y_CORD)
#		EXTRA_ARGS += -DPACKET_W=$(PACKET_W)
		EXTRA_ARGS += -DPACKET_X_ADDR_W=$(PACKET_X_ADDR_W)
		EXTRA_ARGS += -DPACKET_Y_ADDR_W=$(PACKET_Y_ADDR_W)
		EXTRA_ARGS += -DPACKET_DATA_W=$(PACKET_DATA_W)

endif

#ifeq ($(SIM), icarus)
#		EXTRA_ARGS += -PDATA_WIDTH=$(DATA_WIDTH)
#		EXTRA_ARGS += -PFIFO_DEPTH_WIDTH=$(FIFO_DEPTH_WIDTH)
## 		EXTRA_ARGS += -PALMOST_FULL_LEVEL=$(ALMOST_FULL_LEVEL)
## 		EXTRA_ARGS += -PALMOST_EMPTY_LEVEL=$(ALMOST_EMPTY_LEVEL)
#endif

include $(shell cocotb-config --makefiles)/Makefile.sim
