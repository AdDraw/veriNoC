import subprocess
import xml.etree.ElementTree as ET
import argparse
import os

parser = argparse.ArgumentParser(description='FIFO Testbench Run & Verify.')
parser.add_argument('-ps', default=0, help='Set value to 1 if you want to enable'
                                           ' run simulation using a post-synth netlist by default = 0')

args = parser.parse_args()
print(f"Arguments: {args}")

failed_testcases = 0
testcases = []
subprocess.run(["make", "-j12", "-B", f"SYNTH={args.ps}"])
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

print("-----------------------------------------------------------------------------------------------------------")
if failed_testcases > 0:
    print(f"------------------------------- Run & Verify"
          f" {failed_testcases}/{testcases.__len__()} runs have failed"
          f" :( -------------------------------------")
    for ftc_id, failed_tc in enumerate(testcases):
        if failed_tc["result"] == "FAIL":
            print(f"{ftc_id}: {failed_tc}")
    print("-----------------------------------------------------------------------------------------------------------")
    print("Exit Code 1")
    exit(1)
else:
    print(f"-------------------------------- REGRESSION.PY Every run succedded!"
          f" {testcases.__len__()}/{testcases.__len__()}"
          f" ---------------------------------------")

    for tc in testcases:
        print(tc)

    print("-----------------------------------------------------------------------------------------------------------")
    print("Exit Code 0")
    exit(0)
