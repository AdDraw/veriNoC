export PYTHON_BIN=/usr/bin/python3
export SHELL=/bin/bash

export TOPLEVEL_LANG ?= verilog
VER_DIR=$(shell pwd)/../../srcs/components

# files
VERILOG_SOURCES= $(VER_DIR)/fifo.v

# Specifies essentials of the DUT and the cocotb TB
TOPLEVEL := fifo
MODULE   := test
SIM ?= verilator

# Depending on the Simulator we want to choose different sets of arguments to pass

export FIFO_DEPTH_WIDTH 	= 4
export DATA_WIDTH			    = 8

ifeq ($(SIM), verilator)
		COCOTB_HDL_TIMEUNIT = 1ns
		COCOTB_HDL_TIMEPRECISION = 1ps
		# Trace dump
		EXTRA_ARGS += --trace --trace-structs
		COMPILE_ARGS += -O3
		EXTRA_ARGS += -GDATA_WIDTH=$(DATA_WIDTH)
		EXTRA_ARGS += -GFIFO_DEPTH_WIDTH=$(FIFO_DEPTH_WIDTH)
# 		EXTRA_ARGS += -GALMOST_FULL_LEVEL=$(ALMOST_FULL_LEVEL)
# 		EXTRA_ARGS += -GALMOST_EMPTY_LEVEL=$(ALMOST_EMPTY_LEVEL)
endif

ifeq ($(SIM), icarus)
		EXTRA_ARGS += -PDATA_WIDTH=$(DATA_WIDTH)
		EXTRA_ARGS += -PFIFO_DEPTH_WIDTH=$(FIFO_DEPTH_WIDTH)
# 		EXTRA_ARGS += -PALMOST_FULL_LEVEL=$(ALMOST_FULL_LEVEL)
# 		EXTRA_ARGS += -PALMOST_EMPTY_LEVEL=$(ALMOST_EMPTY_LEVEL)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
