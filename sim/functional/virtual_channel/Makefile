include ../common.mk

# files
VERILOG_SOURCES = $(SRCS_DIR)/switch/constants.v
VERILOG_SOURCES += $(SRCS_DIR)/components/circ_fifo.v
VERILOG_SOURCES += $(SRCS_DIR)/switch/routers/xy_router.v
VERILOG_SOURCES += $(SRCS_DIR)/switch/virtual_channels/virtual_channel.v
ifeq ($(SYNTH), 1)
  VERILOG_SOURCES = $(CMOS_CELLS)
  VERILOG_SOURCES += $(SYNTH_DIR)/virtual_channel-netlist.v
endif
VERILOG_SOURCES+= ./tb.v
# Specifies essentials of the DUT and the cocotb TB
TOPLEVEL := tb
MODULE   := test

# Depending on the Simulator we want to choose different sets of arguments to pass
export VC_DEPTH_W   ?= 2
export FLIT_DATA_W  ?= 8
export FLIT_ID_W    ?= 2
export CLK_PERIOD   ?= 10
export ROW_CORD     ?= 1
export COL_CORD     ?= 1
export COL_ADDR_W   ?= 2
export ROW_ADDR_W   ?= 2
export OUT_N_W      ?= 3


COMPILE_ARGS += -P $(TOPLEVEL).FLIT_DATA_W=$(FLIT_DATA_W)
COMPILE_ARGS += -P $(TOPLEVEL).VC_DEPTH_W=$(VC_DEPTH_W)
COMPILE_ARGS += -P $(TOPLEVEL).FLIT_ID_W=$(FLIT_ID_W)
COMPILE_ARGS += -P $(TOPLEVEL).ROW_CORD=$(ROW_CORD)
COMPILE_ARGS += -P $(TOPLEVEL).COL_CORD=$(COL_CORD)
COMPILE_ARGS += -P $(TOPLEVEL).ROW_ADDR_W=$(ROW_ADDR_W)
COMPILE_ARGS += -P $(TOPLEVEL).COL_ADDR_W=$(COL_ADDR_W)
COMPILE_ARGS += -P $(TOPLEVEL).OUT_N_W=$(OUT_N_W)
COMPILE_ARGS += -P $(TOPLEVEL).CLK_PERIOD=$(CLK_PERIOD)


include $(shell cocotb-config --makefiles)/Makefile.sim
