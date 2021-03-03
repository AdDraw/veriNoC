export PYTHON_BIN=/usr/bin/python3
export SHELL=/bin/bash

export TOPLEVEL_LANG ?= verilog
VER_DIR=$(shell git rev-parse --show-toplevel)/srcs/sample

# files
VERILOG_SOURCES= $(VER_DIR)/cnt_nbit.v

# Specifies essentials of the DUT and the cocotb TB
TOPLEVEL := counter_nbit
MODULE   := test
SIM ?= icarus

# Depending on the Simulator we want to choose different sets of arguments to pass
export CNT_BITWIDTH 			= 8
export ALMOST_EMPTY_LEVEL	= 25
export ALMOST_FULL_LEVEL 	= 225
export ENABLE_LOW_SAT  		= 1
export ENABLE_HIGH_SAT 		= 1


ifeq ($(SIM), verilator)
		COCOTB_HDL_TIMEUNIT = 1ns
		COCOTB_HDL_TIMEPRECISION = 1ps
		COMPILE_ARGS += -O3
		EXTRA_ARGS += -GCNT_BITWIDTH=$(CNT_BITWIDTH)
		EXTRA_ARGS += -GALMOST_FULL_LEVEL=$(ALMOST_FULL_LEVEL)
		EXTRA_ARGS += -GALMOST_EMPTY_LEVEL=$(ALMOST_EMPTY_LEVEL)
		EXTRA_ARGS += -GENABLE_LOW_SAT=$(ENABLE_LOW_SAT)
		EXTRA_ARGS += -GENABLE_HIGH_SAT=$(ENABLE_HIGH_SAT)
endif

ifeq ($(SIM), icarus)
		COMPILE_ARGS += -P test.CNT_BITWIDTH=$(CNT_BITWIDTH)
		COMPILE_ARGS += -P test.ALMOST_FULL_LEVEL=$(ALMOST_FULL_LEVEL)
		COMPILE_ARGS += -P test.ALMOST_EMPTY_LEVEL=$(ALMOST_EMPTY_LEVEL)
		COMPILE_ARGS += -P test.ENABLE_LOW_SAT=$(ENABLE_LOW_SAT)
		COMPILE_ARGS += -P test.ENABLE_HIGH_SAT=$(ENABLE_HIGH_SAT)
endif


ifeq ($(PROF), 1)
    export COCOTB_ENABLE_PROFILING=1
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
