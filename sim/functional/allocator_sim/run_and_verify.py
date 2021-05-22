import subprocess
import os
import time
import xml.etree.ElementTree as ET
import argparse
import git
import logging
import sys
from logging.handlers import TimedRotatingFileHandler, RotatingFileHandler
FORMATTER = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(funcName)s — %(message)s")
LOG_FILE = "sim.log"


def get_git_root(path):
    git_repo = git.Repo(path, search_parent_directories=True)
    git_root_t = git_repo.git.rev_parse("--show-toplevel")
    return git_root_t


def get_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    return console_handler


def get_file_handler():
    file_handler = RotatingFileHandler(LOG_FILE, mode='w', backupCount=6)
    file_handler.setFormatter(FORMATTER)
    return file_handler


def get_logger(logger_name, log_lvl):
    logger = logging.getLogger(logger_name)
    if log_lvl:
        logger.setLevel(logging.DEBUG) # better to have too much log than not enough
    else:
        logger.setLevel(logging.INFO)
    logger.addHandler(get_console_handler())
    logger.addHandler(get_file_handler())
    # with this pattern, it's rarely necessary to propagate the error up to parent
    logger.propagate = False
    return logger


def simulate(log, tf=0, ps=0, synth=0, in_n=5, out_m=5, flit_id_w=2, hop_cnt_w=4, out_chan_id=1):
    arguments = {"tf": tf, "ps": ps,
                 "synth": synth, "in_n": in_n, "out_m": out_m,
                 "flit_id_w": flit_id_w, "hop_cnt_w": hop_cnt_w,
                 "out_chan_id": out_chan_id}

    pwd = os.getcwd()
    git_root = get_git_root(os.getcwd())
    tcl_script = "allocator.tcl"

    failed_testcases = 0
    testcases = []
    if synth and ps:
        log.debug(f"ReSynthesize! {tcl_script}")
        os.chdir(f"{git_root}/synth")
        synth_cmd = [f"{git_root}/synth/yosys_wrapper.sh", f"-sf", f"{tcl_script}", f"IN_N={int(in_n)}",
                     "--no-xdot", f"HOP_CNT_W={int(hop_cnt_w)}", f"FLIT_ID_W={int(flit_id_w)}",
                    f"OUT_CHAN_ID={int(out_chan_id)}", f"OUT_M={int(out_m)}"]
        log.debug(f"Synth Command: {synth_cmd}")
        subprocess.run(synth_cmd)
        os.chdir(pwd)

    cmd = ["make", "-j12", "-B", f"TESTFACTORY={tf}", f"SYNTH={ps}",
           f"IN_N={int(in_n)}", f"HOP_CNT_W={int(hop_cnt_w)}",
           f"FLIT_ID_W={int(flit_id_w)}", f"OUT_CHAN_ID={int(out_chan_id)}",
           f"OUT_M={int(out_m)}"]

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
        return [1, testcases, failed_testcases, arguments]
    else:
        return [0, testcases, failed_testcases, arguments]


def main(tf, ps, synth, in_n, out_m, flit_id_w, hop_cnt_w, out_chan_id, log_lvl) -> None:
    log = get_logger(__name__, int(log_lvl))
    log.info(f"RUN {time.asctime()}")
    log.info("----------------------------------------------------------------------------------------------------"
             "-------")
    run = simulate(log, tf, ps, synth, in_n, out_m, flit_id_w, hop_cnt_w, out_chan_id)
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
    parser.add_argument('-hop_cnt_w', default=4,    help='Hop Count width of the Header flit(default=4)')
    parser.add_argument('-out_chan_id', default=1,  help='Id of the output channel associated with the Allocator(default=1)')

    parser.add_argument('-log_lvl', default=1, help="Logging LEVEL (INFO=0, DEBUG=1)")

    args = parser.parse_args()

    main(**vars(parser.parse_args()))
