export PYTHON_BIN=/usr/bin/python3
export SHELL=/bin/bash

export TOPLEVEL_LANG ?= verilog
SWITCH_VER_DIR=$(shell git rev-parse --show-toplevel)/srcs/switch/
NOC_VER_DIR=$(shell git rev-parse --show-toplevel)/srcs/noc

export DEBUG_ATTACH ?=0
#export COVERAGE?=0
LOG_DEBUG?=0

# files
# VERILOG_SOURCES += $(SWITCH_VER_DIR)/arbiters/static_priority_arbiter.v
# VERILOG_SOURCES += $(SWITCH_VER_DIR)/arbiters/matrix_arbiter.v
VERILOG_SOURCES += $(SWITCH_VER_DIR)/arbiters/round_robin.v

# Specifies essentials of the DUT and the cocotb TB
TOPLEVEL := round_robin_arb
MODULE   := test
SIM      ?= icarus

export IN_N         ?= 2


COCOTB_HDL_TIMEUNIT      = 1ns
COCOTB_HDL_TIMEPRECISION = 1ps

COMPILE_ARGS += -P $(TOPLEVEL).IN_N=$(IN_N)
COMPILE_ARGS += -D SIMULATION=1

include $(shell cocotb-config --makefiles)/Makefile.sim