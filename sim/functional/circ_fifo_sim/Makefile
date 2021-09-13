export PYTHON_BIN=/usr/bin/python3
export SHELL=/bin/bash

export TOPLEVEL_LANG ?= verilog
VER_DIR=$(shell git rev-parse --show-toplevel)/srcs/components

# files
VERILOG_SOURCES=$(VER_DIR)/circ_fifo.v
ifeq ($(SYNTH), 1)
  VERILOG_SOURCES = $(shell git rev-parse --show-toplevel)/synth/cmos_cells.v
  VERILOG_SOURCES += $(VER_DIR)/circ_fifo_synth.v
endif

# Specifies essentials of the DUT and the cocotb TB
TOPLEVEL := circ_fifo
MODULE   := test
SIM      ?= icarus

# Depending on the Simulator we want to choose different sets of arguments to pass
export FIFO_DEPTH_W ?= 4
export DATA_W       ?= 8

COMPILE_ARGS += -P $(TOPLEVEL).DATA_W=$(DATA_W)
COMPILE_ARGS += -P $(TOPLEVEL).FIFO_DEPTH_W=$(FIFO_DEPTH_W)

include $(shell cocotb-config --makefiles)/Makefile.sim
