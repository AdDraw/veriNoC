export PYTHON_BIN=/usr/bin/python3
export SHELL=/bin/bash

export TOPLEVEL_LANG ?= verilog
SRCS_DIR=$(shell git rev-parse --show-toplevel)/srcs
SWITCH_VER_DIR=$(SRCS_DIR)/switch
COMPONENT_VER_DIR=$(SRCS_DIR)/components
NOC_VER_DIR=$(SRCS_DIR)/noc

export DEBUG_ATTACH ?=0
export TESTFACTORY ?=0
export SYNTH ?= 0
#export COVERAGE?=0
LOG_DEBUG?=0

# files
VERILOG_SOURCES += $(SWITCH_VER_DIR)/constants.v
VERILOG_SOURCES += $(COMPONENT_VER_DIR)/circ_fifo.v
VERILOG_SOURCES += $(SWITCH_VER_DIR)/arbiters/matrix_arbiter.v
VERILOG_SOURCES += $(SWITCH_VER_DIR)/crossbars/nxn_parrallel_crossbar.v
VERILOG_SOURCES += $(SWITCH_VER_DIR)/routers/xy_router.v
VERILOG_SOURCES += $(SWITCH_VER_DIR)/virtual_channels/virtual_channel.v
VERILOG_SOURCES += $(SWITCH_VER_DIR)/allocators/allocator.v
VERILOG_SOURCES += $(SWITCH_VER_DIR)/mesh_wormhole/mesh_wormhole_node.v
VERILOG_SOURCES += $(NOC_VER_DIR)/mesh_wormhole_xy_noc.v

ifeq ($(SYNTH), 1)
  VERILOG_SOURCES = $(shell git rev-parse --show-toplevel)/synth/cmos_cells.v
  VERILOG_SOURCES += $(NOC_VER_DIR)/mesh_wormhole_xy_noc_synth.v
endif


# Specifies essentials of the DUT and the cocotb TB
TOPLEVEL  := tb
MODULE    := test
SIM       ?= icarus

export ROW_N                ?= 4
export COL_M                ?= 4
export CHANNEL_W            ?= 10
export FLIT_ID_W            ?= 2
export NODE_RADIX           ?= 5
export NODE_BUFFER_DEPTH_W  ?= 2
export CLK_PERIOD           ?= 10

COCOTB_HDL_TIMEUNIT       = 1ns
COCOTB_HDL_TIMEPRECISION  = 10ps

VERILOG_SOURCES += ./tb.sv
COMPILE_ARGS += -P $(TOPLEVEL).ROW_N=$(ROW_N)
COMPILE_ARGS += -P $(TOPLEVEL).COL_M=$(COL_M)
COMPILE_ARGS += -P $(TOPLEVEL).FLIT_ID_W=$(FLIT_ID_W)
COMPILE_ARGS += -P $(TOPLEVEL).NODE_RADIX=$(NODE_RADIX)
COMPILE_ARGS += -P $(TOPLEVEL).CHANNEL_W=$(CHANNEL_W)
COMPILE_ARGS += -P $(TOPLEVEL).NODE_BUFFER_DEPTH_W=$(NODE_BUFFER_DEPTH_W)
COMPILE_ARGS += -P $(TOPLEVEL).CLK_PERIOD=$(CLK_PERIOD)
COMPILE_ARGS += -D SIMULATION=1
ifeq ($(LOG_DEBUG), 1)
  COMPILE_ARGS += -D LOG_DEBUG
endif

test_profile.pstat: sim

callgraph.svg: test_profile.pstat
	gprof2dot -f pstats $< | dot -Tsvg -o $@

.PHONY: profile
profile:
	COCOTB_ENABLE_PROFILING=1 $(MAKE) callgraph.svg


include $(shell cocotb-config --makefiles)/Makefile.sim
