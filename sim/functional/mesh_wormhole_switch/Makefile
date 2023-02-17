include ../common.mk

# files
VERILOG_SOURCES = $(SRCS_DIR)/switch/constants.v
VERILOG_SOURCES += $(SRCS_DIR)/components/circ_fifo.v
VERILOG_SOURCES += $(SRCS_DIR)/switch/arbiters/matrix_arbiter.v
VERILOG_SOURCES += $(SRCS_DIR)/switch/arbiters/round_robin.v
VERILOG_SOURCES += $(SRCS_DIR)/switch/arbiters/static_priority_arbiter.v
VERILOG_SOURCES += $(SRCS_DIR)/switch/allocators/allocator.v
VERILOG_SOURCES += $(SRCS_DIR)/switch/routers/xy_router.v
VERILOG_SOURCES += $(SRCS_DIR)/switch/virtual_channels/virtual_channel.v
VERILOG_SOURCES += $(SRCS_DIR)/switch/crossbars/nxn_parrallel_crossbar.v
VERILOG_SOURCES += $(SRCS_DIR)/switch/mesh_wormhole/mesh_wormhole_node.v
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
export IN_N           ?= 5 # 1
export OUT_M          ?= 5 # 2
export ROW_CORD       ?= 1 # 3
export COL_CORD       ?= 1 # 4
export COL_ADDR_W     ?= 2 # 5
export ROW_ADDR_W     ?= 2 # 6
export FLIT_ID_W      ?= 2 # 7
export FLIT_DATA_W    ?= 8 # 8
export BUFFER_DEPTH_W ?= 2 # 9
export ARB_TYPE       ?= 0 # 10

ifeq ($(SIM), icarus)
  COMPILE_ARGS += -P $(TOPLEVEL).IN_N=$(IN_N)                      # 1
  COMPILE_ARGS += -P $(TOPLEVEL).OUT_M=$(OUT_M)                    # 2
  COMPILE_ARGS += -P $(TOPLEVEL).FLIT_ID_W=$(FLIT_ID_W)            # 3
  COMPILE_ARGS += -P $(TOPLEVEL).FLIT_DATA_W=$(FLIT_DATA_W)        # 4
  COMPILE_ARGS += -P $(TOPLEVEL).ROW_CORD=$(ROW_CORD)              # 5
  COMPILE_ARGS += -P $(TOPLEVEL).ROW_ADDR_W=$(ROW_ADDR_W)          # 6
  COMPILE_ARGS += -P $(TOPLEVEL).COL_ADDR_W=$(COL_ADDR_W)          # 7
  COMPILE_ARGS += -P $(TOPLEVEL).COL_CORD=$(COL_CORD)              # 8
  COMPILE_ARGS += -P $(TOPLEVEL).BUFFER_DEPTH_W=$(BUFFER_DEPTH_W)  # 9
  COMPILE_ARGS += -P $(TOPLEVEL).ARB_TYPE=$(ARB_TYPE)              # 10
  COMPILE_ARGS += -P $(TOPLEVEL).CLK_PERIOD=$(CLK_PERIOD)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
