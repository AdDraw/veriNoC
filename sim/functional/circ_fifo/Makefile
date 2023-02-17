include ../common.mk

# files
VERILOG_SOURCES=$(SRCS_DIR)/components/circ_fifo.v
ifeq ($(SYNTH), 1)
  VERILOG_SOURCES = $(CMOS_CELLS)
  VERILOG_SOURCES += $(SYNTH_DIR)/circ_fifo-netlist.v
endif

# Specifies essentials of the DUT and the cocotb TB
TOPLEVEL := circ_fifo
MODULE   := test

# Depending on the Simulator we want to choose different sets of arguments to pass
export FIFO_DEPTH_W ?= 4
export DATA_W       ?= 8

COMPILE_ARGS += -P $(TOPLEVEL).DATA_W=$(DATA_W)
COMPILE_ARGS += -P $(TOPLEVEL).FIFO_DEPTH_W=$(FIFO_DEPTH_W)

include $(shell cocotb-config --makefiles)/Makefile.sim
