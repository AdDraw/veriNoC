import os
from math import log
import subprocess
import datetime

# Simulation Parameters
PROF = 0
CLEAN = 1
MUTE = False
os.environ["HDL_LANG"] = "vhdl"
os.environ["SIM"] = "verilator"

CNT_BITWIDTH = int(log(256, 2))
ALMOST_EMPTY_LEVEL = 25
ALMOST_FULL_LEVEL = 225
ENABLE_LOW_SAT = 1
ENABLE_HIGH_SAT = 1

os.environ["CNT_BITWIDTH"] = f"{CNT_BITWIDTH}"
os.environ["ALMOST_FULL_LEVEL"] = f"{CNT_BITWIDTH}'d{ALMOST_FULL_LEVEL}"
os.environ["ALMOST_EMPTY_LEVEL"] = f"{CNT_BITWIDTH}'d{ALMOST_EMPTY_LEVEL}"
os.environ["ENABLE_LOW_SAT"] = f"1'b{ENABLE_LOW_SAT}"
os.environ["ENABLE_HIGH_SAT"] = f"1'b{ENABLE_HIGH_SAT}"

# MAKEFILE call
if PROF == 1:
    os.environ["PROF"] = str(1)

if CLEAN == 1:
    subprocess.call(["make", "clean"])
    subprocess.call(["make"])
else:
    subprocess.call(["make"])
