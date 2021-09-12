import subprocess
import os
import time
import argparse
from utils.rav import *
from utils.adam_logger import *


def main(tf, ps, synth, row_n, col_m, ff_depth, channel_w, regression, log_lvl) -> None:
  log = get_logger(__name__, int(log_lvl))
  log.info(f"RUN {time.asctime()}")

  tcl_script = "mesh_wh_xy_noc.tcl"
  arguments = {"ROW_N": row_n,
               "COL_M": col_m,
               "NODE_BUFFER_DEPTH_W": ff_depth,
               "CHANNEL_W": channel_w}

  if regression:
    runs = []
    failed_runs = 0
    row_max = 4
    col_max = 4
    for ri in range(2, row_max + 1):
      for ci in range(2, col_max + 1):
        arguments = {"ROW_N": row_n,
                     "COL_M": col_m, "NODE_BUFFER_DEPTH_W": ff_depth,
                     "CHANNEL_W": channel_w}
        runs.append(simulate(log, tf, ps, synth, arguments, tcl_script))
        failed_runs += runs[-1][0]

    log.info("----------------------------------------------------------------------------------------------------"
             "-------")
    if failed_runs > 0:
      for rid, run in enumerate(runs):
          if run[0]:  # FAILED RUN
              log.error(f"Run {rid}. FAILED")
              log.error(f"Config: {run[3]}")
              for tc_id, tc in enumerate(run[1]):
                  if tc["result"] == "FAIL":
                      log.error(f"TC {tc_id+1}/{run[1].__len__()}. {tc}")
              log.info("-----------------------------------------------------------------------------------------"
                       "------------------")
      log.error(f"{failed_runs}/{runs.__len__()} [failed runs / attempts]")
      log.error(f"Finished main() with exit_code=1")
      exit(1)
    else:
      log.info(f"SUCCESS: {failed_runs}/{runs.__len__()} [failed runs / attempts]")
      log.info(f"Finished main() with exit_code=0")
      exit(0)
  else:
    log.info("----------------------------------------------------------------------------------------------------"
             "-------")
    run = simulate(log, tf, ps, synth, arguments, tcl_script)
    if run[0]:  # FAILED RUN
      log.error(f"Run FAILED")
      log.error(f"Config: {run[3]}")
      for tc_id, tc in enumerate(run[1]):
          if tc["result"] == "FAIL":
              log.error(f"TC {tc_id + 1}/{run[1].__len__()}. {tc}")
      log.info("-----------------------------------------------------------------------------------------"
               "------------------")
    log.info(f"RESULTS: {run[2]}/{run[1].__len__()} [failed runs / attempts]")
    log.info(f"Finished main() with exit_code={run[0]}")
    exit(run[0])


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Mesh XY NOC Testbench Run & Verify.')
  parser.add_argument('-tf', default=0, action="store_const", const=1,
                      help='TestFactory() for some testcases. Not enabled by Default')
  parser.add_argument('-ps', default=0, action="store_const", const=1,
                      help='run simulation using a post-synth netlist. Not enabled by Default')
  parser.add_argument('-synth', default=0, action="store_const", const=1,
                      help='rerun the synthesis using parameter values taken from arguments. Not enabled by Default')
  parser.add_argument('-row_n', default=3, help='ROW_N parameter')
  parser.add_argument('-col_m', default=3, help='COL_M parameter')
  parser.add_argument('-ff_depth', default=2, help='FIFO_DEPTH_W parameter')
  parser.add_argument('-channel_w', default=10, help='CHANNEL_W parameter')
  parser.add_argument('-regression', default=0, help="IF '1' RUNS NOC simulations from 2x2 to 4x4"
                                                     " to check size problems")
  parser.add_argument('-log_lvl', default=1, help="Logging LEVEL (INFO=0, DEBUG=1)")

  args = parser.parse_args()

  if args.ps:
    metrics_filename = f"mesh_noc_wh_xy_postsynth_{args.row_n}_{args.col_m}" \
                       f"_{args.ff_depth}_{args.channel_w}.json"
  else:
    metrics_filename = f"mesh_noc_wh_xy_presynth_{args.row_n}_{args.col_m}" \
                       f"_{args.ff_depth}_{args.channel_w}.json"

  if args.tf is False:
   if os.path.exists(metrics_filename):
      os.remove(metrics_filename)

  os.environ['METRICS_FILENAME'] = metrics_filename

  try:
    main(**vars(parser.parse_args()))
  except KeyboardInterrupt:
    print("ERROR: KEYBOARD INTERRUPT OCCURED, KILLING VVPs")
    subprocess.run(["killall", "vvp"])
    exit(0)
