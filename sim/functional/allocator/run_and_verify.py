import time
import argparse
from utils.logger import *
from utils.rav import simulate


def main(tf, ps, synth, in_n, out_m, flit_id_w, out_chan_id, log_lvl) -> None:
  log = get_logger(__name__, int(log_lvl))
  log.info(f"RUN {time.asctime()}")
  log.info("----------------------------------------------------------------------------------------------------"
           "-------")
  tcl_script = "allocator.tcl"
  arguments = {"IN_N": in_n,
               "OUT_M": out_m,
               "FLIT_ID_W": flit_id_w,
               "OUT_CHAN_ID": out_chan_id}

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
  parser = argparse.ArgumentParser(description='Allocator Run & Verify.')
  parser.add_argument('-tf', default=0, action="store_const", const=1,
                      help='TestFactory() for some testcases. Not enabled by Default')
  parser.add_argument('-ps', default=0, action="store_const", const=1,
                      help='run simulation using a post-synth netlist. Not enabled by Default')
  parser.add_argument('-synth', default=0, action="store_const", const=1,
                      help='rerun the synthesis using parameter values taken from arguments. Not enabled by Default')
  parser.add_argument('-in_n', default=5,         help='number of input channels(default=5)')
  parser.add_argument('-out_m', default=5,        help='number of output channels(default=5)')
  parser.add_argument('-flit_id_w', default=2,    help="Width of Flit's ID part(default=2)")
  parser.add_argument('-out_chan_id', default=1,  help='Id of the output channel associated with the Allocator(default=1)')

  parser.add_argument('-log_lvl', default=1, help="Logging LEVEL (INFO=0, DEBUG=1)")

  args = parser.parse_args()

  main(**vars(parser.parse_args()))
