export PYTHON_BIN=/usr/bin/python3
export SHELL=/bin/bash

export TOPLEVEL_LANG ?= verilog
SRC_DIR=$(shell git rev-parse --show-toplevel)/srcs/

# files
VERILOG_SOURCES= $(SRC_DIR)/components/circ_fifo.v
VERILOG_SOURCES+= $(SRC_DIR)/switch/constants.v
VERILOG_SOURCES+= $(SRC_DIR)/switch/virtual_channels/virtual_channel.v
ifeq ($(SYNTH), 1)
	VERILOG_SOURCES= $(SRC_DIR)/switch/virtual_channels/virtual_channel_synth.v
endif
VERILOG_SOURCES+= ./tb.v
# Specifies essentials of the DUT and the cocotb TB
TOPLEVEL := tb
MODULE   := test
SIM 		 ?= icarus

# Depending on the Simulator we want to choose different sets of arguments to pass
export VC_DEPTH_W 	= 2
export FLIT_DATA_W	= 8
export FLIT_ID_W 		= 2
export CLK_PERIOD 	= 10

ifeq ($(SIM), verilator)
		COCOTB_HDL_TIMEUNIT = 1ns
		COCOTB_HDL_TIMEPRECISION = 1ps
		# Trace dump
		EXTRA_ARGS += --trace --trace-structs
		COMPILE_ARGS += -O3
		EXTRA_ARGS += -GDATA_W=$(FLIT_DATA_W)
		EXTRA_ARGS += -GVC_DEPTH_W=$(VC_DEPTH_W)
		EXTRA_ARGS += -GID_W=$(FLIT_ID_W)
endif

ifeq ($(SIM), icarus)
		COMPILE_ARGS += -P $(TOPLEVEL).FLIT_DATA_W=$(FLIT_DATA_W)
		COMPILE_ARGS += -P $(TOPLEVEL).VC_DEPTH_W=$(VC_DEPTH_W)
		COMPILE_ARGS += -P $(TOPLEVEL).FLIT_ID_W=$(FLIT_ID_W)
		COMPILE_ARGS += -P $(TOPLEVEL).CLK_PERIOD=$(CLK_PERIOD)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
