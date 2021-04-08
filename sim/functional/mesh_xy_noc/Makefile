export PYTHON_BIN=/usr/bin/python3
export SHELL=/bin/bash

export TOPLEVEL_LANG ?= verilog
SWITCH_VER_DIR=$(shell git rev-parse --show-toplevel)/srcs/switch/simple_mesh_xy
NOC_VER_DIR=$(shell git rev-parse --show-toplevel)/srcs/noc

export DEBUG_ATTACH ?=0
export TESTFACTORY ?=0
#export COVERAGE?=0
LOG_DEBUG?=0

# files
VERILOG_SOURCES += $(SWITCH_VER_DIR)/switch_constants.v
VERILOG_SOURCES += $(SWITCH_VER_DIR)/xy_switch.v
VERILOG_SOURCES += $(SWITCH_VER_DIR)/control_unit.v
VERILOG_SOURCES += $(SWITCH_VER_DIR)/packet_arbiter.v
VERILOG_SOURCES += $(SWITCH_VER_DIR)/crossbar.v
VERILOG_SOURCES += $(SWITCH_VER_DIR)/router_xy.v
VERILOG_SOURCES += $(SWITCH_VER_DIR)/../../components/fifo.v
VERILOG_SOURCES += $(NOC_VER_DIR)/mesh_xy_noc.v
ifeq ($(SYNTH), 1)
	VERILOG_SOURCES = $(NOC_VER_DIR)/mesh_xy_noc_synth.v
endif
VERILOG_SOURCES += ./tb.sv

# Specifies essentials of the DUT and the cocotb TB
TOPLEVEL 	:= tb
MODULE   	:= test
SIM 		?= icarus

export ROW_N		?= 4
export COL_M		?= 4
export PCKT_DATA_W	?= 8
export FIFO_DEPTH_W	?= 8

# Clock period in NS
export CLK_PERIOD   ?= 10

COCOTB_HDL_TIMEUNIT = 1ns
COCOTB_HDL_TIMEPRECISION = 1ps

COMPILE_ARGS+= -P $(TOPLEVEL).ROW_N=$(ROW_N)
COMPILE_ARGS+= -P $(TOPLEVEL).COL_M=$(COL_M)
COMPILE_ARGS+= -P $(TOPLEVEL).PCKT_DATA_W=$(PCKT_DATA_W)
COMPILE_ARGS+= -P $(TOPLEVEL).FIFO_DEPTH_W=$(FIFO_DEPTH_W)
COMPILE_ARGS+= -P $(TOPLEVEL).CLK_PERIOD=$(CLK_PERIOD)
COMPILE_ARGS+= -D SIMULATION=1
ifeq ($(LOG_DEBUG), 1)
	COMPILE_ARGS+= -D LOG_DEBUG
endif


DOT_BINARY ?= dot
test_profile.pstat: sim
callgraph.svg: test_profile.pstat
	$(shell cocotb-config --python-bin) -m gprof2dot -f pstats ./$< | $(DOT_BINARY) -Tsvg -o $@

.PHONY: profile
profile:
	COCOTB_ENABLE_PROFILING=1 $(MAKE) callgraph.svg

include $(shell cocotb-config --makefiles)/Makefile.sim
