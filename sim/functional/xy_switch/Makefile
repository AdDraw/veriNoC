export PYTHON_BIN=/usr/bin/python3
export SHELL=/bin/bash

export TOPLEVEL_LANG ?= verilog
VER_DIR=$(shell git rev-parse --show-toplevel)/srcs/switch/simple_mesh_xy

export DEBUG_ATTACH ?=0
export TESTFACTORY ?=0
#export COVERAGE?=0

# files
VERILOG_SOURCES += $(VER_DIR)/xy_switch.v
VERILOG_SOURCES += $(VER_DIR)/control_unit.v
VERILOG_SOURCES += $(VER_DIR)/packet_arbiter.v
VERILOG_SOURCES += $(VER_DIR)/crossbar.v
VERILOG_SOURCES += $(VER_DIR)/router_xy.v
VERILOG_SOURCES += $(VER_DIR)/../../components/fifo.v
VERILOG_SOURCES += ./tb.v

# Specifies essentials of the DUT and the cocotb TB
TOPLEVEL := tb
MODULE   := test
SIM ?= icarus

export PORT_N=5
export X_CORD=1
export Y_CORD=1
export PACKET_X_ADDR_W=4
export PACKET_Y_ADDR_W=4
export PACKET_DATA_W=16
PCKT_W_calc = $(shell expr $(PACKET_X_ADDR_W) + $(PACKET_Y_ADDR_W) + $(PACKET_DATA_W) )
export PACKET_W=$(PCKT_W_calc)
export IN_FIFO_DEPTH_W=2

COCOTB_HDL_TIMEUNIT = 1ns
COCOTB_HDL_TIMEPRECISION = 1ps
#COMPILE_ARGS+= -m /usr/local/libexec/covered.vpi covered_vpi.v
COMPILE_ARGS+= -P $(TOPLEVEL).PORT_N=$(PORT_N)
COMPILE_ARGS+= -P $(TOPLEVEL).X_CORD=$(X_CORD)
COMPILE_ARGS+= -P $(TOPLEVEL).Y_CORD=$(Y_CORD)
COMPILE_ARGS+= -P $(TOPLEVEL).PCKT_W=$(PACKET_W)
COMPILE_ARGS+= -P $(TOPLEVEL).PCKT_XADDR_W=$(PACKET_X_ADDR_W)
COMPILE_ARGS+= -P $(TOPLEVEL).PCKT_YADDR_W=$(PACKET_Y_ADDR_W)
COMPILE_ARGS+= -P $(TOPLEVEL).PCKT_DATA_W=$(PACKET_DATA_W)
COMPILE_ARGS+= -P $(TOPLEVEL).IN_FIFO_DEPTH_W=$(IN_FIFO_DEPTH_W)

include $(shell cocotb-config --makefiles)/Makefile.sim
