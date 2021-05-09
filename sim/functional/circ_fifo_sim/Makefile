export PYTHON_BIN=/usr/bin/python3
export SHELL=/bin/bash

export TOPLEVEL_LANG ?= verilog
VER_DIR=$(shell git rev-parse --show-toplevel)/srcs/components

# files
VERILOG_SOURCES=$(VER_DIR)/circ_fifo.v
ifeq ($(SYNTH), 1)
	VERILOG_SOURCES= $(VER_DIR)/circ_fifo_synth.v
endif

# Specifies essentials of the DUT and the cocotb TB
TOPLEVEL := circ_fifo
MODULE   := test
SIM 		 ?= icarus

# Depending on the Simulator we want to choose different sets of arguments to pass
export FIFO_DEPTH_W	= 2
export DATA_W				= 8

ifeq ($(SIM), verilator)
		COCOTB_HDL_TIMEUNIT = 1ns
		COCOTB_HDL_TIMEPRECISION = 1ps
		# Trace dump
		EXTRA_ARGS += --trace --trace-structs
		COMPILE_ARGS += -O3
		EXTRA_ARGS += -GDATA_W=$(DATA_W)
		EXTRA_ARGS += -GFIFO_DEPTH_W=$(FIFO_DEPTH_W)
endif

ifeq ($(SIM), icarus)
		COMPILE_ARGS += -P $(TOPLEVEL).DATA_W=$(DATA_W)
		COMPILE_ARGS += -P $(TOPLEVEL).FIFO_DEPTH_W=$(FIFO_DEPTH_W)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
