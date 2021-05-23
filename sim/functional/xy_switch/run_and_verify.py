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


def simulate(log, tf=0, port_n=5, pckt_data_w=8, fifo_depth_w=2, row_cord=1, col_cord=1,
             row_addr_w=2, col_addr_w=2):
    arguments = {"PORT_N": port_n,
                 "PCKT_DATA_W": pckt_data_w,
                 "ROW_CORD": row_cord,
                 "COL_CORD": col_cord,
                 "ROW_ADDR_W": row_addr_w,
                 "COL_ADDR_W": col_addr_w,
                 "FIFO_DEPTH_W": fifo_depth_w}

    pwd = os.getcwd()
    git_root = get_git_root(os.getcwd())

    failed_testcases = 0
    testcases = []

    cmd = ["make", "-j12", "-B", f"TESTFACTORY={tf}"]
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
        return [1, testcases, failed_testcases, arguments]
    else:
        return [0, testcases, failed_testcases, arguments]


def main(tf, port_n, pckt_data_w, fifo_depth_w, row_cord, col_cord,
             row_addr_w, col_addr_w, log_lvl) -> None:
    log = get_logger(__name__, int(log_lvl))
    log.info(f"RUN {time.asctime()}")
    log.info("----------------------------------------------------------------------------------------------------"
             "-------")
    run = simulate(log, tf, port_n, pckt_data_w, fifo_depth_w, row_cord, col_cord,
                 row_addr_w, col_addr_w)
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
