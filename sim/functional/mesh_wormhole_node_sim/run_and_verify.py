import subprocess
import os
import time
import xml.etree.ElementTree as ET
import argparse
from adam_logger import get_logger, get_git_root


def simulate(log, tf=0, ps=0, synth=0, in_n=5, out_m=5, flit_data_w=8, flit_id_w=2, row_cord=1,
             col_cord=1, hop_cnt_w=4, row_addr_w=2, col_addr_w=2, buffer_depth_w=2):
    arguments = {"IN_N": in_n,
                 "OUT_M": out_m,
                 "FLIT_DATA_W": flit_data_w,
                 "FLIT_ID_W": flit_id_w,
                 "ROW_CORD": row_cord,
                 "COL_CORD": col_cord,
                 "ROW_ADDR_W": row_addr_w,
                 "COL_ADDR_W": col_addr_w,
                 "HOP_CNT_W": hop_cnt_w,
                 "BUFFER_DEPTH_W": buffer_depth_w}

    pwd = os.getcwd()
    git_root = get_git_root(os.getcwd())
    tcl_script = "mesh_wormhole_node.tcl"

    failed_testcases = 0
    testcases = []
    if synth and ps:
        log.debug(f"ReSynthesize! {tcl_script}")
        os.chdir(f"{git_root}/synth")

        synth_cmd = [f"{git_root}/synth/yosys_wrapper.sh", f"-sf", f"{tcl_script}",
                     "--no-xdot"]
        for arg in arguments.items():
            synth_cmd.append(f"{arg[0]}={arg[1]}")

        log.debug(f"Synth Command: {synth_cmd}")
        subprocess.run(synth_cmd)
        os.chdir(pwd)

    cmd = ["make", "-j12", "-B", f"TESTFACTORY={tf}", f"SYNTH={ps}"]
    for arg in arguments.items():
        cmd.append(f"{arg[0]}={arg[1]}")

    log.debug(f"Command {cmd}")
    subprocess.run(cmd)
    tree = ET.parse("results.xml")
    root = tree.getroot()
    for testsuite in root:
        for testcase in testsuite:
            if testcase.attrib["name"] != "random_seed":
                if testcase.__len__() > 0:
                    testcases.append({"result": "FAIL", "testcase": testcase.attrib})
                    failed_testcases += 1
                else:
                    testcases.append({"result": "PASS", "testcase": testcase.attrib})

    if failed_testcases > 0:
        return [1, testcases, failed_testcases, args]
    else:
        return [0, testcases, failed_testcases, args]


def main(tf, ps, synth, in_n, out_m, flit_data_w, flit_id_w, row_cord,
         col_cord, hop_cnt_w, row_addr_w, col_addr_w, buffer_depth_w, log_lvl) -> None:
    log = get_logger(__name__, int(log_lvl))
    log.info(f"RUN {time.asctime()}")
    log.info("----------------------------------------------------------------------------------------------------"
             "-------")
    run = simulate(log, tf, ps, synth, in_n, out_m, flit_data_w, flit_id_w, row_cord,
                   col_cord, hop_cnt_w, row_addr_w, col_addr_w, buffer_depth_w)
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
    parser.add_argument('-tf', default=0, help='Set value to 1 if you want to enable'
                                               ' TestFactory() for some testcases. Not enabled by Default')
    parser.add_argument('-ps', default=0, help='Set value to 1 if you want to enable'
                                               ' run simulation using a post-synth netlist. Not enabled by Default')
    parser.add_argument('-synth', default=0, help='Set value to 1 if you want to rerun the synthesis using'
                                                  ' parameter values taken from arguments. Not enabled by Default')
    parser.add_argument('-in_n', default=5,         help='number of input channels(default=5)')
    parser.add_argument('-out_m', default=5,        help='number of output channels(default=5)')
    parser.add_argument('-flit_id_w', default=2,    help="Width of Flit's ID part(default=2)")
    parser.add_argument('-flit_data_w', default=8,  help="Width of Flit's data part(default=8)")
    parser.add_argument('-hop_cnt_w', default=4,    help='Hop Count width of the Header flit(default=4)')
    parser.add_argument('-row_cord', default=1,     help='Row Coordinate of the NODE(def=1)')
    parser.add_argument('-col_cord', default=1,     help='Cow Coordinate of the NODE(def=1)')
    parser.add_argument('-row_addr_w', default=2,    help='Width of Row Address(def=2)')
    parser.add_argument('-col_addr_w', default=2,    help='Width of Col Address(def=2)')
    parser.add_argument('-buffer_depth_w', default=2,    help='Buffer Depth Width(def=2)')
    parser.add_argument('-log_lvl', default=1, help="Logging LEVEL (INFO=0, DEBUG=1)")

    args = parser.parse_args()

    try:
        main(**vars(parser.parse_args()))
    except KeyboardInterrupt:
        print("ERROR: KEYBOARD INTERRUPT OCCURED, KILLING VVPs")
        subprocess.run(["killall", "vvp"])
        exit(0)