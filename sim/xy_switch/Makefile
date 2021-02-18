export PYTHON_BIN=/usr/bin/python3
export SHELL=/bin/bash

export TOPLEVEL_LANG ?= verilog
VER_DIR=$(shell pwd)/../../srcs/switch/simple_mesh_xy

# files
VERILOG_SOURCES += $(VER_DIR)/xy_switch.v
VERILOG_SOURCES += $(VER_DIR)/control_unit.v
VERILOG_SOURCES += $(VER_DIR)/packet_arbiter.v
VERILOG_SOURCES += $(VER_DIR)/crossbar.v
VERILOG_SOURCES += $(VER_DIR)/router_xy.v
VERILOG_SOURCES += $(VER_DIR)/../../components/fifo.v

# Specifies essentials of the DUT and the cocotb TB
TOPLEVEL := xy_switch
MODULE   := test
SIM ?= verilator

export PORT_N=5
export X_CORD=1
export Y_CORD=1
export PACKET_X_ADDR_W=4
export PACKET_Y_ADDR_W=4
export PACKET_DATA_W=8
PCKT_W_calc = $(shell expr $(PACKET_X_ADDR_W) + $(PACKET_Y_ADDR_W) + $(PACKET_DATA_W) )
export PACKET_W=$(PCKT_W_calc)
export IN_FIFO_DEPTH_W=8

COCOTB_HDL_TIMEUNIT = 1ns
COCOTB_HDL_TIMEPRECISION = 1ps
# Trace dump
EXTRA_ARGS +=--trace --trace-structs
COMPILE_ARGS+=-O3
EXTRA_ARGS+=-GPORT_N=$(PORT_N)
EXTRA_ARGS+=-GX_CORD=$(X_CORD)
EXTRA_ARGS+=-GY_CORD=$(Y_CORD)
EXTRA_ARGS+=-GPCKT_W=$(PACKET_W)
EXTRA_ARGS+=-GPCKT_XADDR_W=$(PACKET_X_ADDR_W)
EXTRA_ARGS+=-GPCKT_YADDR_W=$(PACKET_Y_ADDR_W)
EXTRA_ARGS+=-GPCKT_DATA_W=$(PACKET_DATA_W)
EXTRA_ARGS+=-GIN_FIFO_DEPTH_W=$(IN_FIFO_DEPTH_W)

include $(shell cocotb-config --makefiles)/Makefile.sim
