export PYTHON_BIN=/usr/bin/python3
export SHELL=/bin/bash

export TOPLEVEL_LANG ?= verilog
VER_DIR=$(shell git rev-parse --show-toplevel)/srcs/switch/simple_mesh_xy

export DEBUG_ATTACH ?=0
export TESTFACTORY ?=0
#export COVERAGE?=0

CENTER  = 0
EDGE_RT = 1
EDGE_LT = 2
EDGE_RB = 3
EDGE_LB = 4
SIDE_R  = 5
SIDE_L  = 6
SIDE_T  = 7
SIDE_B  = 8

# files
VERILOG_SOURCES += $(VER_DIR)/switch_constants.v
VERILOG_SOURCES += $(VER_DIR)/xy_switch.v
VERILOG_SOURCES += $(VER_DIR)/control_unit.v
VERILOG_SOURCES += $(VER_DIR)/packet_arbiter.v
VERILOG_SOURCES += $(VER_DIR)/crossbar.v
VERILOG_SOURCES += $(VER_DIR)/router_xy.v
VERILOG_SOURCES += $(VER_DIR)/../../components/fifo.v
VERILOG_SOURCES += ./tb.v

# Specifies essentials of the DUT and the cocotb TB
TOPLEVEL 	:= tb
MODULE   	:= test
SIM 			?= icarus

export PORT_N					?= 5
export COL_CORD					?= 1
export ROW_CORD					?= 1
export PACKET_COL_ADDR_W		?= 4
export PACKET_ROW_ADDR_W		?= 4
export PACKET_DATA_W			?= 16
PCKT_W_calc 					=  $(shell expr $(PACKET_COL_ADDR_W) + $(PACKET_ROW_ADDR_W) + $(PACKET_DATA_W) )
export PACKET_W					?= $(PCKT_W_calc)
export IN_FIFO_DEPTH_W			?= 2
export SW_CONFIG				?= $(CENTER)

COCOTB_HDL_TIMEUNIT = 1ns
COCOTB_HDL_TIMEPRECISION = 1ps
#COMPILE_ARGS+= -m /usr/local/libexec/covered.vpi covered_vpi.v
COMPILE_ARGS+= -P $(TOPLEVEL).PORT_N=$(PORT_N)
COMPILE_ARGS+= -P $(TOPLEVEL).COL_CORD=$(COL_CORD)
COMPILE_ARGS+= -P $(TOPLEVEL).ROW_CORD=$(ROW_CORD)
COMPILE_ARGS+= -P $(TOPLEVEL).PCKT_W=$(PACKET_W)
COMPILE_ARGS+= -P $(TOPLEVEL).PCKT_COL_ADDR_W=$(PACKET_COL_ADDR_W)
COMPILE_ARGS+= -P $(TOPLEVEL).PCKT_ROW_ADDR_W=$(PACKET_ROW_ADDR_W)
COMPILE_ARGS+= -P $(TOPLEVEL).PCKT_DATA_W=$(PACKET_DATA_W)
COMPILE_ARGS+= -P $(TOPLEVEL).IN_FIFO_DEPTH_W=$(IN_FIFO_DEPTH_W)
COMPILE_ARGS+= -P $(TOPLEVEL).SW_CONFIG=$(SW_CONFIG)
COMPILE_ARGS+= -D SIMULATION=1

include $(shell cocotb-config --makefiles)/Makefile.sim
