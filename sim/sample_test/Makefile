export PYTHON_BIN=/usr/bin/python3
export SHELL=/bin/bash

export TOPLEVEL_LANG ?= verilog
VER_DIR=$(shell pwd)/../../srcs/sample

# files
VERILOG_SOURCES= $(VER_DIR)/cnt_nbit.v

# Specifies essentials of the DUT and the cocotb TB
TOPLEVEL := counter_nbit
MODULE   := test
SIM ?= verilator

# Depending on the Simulator we want to choose different sets of arguments to pass
CNT_BITWIDTH 				= "8"
ALMOST_EMPTY_LEVEL	= "$(CNT_BITWIDTH)'d25"
ALMOST_FULL_LEVEL 	= "$(CNT_BITWIDTH)'d225"
ENABLE_LOW_SAT  		= "1'b1"
ENABLE_HIGH_SAT 		= "1'b1"


ifeq ($(SIM), verilator)
		COCOTB_HDL_TIMEUNIT = 1ns
		COCOTB_HDL_TIMEPRECISION = 1ps
		export VERILATOR_TRACE = 1
		COMPILE_ARGS += -O3
		EXTRA_ARGS += -GCNT_BITWIDTH=$(CNT_BITWIDTH)
		EXTRA_ARGS += -GALMOST_FULL_LEVEL=$(ALMOST_FULL_LEVEL)
		EXTRA_ARGS += -GALMOST_EMPTY_LEVEL=$(ALMOST_EMPTY_LEVEL)
		EXTRA_ARGS += -GENABLE_LOW_SAT=$(ENABLE_LOW_SAT)
		EXTRA_ARGS += -GENABLE_HIGH_SAT=$(ENABLE_HIGH_SAT)
endif

ifeq ($(SIM), icarus)
		EXTRA_ARGS += -PCNT_BITWIDTH=$(CNT_BITWIDTH)
		EXTRA_ARGS += -PALMOST_FULL_LEVEL=$(ALMOST_FULL_LEVEL)
		EXTRA_ARGS += -PALMOST_EMPTY_LEVEL=$(ALMOST_EMPTY_LEVEL)
		EXTRA_ARGS += -PENABLE_LOW_SAT=$(ENABLE_LOW_SAT)
		EXTRA_ARGS += -PENABLE_HIGH_SAT=$(ENABLE_HIGH_SAT)
endif


ifeq ($(PROF), 1)
    export COCOTB_ENABLE_PROFILING=1
endif

include $(shell cocotb-config --makefiles)/Makefile.inc
include $(shell cocotb-config --makefiles)/Makefile.sim
