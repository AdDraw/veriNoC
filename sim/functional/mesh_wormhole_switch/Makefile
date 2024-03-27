include ../common.mk

# files
VERILOG_SOURCES = $(SRCS_DIR)/switch/constants.v
VERILOG_SOURCES += $(SRCS_DIR)/components/circ_fifo.v
VERILOG_SOURCES += $(SRCS_DIR)/components/mux_Nx1.sv
VERILOG_SOURCES += $(SRCS_DIR)/switch/arbiters/matrix_arbiter.v
VERILOG_SOURCES += $(SRCS_DIR)/switch/arbiters/round_robin_arbiter.v
VERILOG_SOURCES += $(SRCS_DIR)/switch/arbiters/static_priority_arbiter.v
VERILOG_SOURCES += $(SRCS_DIR)/switch/allocators/allocator.sv
VERILOG_SOURCES += $(SRCS_DIR)/switch/routers/xy_router.v
VERILOG_SOURCES += $(SRCS_DIR)/switch/virtual_channels/virtual_channel.sv
VERILOG_SOURCES += $(SRCS_DIR)/switch/mesh_wormhole/output_channel.sv
VERILOG_SOURCES += $(SRCS_DIR)/switch/mesh_wormhole/mesh_wormhole_node.sv
ifeq ($(SYNTH), 1)
	VERILOG_SOURCES = $(SRCS_DIR)/switch/constants.v
  VERILOG_SOURCES += $(CMOS_CELLS)
  VERILOG_SOURCES += $(SYNTH_DIR)/mesh_wormhole_node-netlist.v
endif
VERILOG_SOURCES += ./tb.sv
# Specifies essentials of the DUT and the cocotb TB
TOPLEVEL := tb
MODULE   := test

export CLK_PERIOD     ?= 10
# Depending on the Simulator we want to choose different sets of arguments to pass
export NODE_RADIX     ?= 5 # 1
export ROW_CORD       ?= 1 # 2
export COL_CORD       ?= 1 # 3
export COL_ADDR_W     ?= 2 # 4
export ROW_ADDR_W     ?= 2 # 5
export FLIT_ID_W      ?= 2 # 6
export FLIT_DATA_W    ?= 8 # 7
export BUFFER_DEPTH_W ?= 2 # 8
export ARB_TYPE       ?= 0 # 9

ifeq ($(SIM), icarus)
  COMPILE_ARGS += -P $(TOPLEVEL).NODE_RADIX=$(NODE_RADIX)          # 1
  COMPILE_ARGS += -P $(TOPLEVEL).FLIT_ID_W=$(FLIT_ID_W)            # 2
  COMPILE_ARGS += -P $(TOPLEVEL).FLIT_DATA_W=$(FLIT_DATA_W)        # 3
  COMPILE_ARGS += -P $(TOPLEVEL).ROW_CORD=$(ROW_CORD)              # 4
  COMPILE_ARGS += -P $(TOPLEVEL).ROW_ADDR_W=$(ROW_ADDR_W)          # 5
  COMPILE_ARGS += -P $(TOPLEVEL).COL_ADDR_W=$(COL_ADDR_W)          # 6
  COMPILE_ARGS += -P $(TOPLEVEL).COL_CORD=$(COL_CORD)              # 7
  COMPILE_ARGS += -P $(TOPLEVEL).BUFFER_DEPTH_W=$(BUFFER_DEPTH_W)  # 8
  COMPILE_ARGS += -P $(TOPLEVEL).ARB_TYPE=$(ARB_TYPE)              # 9
  COMPILE_ARGS += -P $(TOPLEVEL).CLK_PERIOD=$(CLK_PERIOD)
else ifeq ($(SIM), questa)
	COMPILE_ARGS += -GNODE_RADIX=$(NODE_RADIX)          # 1
  COMPILE_ARGS += -GFLIT_ID_W=$(FLIT_ID_W)            # 2
  COMPILE_ARGS += -GFLIT_DATA_W=$(FLIT_DATA_W)        # 3
  COMPILE_ARGS += -GROW_CORD=$(ROW_CORD)              # 4
  COMPILE_ARGS += -GROW_ADDR_W=$(ROW_ADDR_W)          # 5
  COMPILE_ARGS += -GCOL_ADDR_W=$(COL_ADDR_W)          # 6
  COMPILE_ARGS += -GCOL_CORD=$(COL_CORD)              # 7
  COMPILE_ARGS += -GBUFFER_DEPTH_W=$(BUFFER_DEPTH_W)  # 8
  COMPILE_ARGS += -GARB_TYPE=$(ARB_TYPE)              # 9
  COMPILE_ARGS += -GCLK_PERIOD=$(CLK_PERIOD)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
