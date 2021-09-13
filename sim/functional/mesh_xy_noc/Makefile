export PYTHON_BIN=/usr/bin/python3
export SHELL=/bin/bash

export TOPLEVEL_LANG ?= verilog
SWITCH_VER_DIR=$(shell git rev-parse --show-toplevel)/srcs/switch/
NOC_VER_DIR=$(shell git rev-parse --show-toplevel)/srcs/noc

export DEBUG_ATTACH ?=0
export TESTFACTORY ?=0
export SYNTH ?= 0
#export COVERAGE?=0
LOG_DEBUG?=0

# files
VERILOG_SOURCES += $(SWITCH_VER_DIR)/simple_mesh_xy/switch_constants.v
VERILOG_SOURCES += $(SWITCH_VER_DIR)/simple_mesh_xy/xy_switch.v
VERILOG_SOURCES += $(SWITCH_VER_DIR)/simple_mesh_xy/control_unit.v
VERILOG_SOURCES += $(SWITCH_VER_DIR)/arbiters/static_priority_arbiter.v
VERILOG_SOURCES += $(SWITCH_VER_DIR)/arbiters/matrix_arbiter.v
VERILOG_SOURCES += $(SWITCH_VER_DIR)/crossbars/nxn_single_crossbar.v
VERILOG_SOURCES += $(SWITCH_VER_DIR)/routers/xy_router.v
VERILOG_SOURCES += $(SWITCH_VER_DIR)/../components/circ_fifo.v
VERILOG_SOURCES += $(NOC_VER_DIR)/mesh_xy_noc.v
ifeq ($(SYNTH), 1)
  VERILOG_SOURCES = $(shell git rev-parse --show-toplevel)/synth/cmos_cells.v
  VERILOG_SOURCES += $(NOC_VER_DIR)/mesh_xy_noc_synth.v
endif

# Specifies essentials of the DUT and the cocotb TB
TOPLEVEL := tb
MODULE   := test
SIM      ?= icarus

export ROW_N        ?= 4
export COL_M        ?= 4
export PCKT_DATA_W  ?= 8
export FIFO_DEPTH_W ?= 8

# Clock period in NS
export CLK_PERIOD        ?= 10
COCOTB_HDL_TIMEUNIT      = 1ns
COCOTB_HDL_TIMEPRECISION = 1ps

VERILOG_SOURCES += ./tb.sv

COMPILE_ARGS += -P $(TOPLEVEL).ROW_N=$(ROW_N)
COMPILE_ARGS += -P $(TOPLEVEL).COL_M=$(COL_M)
COMPILE_ARGS += -P $(TOPLEVEL).PCKT_DATA_W=$(PCKT_DATA_W)
COMPILE_ARGS += -P $(TOPLEVEL).FIFO_DEPTH_W=$(FIFO_DEPTH_W)
COMPILE_ARGS += -P $(TOPLEVEL).CLK_PERIOD=$(CLK_PERIOD)
COMPILE_ARGS += -D SIMULATION=1

include $(shell cocotb-config --makefiles)/Makefile.sim
