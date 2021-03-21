import subprocess
import xml.etree.ElementTree as ET

row_max = 6
col_max = 6

fail_testcases = []
testcase_cnt = 0

for ri in range(2, row_max+1):
    for ci in range(2, col_max+1):
        sim_build = f"meshtb_{ri}_{ci}"
        results_file = f"{sim_build}/results{ri}_{ci}.xml"
        vcd_name = f"{sim_build}/dump_{ri}_{ci}.vcd"
        subprocess.run(["make", "-j12", "-B",
                        f"ROW_N={ri}", f"COL_M={ci}",
                        "TESTFACTORY=1",
                        f"SIM_BUILD={sim_build}",
                        f"COCOTB_RESULTS_FILE={results_file}",
                        f"VCD_NAME={vcd_name}"])
        tree = ET.parse(results_file)
        root = tree.getroot()
        for testsuite in root:
            for testcase in testsuite:
                testcase_cnt += 1
                if testcase.__len__() > 0:
                    fail_testcases.append({"call": f"make -j12 -B ROW_N={ri} COL_M={ci} TESTFACTORY=1",
                                           "testcase": testcase.attrib})

print("-----------------------------------------------------------------------------------------------------------")
if fail_testcases.__len__() > 0:
    print(f"------------------------------- REGRESSION.PY {fail_testcases.__len__()}/{testcase_cnt} runs have failed"
          f" :( -------------------------------------")
    for ftc_id, failed_tc in enumerate(fail_testcases):
        print(f"{ftc_id}: {failed_tc} failed")
    print("-----------------------------------------------------------------------------------------------------------")
    exit(1)
else:
    print(f"-------------------------------- REGRESSION.PY Every run succedded!"
          f" ---------------------------------------")
    print("-----------------------------------------------------------------------------------------------------------")
    exit(0)