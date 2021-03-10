export PYTHON_BIN=/usr/bin/python3
export SHELL=/bin/bash

export TOPLEVEL_LANG ?= verilog
SWITCH_VER_DIR=$(shell git rev-parse --show-toplevel)/srcs/switch/simple_mesh_xy
NOC_VER_DIR=$(shell git rev-parse --show-toplevel)/srcs/noc

export DEBUG_ATTACH ?=0
export TESTFACTORY ?=0
#export COVERAGE?=0

# files
VERILOG_SOURCES += $(SWITCH_VER_DIR)/switch_constants.v
VERILOG_SOURCES += $(SWITCH_VER_DIR)/xy_switch.v
VERILOG_SOURCES += $(SWITCH_VER_DIR)/control_unit.v
VERILOG_SOURCES += $(SWITCH_VER_DIR)/packet_arbiter.v
VERILOG_SOURCES += $(SWITCH_VER_DIR)/crossbar.v
VERILOG_SOURCES += $(SWITCH_VER_DIR)/router_xy.v
VERILOG_SOURCES += $(SWITCH_VER_DIR)/../../components/fifo.v
VERILOG_SOURCES += $(NOC_VER_DIR)/mesh_xy_noc.v
VERILOG_SOURCES += ./tb.sv

# Specifies essentials of the DUT and the cocotb TB
TOPLEVEL 	:= tb
MODULE   	:= test
SIM 		?= icarus

export ROW_N		?= 3
export COL_M		?= 3
export PCKT_DATA_W	?= 8
export FIFO_DEPTH_W	?= 3

COCOTB_HDL_TIMEUNIT = 1ns
COCOTB_HDL_TIMEPRECISION = 1ps

COMPILE_ARGS+= -P $(TOPLEVEL).ROW_N=$(ROW_N)
COMPILE_ARGS+= -P $(TOPLEVEL).COL_M=$(COL_M)
COMPILE_ARGS+= -P $(TOPLEVEL).PCKT_DATA_W=$(PCKT_DATA_W)
COMPILE_ARGS+= -P $(TOPLEVEL).FIFO_DEPTH_W=$(FIFO_DEPTH_W)
COMPILE_ARGS+= -D SIMULATION=1

include $(shell cocotb-config --makefiles)/Makefile.sim
