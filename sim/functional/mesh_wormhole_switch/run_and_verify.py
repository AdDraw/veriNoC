import subprocess
import time
import argparse
from utils.logger import get_logger
from utils.rav import simulate


def main(tf, ps, synth, node_radix, flit_data_w, flit_id_w, row_cord,
         col_cord, row_addr_w, col_addr_w, buffer_depth_w, arb_type, log_lvl) -> None:
    log = get_logger(__name__, int(log_lvl))
    log.info(f"RUN {time.asctime()}")
    log.info("----------------------------------------------------------------------------------------------------"
             "-------")

    tcl_script = "mesh_wormhole_node.tcl"
    arguments = {"NODE_RADIX": node_radix,
                 "FLIT_DATA_W": flit_data_w,
                 "FLIT_ID_W": flit_id_w,
                 "ROW_CORD": row_cord,
                 "COL_CORD": col_cord,
                 "ROW_ADDR_W": row_addr_w,
                 "COL_ADDR_W": col_addr_w,
                 "BUFFER_DEPTH_W": buffer_depth_w,
                 "ARB_TYPE": arb_type}

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
    parser = argparse.ArgumentParser(description='Mesh WORMHOLE XY NOC NODE Testbench Run & Verify.')
    parser.add_argument('-tf', default=0, action="store_const", const=1,
                        help='TestFactory() for some testcases. Not enabled by Default')
    parser.add_argument('-ps', default=0, action="store_const", const=1,
                        help='run simulation using a post-synth netlist. Not enabled by Default')
    parser.add_argument('-synth', default=0, action="store_const", const=1,
                        help='rerun the synthesis using parameter values taken from arguments. Not enabled by Default')
    parser.add_argument('-node_radix', default=5,         help='node radix(default=5)')
    parser.add_argument('-flit_id_w', default=2,    help="Width of Flit's ID part(default=2)")
    parser.add_argument('-flit_data_w', default=8,  help="Width of Flit's data part(default=8)")
    parser.add_argument('-row_cord', default=1,     help='Row Coordinate of the NODE(def=1)')
    parser.add_argument('-col_cord', default=1,     help='Cow Coordinate of the NODE(def=1)')
    parser.add_argument('-row_addr_w', default=2,    help='Width of Row Address(def=2)')
    parser.add_argument('-col_addr_w', default=2,    help='Width of Col Address(def=2)')
    parser.add_argument('-buffer_depth_w', default=2,    help='Buffer Depth Width(def=2)')
    parser.add_argument('-arb_type', default=0, help="Arbitration Type(0-matrix, 1-round robin, 2-static")
    parser.add_argument('-log_lvl', default=1, help="Logging LEVEL (INFO=0, DEBUG=1)")

    args = parser.parse_args()

    try:
        main(**vars(parser.parse_args()))
    except KeyboardInterrupt:
        print("ERROR: KEYBOARD INTERRUPT OCCURED, KILLING VVPs")
        subprocess.run(["killall", "vvp"])
        exit(0)
