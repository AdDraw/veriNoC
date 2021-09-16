import os
import subprocess
import xml.etree.ElementTree as ElTree
from utils.adam_logger import *
FORMATTER = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(funcName)s — %(message)s")
LOG_FILE = "sim.log"


def simulate(log, tf, ps, synth, parameters, tcl_script):
    pwd = os.getcwd()
    git_root = get_git_root(os.getcwd())

    failed_testcases = 0
    testcases = []
    if synth and ps:
        log.debug(f"ReSynthesize! {tcl_script}")
        os.chdir(f"{git_root}/synth")

        synth_cmd = [f"{git_root}/synth/yosys_wrapper.sh", f"-sf", f"{tcl_script}",
                     "--no-xdot"]
        for arg in parameters.items():
            synth_cmd.append(f"{arg[0]}={arg[1]}")

        log.debug(f"Synth Command: {synth_cmd}")
        subprocess.run(synth_cmd)
        os.chdir(pwd)

    cmd = ["make", "sim", "-j12", "-B", f"TESTFACTORY={tf}", f"SYNTH={ps}"]
    for arg in parameters.items():
        cmd.append(f"{arg[0]}={arg[1]}")

    log.debug(f"Command {cmd}")
    subprocess.run(cmd)
    tree = ElTree.parse("results.xml")
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
        return [1, testcases, failed_testcases, parameters]
    else:
        return [0, testcases, failed_testcases, parameters]
