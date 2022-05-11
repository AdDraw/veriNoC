import subprocess
import time
import argparse
from utils.rav import *
from utils.logger import *


def main(tf, ps, synth, log_lvl, ff_depth, data_w) -> None:
  log = get_logger(__name__, int(log_lvl))
  log.info(f"RUN {time.asctime()}")

  tcl_script = "fifo_synth.tcl"
  arguments = {"FIFO_DEPTH_W": ff_depth,
               "DATA_W": data_w}

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
  parser.add_argument('-log_lvl', default=1, help="Logging LEVEL (INFO=0, DEBUG=1)")

  parser.add_argument('-ff_depth', default=2, help='FIFO_DEPTH_W parameter')
  parser.add_argument('-data_w', default=10, help='DATA_W parameter')

  args = parser.parse_args()

  try:
    main(**vars(parser.parse_args()))
  except KeyboardInterrupt:
    print("ERROR: KEYBOARD INTERRUPT OCCURED, KILLING VVPs")
    subprocess.run(["killall", "vvp"])
    exit(0)
