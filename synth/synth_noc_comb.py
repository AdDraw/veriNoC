import subprocess
import os
import time
import argparse
from utils.rav import *
from utils.adam_logger import *
import glob
import sys
import numpy as np

def call_yosys_wrapper(tcl_script, parameters):
  pwd = os.getcwd()
  git_root = get_git_root(os.getcwd())
  synth_cmd = [f"{git_root}/synth/yosys_wrapper.sh", f"-sf", f"{tcl_script}",
               "--no-xdot"]
  for arg in parameters.items():
      synth_cmd.append(f"{arg[0]}={arg[1]}")

  print(f"Synth Command: {synth_cmd}")
  subprocess.run(synth_cmd)
  os.chdir(pwd)

  return 0


def run_synths(scripts, change):

  if change == "k":
    k = np.arange(3, 5+1, step=1)
  else:
    k = [3]

  if change == "w":
    channel_w = np.array([1, 2, 4]) * 8
  else:
    channel_w = [8]

  if change == "d":
    ff_depth = np.arange(2, 4+1, step =1)
  else:
    ff_depth = [2]

  for k_val in k:
    for depth in ff_depth:
      for w in channel_w:
        for script in scripts:
          if script == "mesh_wh_xy_noc.tcl":
            arguments = {"ROW_N": k_val,
                         "COL_M": k_val,
                         "NODE_BUFFER_DEPTH_W": depth,
                         "CHANNEL_W": w}
          else:
            arguments = {"ROW_N": k_val,
                         "COL_M": k_val,
                         "FIFO_DEPTH_W": depth,
                         "PCKT_DATA_W": w}

          call_yosys_wrapper(script, arguments)

def main() -> None:
  scripts = [ "mesh_wh_xy_noc.tcl", "mesh_xy_noc.tcl"]

  # STATIC K,FD_D CHANGING CHAN W
  run_synths(scripts, change="w")
  #STATIC CHAN_W, FFD, CHANGING K
  run_synths(scripts, change="k")
  #STATIC K, CHAN_W, CHANGING FF_D
  run_synths(scripts, change="d")

  sys.exit(0)

if __name__ == '__main__':

  main()
