import os
from math import log
import subprocess
import datetime

# Simulation Parameters
PROF = 0
CLEAN = 0
MUTE = False
os.environ["HDL_LANG"] = "verilog"
os.environ["SIM"] = "verilator"

DATA_WIDTH = 8
FIFO_DEPTH_WIDTH = 2
ALMOST_EMPTY_LEVEL = 2
ALMOST_FULL_LEVEL = 8

os.environ["DATA_WIDTH"] = f"{DATA_WIDTH}"
os.environ["FIFO_DEPTH_WIDTH"] = f"{FIFO_DEPTH_WIDTH}"
os.environ["ALMOST_FULL_LEVEL"] = f"{FIFO_DEPTH_WIDTH}'d{ALMOST_FULL_LEVEL}"
os.environ["ALMOST_EMPTY_LEVEL"] = f"{FIFO_DEPTH_WIDTH}'d{ALMOST_EMPTY_LEVEL}"

# MAKEFILE call
if PROF == 1:
    os.environ["PROF"] = str(1)

if CLEAN == 1:
    subprocess.call(["make", "clean"])
    subprocess.call(["make"])
    # subprocess.call(["gtkwave dump.vcd -S gtkwave_tcl.tcl"])

else:
    subprocess.call(["make"])
    # subprocess.call(["pwd"])
    # subprocess.call(["ls"])
    # subprocess.call(["gtkwave dump.vcd -S gtkwave_tcl.tcl"])
