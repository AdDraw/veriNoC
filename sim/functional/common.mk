# common VARS and EXPORTS
## EXPORTS
export PYTHON_BIN=/usr/bin/python3
export SHELL=/bin/bash
export TOPLEVEL_LANG ?= verilog
## VARS
GIT_ROOT=$(shell git rev-parse --show-toplevel)
SRCS_DIR=$(GIT_ROOT)/srcs
SYNTH_DIR=$(GIT_ROOT)/synth
CMOS_CELLS=$(SYNTH_DIR)/cmos_cells.v
SIM ?= icarus
COCOTB_HDL_TIMEUNIT      = 1ns
COCOTB_HDL_TIMEPRECISION = 10ps