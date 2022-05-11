import subprocess
import time
import argparse
from utils.logger import *
from utils.rav import *

def main(tf, ps, synth, port_n, pckt_data_w, fifo_depth_w, row_cord, col_cord,
             row_addr_w, col_addr_w, log_lvl) -> None:
  log = get_logger(__name__, int(log_lvl))
  log.info(f"RUN {time.asctime()}")
  log.info("----------------------------------------------------------------------------------------------------"
           "-------")

  tcl_script = "sw_xy_synth.tcl"
  arguments = {"PORT_N": port_n,
               "PCKT_DATA_W": pckt_data_w,
               "ROW_CORD": row_cord,
               "COL_CORD": col_cord,
               "ROW_ADDR_W": row_addr_w,
               "COL_ADDR_W": col_addr_w,
               "FIFO_DEPTH_W": fifo_depth_w}

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
  parser = argparse.ArgumentParser(description='Mesh XY Node Testbench Run & Verify.')
  parser.add_argument('-tf', default=0, action="store_const", const=1,
                      help='TestFactory() for some testcases. Not enabled by Default')
  parser.add_argument('-ps', default=0, action="store_const", const=1,
                      help='run simulation using a post-synth netlist. Not enabled by Default')
  parser.add_argument('-synth', default=0, action="store_const", const=1,
                      help='rerun the synthesis using parameter values taken from arguments. Not enabled by Default')

  parser.add_argument('-port_n', default=5,       help='Width of the Flit ID part(default=2)')
  parser.add_argument('-pckt_data_w', default=16, help='Width of the Data part of the FLIT(default=8)')
  parser.add_argument('-fifo_depth_w', default=2, help='Virtual Channel Depth Width(default=2)')
  parser.add_argument('-row_cord', default=1,     help='Row Coordinate of the NODE(def=1)')
  parser.add_argument('-col_cord', default=1,     help='Cow Coordinate of the NODE(def=1)')
  parser.add_argument('-row_addr_w', default=4,   help='Width of Row Address(def=2)')
  parser.add_argument('-col_addr_w', default=4,   help='Width of Col Address(def=2)')

  parser.add_argument('-log_lvl', default=1, help="Logging LEVEL (INFO=0, DEBUG=1)")

  args = parser.parse_args()

  try:
      main(**vars(parser.parse_args()))
  except KeyboardInterrupt:
      subprocess.run(["killall", "vvp"])
