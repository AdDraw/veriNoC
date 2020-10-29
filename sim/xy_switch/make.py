import os
import subprocess

# Simulation Parameters
PROF = 0
CLEAN = 0
MUTE = False
os.environ["HDL_LANG"] = "verilog"
os.environ["SIM"] = "verilator"

PACKET_W = 16
PACKET_X_ADDR_W = 4
PACKET_Y_ADDR_W = 4
PACKET_DATA_W = 8
NEIGHBOURS_N = 4

os.environ["PACKET_W"] = f"{PACKET_W}"
os.environ["PACKET_X_ADDR_W"] = f"{PACKET_X_ADDR_W}"
os.environ["PACKET_Y_ADDR_W"] = f"{PACKET_Y_ADDR_W}"
os.environ["PACKET_DATA_W"] = f"{PACKET_DATA_W}"
os.environ["NEIGHBOURS_N"] = f"{NEIGHBOURS_N}"

# MAKEFILE call
if PROF == 1:
    os.environ["PROF"] = str(1)

if CLEAN == 1:
    subprocess.call(["make", "clean"])
    subprocess.call(["make"])

else:
    subprocess.call(["make"])