export PYTHON_BIN=/usr/bin/python3
export SHELL=/bin/bash

export TOPLEVEL_LANG ?= verilog
VER_DIR=$(shell git rev-parse --show-toplevel)/srcs/components

# files
VERILOG_SOURCES= $(VER_DIR)/fifo.v
ifeq ($(SYNTH), 1)
	VERILOG_SOURCES= $(VER_DIR)/fifo_synth.v
endif

# Specifies essentials of the DUT and the cocotb TB
TOPLEVEL := fifo
MODULE   := test
SIM 		 ?= icarus

# Depending on the Simulator we want to choose different sets of arguments to pass
export FIFO_DEPTH_WIDTH = 2
export DATA_WIDTH = 8

ifeq ($(SIM), verilator)
		COCOTB_HDL_TIMEUNIT = 1ns
		COCOTB_HDL_TIMEPRECISION = 1ps
		# Trace dump
		EXTRA_ARGS += --trace --trace-structs
		COMPILE_ARGS += -O3
		EXTRA_ARGS += -GDATA_WIDTH=$(DATA_WIDTH)
		EXTRA_ARGS += -GFIFO_DEPTH_WIDTH=$(FIFO_DEPTH_WIDTH)
endif

ifeq ($(SIM), icarus)
		COMPILE_ARGS += -P fifo.DATA_WIDTH=$(DATA_WIDTH)
		COMPILE_ARGS += -P fifo.FIFO_DEPTH_WIDTH=$(FIFO_DEPTH_WIDTH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
