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


def simulate(log, tf=0, ps=0, synth=0, row_n=3, col_m=3, ff_depth=4, pckt_w=8):
    arguments = {"tf": tf, "ps": ps,
                 "synth": synth, "row_n": row_n,
                 "col_m": col_m, "ff_depth": ff_depth,
                 "pckt_w": pckt_w}
    pwd = os.getcwd()
    git_root = get_git_root(os.getcwd())
    tcl_script = "mesh_xy_noc.tcl"

    failed_testcases = 0
    testcases = []
    if synth and ps:
        log.debug(f"ReSynthesize! {tcl_script}")
        os.chdir(f"{git_root}/synth")
        synth_cmd = [f"{git_root}/synth/yosys_wrapper.sh", f"-sf", f"{tcl_script}", f"ROW_N={int(row_n)}",
                     "--no-xdot", f"COL_M={int(col_m)}", f"FIFO_DEPTH_W={int(ff_depth)}",
                     f"PCKT_DATA_W={int(pckt_w)}"]
        log.debug(f"Synth Command: {synth_cmd}")
        subprocess.run(synth_cmd)
        os.chdir(pwd)

    cmd = ["make", "-j12", "-B", f"TESTFACTORY={tf}", f"SYNTH={ps}", f"ROW_N={int(row_n)}",
           f"COL_M={int(col_m)}", f"FIFO_DEPTH_W={int(ff_depth)}", f"PCKT_DATA_W={int(pckt_w)}"]

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


def main(tf, ps, synth, row_n, col_m, ff_depth, pckt_w, regression, log_lvl) -> None:
    log = get_logger(__name__, int(log_lvl))
    log.info(f"RUN {time.asctime()}")
    if regression:
        runs = []
        failed_runs = 0
        row_max = 4
        col_max = 4
        for ri in range(2, row_max + 1):
            for ci in range(2, col_max + 1):
                runs.append(simulate(log, tf, ps, synth, row_n, col_m, ff_depth, pckt_w))
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
        run = simulate(log, tf, ps, synth, row_n, col_m, ff_depth, pckt_w)
        if run[0]:  # FAILED RUN
            log.error(f"Run FAILED")
            log.error(f"Config: {run[3]}")
            for tc_id, tc in enumerate(run[1]):
                if tc["result"] == "FAIL":
                    log.error(f"TC {tc_id + 1}/{run[1].__len__()}. {tc}")
            log.info("-----------------------------------------------------------------------------------------"
                     "------------------")
        log.info(f"SUCCESS: {run[2]}/{run[1].__len__()} [failed runs / attempts]")
        log.info(f"Finished main() with exit_code={run[0]}")
        exit(run[0])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Mesh XY NOC Testbench Run & Verify.')
    parser.add_argument('-tf', default=0, help='Set value to 1 if you want to enable'
                                               ' TestFactory() for some testcases by default = 0')
    parser.add_argument('-ps', default=0, help='Set value to 1 if you want to enable'
                                               ' run simulation using a post-synth netlist by default = 0')
    parser.add_argument('-synth', default=0, help='Set value to 1 if you want to enable'
                                                  ' run simulation using a post-synth netlist by default = 0')
    parser.add_argument('-row_n', default=2, help='ROW_N parameter')
    parser.add_argument('-col_m', default=2, help='COL_M parameter')
    parser.add_argument('-ff_depth', default=4, help='FIFO_DEPTH_W parameter')
    parser.add_argument('-pckt_w', default=10, help='PCKT_DATA_W parameter')
    parser.add_argument('-regression', default=0, help="IF '1' RUNS NOC simulations from 2x2 to 4x4")
    parser.add_argument('-log_lvl', default=1, help="Logging LEVEL (INFO=0, DEBUG=1)")
    main(**vars(parser.parse_args()))
