include ../common.mk

# files
VERILOG_SOURCES = $(SRCS_DIR)/switch/constants.v
VERILOG_SOURCES += $(SRCS_DIR)/switch/arbiters/matrix_arbiter.v
VERILOG_SOURCES += $(SRCS_DIR)/switch/allocators/allocator.v
ifeq ($(SYNTH), 1)
  VERILOG_SOURCES = $(CMOS_CELLS)
  VERILOG_SOURCES += $(SYNTH_DIR)/allocator-netlist.v
endif
VERILOG_SOURCES += ./tb.v
# Specifies essentials of the DUT and the cocotb TB
TOPLEVEL := tb
MODULE   := test

# Depending on the Simulator we want to choose different sets of arguments to pass
export IN_N        = 5
export OUT_M       = 5
export FLIT_ID_W   = 2
export OUT_CHAN_ID = 1
export CLK_PERIOD  = 10

ifeq ($(SIM), icarus)
  COMPILE_ARGS += -P $(TOPLEVEL).IN_N=$(IN_N)
  COMPILE_ARGS += -P $(TOPLEVEL).OUT_M=$(OUT_M)
  COMPILE_ARGS += -P $(TOPLEVEL).FLIT_ID_W=$(FLIT_ID_W)
  COMPILE_ARGS += -P $(TOPLEVEL).OUT_CHAN_ID=$(OUT_CHAN_ID)
  COMPILE_ARGS += -P $(TOPLEVEL).CLK_PERIOD=$(CLK_PERIOD)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
