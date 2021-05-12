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


def simulate(log, tf=0, ps=0, synth=0, flit_id_w=2, data_w=8, vc_depth_w=2):
    arguments = {"tf": tf, "ps": ps,
                 "synth": synth, "flit_id_w": flit_id_w,
                 "data_w": data_w, "vc_depth_w": vc_depth_w}
    pwd = os.getcwd()
    git_root = get_git_root(os.getcwd())
    tcl_script = "virtual_channel.tcl"

    failed_testcases = 0
    testcases = []
    if synth and ps:
        log.debug(f"ReSynthesize! {tcl_script}")
        os.chdir(f"{git_root}/synth")
        synth_cmd = [f"{git_root}/synth/yosys_wrapper.sh", f"-sf", f"{tcl_script}", f"VC_DEPTH_W={int(vc_depth_w)}",
                     "--no-xdot", f"DATA_W={int(data_w)}", f"FLIT_ID_W={int(flit_id_w)}"]
        log.debug(f"Synth Command: {synth_cmd}")
        subprocess.run(synth_cmd)
        os.chdir(pwd)

    cmd = ["make", "-j12", "-B", f"TESTFACTORY={tf}", f"SYNTH={ps}", f"VC_DEPTH_W={int(vc_depth_w)}",
           f"DATA_W={int(data_w)}", f"FLIT_ID_W={int(flit_id_w)}"]

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


def main(tf, ps, synth, flit_id_w, data_w, vc_depth_w,log_lvl) -> None:
    log = get_logger(__name__, int(log_lvl))
    log.info(f"RUN {time.asctime()}")
    log.info("----------------------------------------------------------------------------------------------------"
             "-------")
    run = simulate(log, tf, ps, synth, flit_id_w, data_w, vc_depth_w)
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

    parser.add_argument('-flit_id_w', default=2, help='Width of the Flit ID part(default=2)')
    parser.add_argument('-data_w', default=8, help='Width of the Data part of the FLIT(default=8)')
    parser.add_argument('-vc_depth_w', default=2, help='Virtual Channel Depth Width(default=2)')

    parser.add_argument('-log_lvl', default=1, help="Logging LEVEL (INFO=0, DEBUG=1)")

    args = parser.parse_args()

    # if args.ps:
    #     metrics_filename = f"vc_postsynth_{args.flit_id_w}_{args.data_w}" \
    #                        f"_{args.vc_depth_w}.json"
    # else:
    #     metrics_filename = f"vc_presynth_{args.row_n}_{args.col_m}" \
    #                        f"_{args.ff_depth}_{args.pckt_w}.json"

    # if os.path.exists(metrics_filename):
    #     os.remove(metrics_filename)

    # os.environ['METRICS_FILENAME'] = metrics_filename

    main(**vars(parser.parse_args()))
