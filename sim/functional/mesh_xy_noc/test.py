# COCOTB imports
import cocotb
from cocotb.result import TestSuccess, TestFailure, TestError
from cocotb.triggers import ClockCycles, RisingEdge
from logging import INFO, DEBUG
from cocotb.log import SimLog
# Global Imports
import os
from random import sample
from math import log, ceil
# Modules
from Resource import Resource


class NocTB:
    """
        TB suite for a MESH NOC with XY Routing
        inputs are to be driven from RESOURCES DRIVERS
        outputs should be checked by the RESOURCE MONITORS

        1)  check if everything correctly landed into the correct DESTINATION
            dst is defined by X_ADDR & Y_ADDR and those need to be equal to X_CORD & Y_CORD
            of the RESOURCE

        TODO: 2) Check for DeadLocks & LiveLocks
        TODO: 3) Check Latency & Collect Measurements

        Mesh NoC has:
        - N Rows of switches
        - M Columns of switches
        - Each switch is connected to min 2 neighboring switches
        - XY routing

        Data from within the resource comes at the lowest priority.
    """
    def __init__(self, dut, log_lvl=INFO):
        self.dut = dut
        self.dut._discover_all()

        self.log = SimLog("noctb")
        self.log.setLevel(log_lvl)

        self.config = {
            "row_n": int(os.environ["ROW_N"]),
            "col_m": int(os.environ["COL_M"]),
            "pckt_data_w": int(os.environ["PCKT_DATA_W"]),
            "fifo_depth_w": int(os.environ["FIFO_DEPTH_W"]),
            "clk_period": int(os.environ["CLK_PERIOD"])
        }

        self.log.info(f"Created NocTB! {self.config}")

        self.received = []
        self.sent = []
        self.rsc_list = []
        self.resource_n = self.config["row_n"] * self.config["col_m"]
        self.clk_period = self.config["clk_period"]

        for row_id in range(self.config["row_n"]):
            for col_id in range(self.config["col_m"]):
                self.config_rsc = {
                    "row_n": int(os.environ["ROW_N"]),
                    "col_m": int(os.environ["COL_M"]),
                    "pckt_data_w": int(os.environ["PCKT_DATA_W"]),
                    "fifo_depth_w": int(os.environ["FIFO_DEPTH_W"]),
                    "packet_col_addr_w": ceil(log(int(os.environ["COL_M"]), 2)),
                    "packet_row_addr_w": ceil(log(int(os.environ["ROW_N"]), 2)),
                    "packet_w":  ceil(log(int(os.environ["COL_M"]), 2)) + ceil(log(int(os.environ["ROW_N"]), 2)) + int(os.environ["PCKT_DATA_W"]),
                    "col_cord": col_id,
                    "row_cord": row_id
                }

                self.rsc_list.append(Resource(dut, "", dut.clk_i, self.config_rsc, callback=self.mon_callback))

    def mon_callback(self, t):
        self.received.append(t)

    def setup_dut(self):
        cocotb.fork(self.reset_hdl())
        self.dut.rst_ni <= 0
        for i in range(self.rsc_list.__len__()):
            self.dut.rsc_pckt_i[i] <= 0
        self.dut.rsc_full_i <= 0
        self.dut.rsc_ovrflw_i <= 0
        self.dut.rsc_wren_i <= 0

    def reset_swtb(self):
        for rsc in self.rsc_list:
            rsc.clear_rsc_output(True)

    async def reset_hdl(self):
        await RisingEdge(self.dut.clk_i)
        self.dut.rst_ni <= 0

        await ClockCycles(self.dut.clk_i, 5)
        self.dut.rst_ni <= 1

    def compare(self):
        packets_sent = 0
        time_total = 0
        total_hops = 0
        min_time = pow(2, 20)
        max_time = -1
        shortest_path = pow(2, 20)
        longest_path = -1
        sent_and_received = []
        for rsc in self.rsc_list:
            packets_sent += rsc.sent_packets.__len__()

            for sent_pckt in rsc.sent_packets:
                self.sent.append(sent_pckt)
                self.log.debug(sent_pckt)

            for rec_pckt in rsc.received_pckts:
                self.log.debug(rec_pckt)

        self.log.info("------------------------------------------------------------------------- Final!")
        packets_received = self.received.__len__()
        if packets_received != packets_sent:
            raise TestFailure(f"Numbers of packets sent and received in the whole NOC is not the same "
                              f"rec: {packets_received} != sent: {packets_sent}")
        else:
            self.log.warning(f"Number of received packets matches the sent packet count rec/sent: "
                             f"{packets_received}/{packets_sent}")

            # check correctness (and what was sent and received)

            received_tmp = self.received
            for sent_pckt in self.sent:
                s_col_dest = sent_pckt["col_dest"]
                s_row_dest = sent_pckt["row_dest"]
                s_data = sent_pckt["data"]
                s_time = sent_pckt["time"]

                checked = 0
                for rp_idx, rec_pckt in enumerate(received_tmp):
                    r_col_dest = rec_pckt["col_dest"]
                    r_row_dest = rec_pckt["row_dest"]
                    r_data = rec_pckt["data"]
                    r_time = rec_pckt["time"]
                    if s_col_dest == r_col_dest and s_row_dest == r_row_dest and s_data == r_data:
                        received_tmp.pop(rp_idx)
                        time_diff = r_time - s_time

                        s_row_cord, s_col_cord = divmod(sent_pckt["source"],  self.config["col_m"])
                        r_row_cord, r_col_cord = divmod(rec_pckt["sink"], self.config["col_m"])

                        sent_and_received.append({"from": [sent_pckt["source"], s_row_cord, s_col_cord],
                                                  "to": [rec_pckt["sink"], r_row_cord, r_col_cord],
                                                  "time": time_diff})

                        if s_row_cord > r_row_cord:
                            vert_hops = s_row_cord - r_row_cord
                        else:
                            vert_hops = r_row_cord - s_row_cord
                        if s_col_cord > r_col_cord:
                            hor_hops = s_col_cord - r_col_cord
                        else:
                            hor_hops = r_col_cord - s_col_cord
                        hops_req = 1 + hor_hops + vert_hops
                        if hops_req < shortest_path:
                            shortest_path = hops_req
                        if hops_req > longest_path:
                            longest_path = hops_req

                        self.log.debug(sent_and_received[-1])

                        if time_diff < min_time:
                            min_time = time_diff
                        if time_diff > max_time:
                            max_time = time_diff

                        time_total += time_diff
                        total_hops += hops_req
                        checked = 1
                        break

                if not checked:
                    raise TestFailure(f"sent_packet not received {sent_pckt}")

            if sent_and_received.__len__() == self.sent.__len__():
                self.log.warning(f"All sent packets were properly received "
                                 f"{sent_and_received.__len__()}/{self.sent.__len__()}")

                mean_packet_life_ns = time_total/sent_and_received.__len__()
                mean_packet_life_cyc = mean_packet_life_ns/self.clk_period

                self.log.warning(f"Average packet lifetime: {mean_packet_life_ns} ns")
                self.log.warning(f"Average packet lifetime: {mean_packet_life_cyc} cycles "
                                 f"(CLK_PERIOD = {self.clk_period} ns)")

                self.log.warning(f"Min packet lifetime: {min_time} ns")
                self.log.warning(f"Max packet lifetime: {max_time} ns")

                self.log.warning(f"Total Hops {total_hops} (with included hops from Resource to Switch)")
                self.log.warning(f"Mean Time per Hop {time_total/total_hops} ns "
                                 f"| {(time_total/total_hops)/self.clk_period} cyc")

                self.log.warning(f"Longest packet path  {longest_path} hops")
                self.log.warning(f"Shortest packet path {shortest_path} hops")
                self.log.warning(f"Average packet path  {total_hops/self.sent.__len__()} hops")

        self.log.info("")
        raise TestSuccess()


@cocotb.test()
async def smoke_test(dut, log_lvl=INFO, cycles=100000):
    log = SimLog("smoke_test")
    log.setLevel(log_lvl)
    log.info("----------------------------------------------------------------------------- Setup!")
    if int(os.environ['DEBUG_ATTACH']) > 0:
        import pydevd_pycharm
        pydevd_pycharm.settrace('localhost', port=9090, stdoutToServer=True, stderrToServer=True)

    dut._discover_all()
    log.debug(dut._sub_handles)
    noctb = NocTB(dut, log_lvl)
    noctb.setup_dut()
    log.info("----------------------------------------------------------------------------- Simulation!")
    await ClockCycles(dut.clk_i, 100)
    # Edge LT
    # - send RT
    await noctb.rsc_list[0].send_packet_to_xy(1, 0, noctb.config["col_m"]-1)
    await noctb.rsc_list[0].clear_rsc_output(True)

    # - send LB
    await noctb.rsc_list[0].send_packet_to_xy(2, noctb.config["row_n"]-1, 0)
    await noctb.rsc_list[0].clear_rsc_output(True)
    # - send to Edge RB
    await noctb.rsc_list[0].send_packet_to_xy(3, noctb.config["row_n"]-1, noctb.config["col_m"]-1)
    await noctb.rsc_list[0].clear_rsc_output(True)

    # Edge LT
    # - send RT
    await noctb.rsc_list[-1].send_packet_to_xy(4, 0, noctb.config["col_m"]-1)
    await noctb.rsc_list[-1].clear_rsc_output(True)
    # - send LB
    await noctb.rsc_list[-1].send_packet_to_xy(5, noctb.config["row_n"]-1, 0)
    await noctb.rsc_list[-1].clear_rsc_output(True)
    # - send to Edge RB
    await noctb.rsc_list[-1].send_packet_to_xy(6, 0, 0)
    await noctb.rsc_list[-1].clear_rsc_output(True)

    await ClockCycles(dut.clk_i, 100)

    log.info("----------------------------------------------------------------------------- Results!")
    noctb.compare()


@cocotb.test()
async def test_allpaths_1(dut, log_lvl=INFO, cycles=100000):
    log = SimLog("test_all_paths_packet_doesnt_wait_in_fifo")
    log.setLevel(log_lvl)
    log.info("----------------------------------------------------------------------------- Setup!")
    if int(os.environ['DEBUG_ATTACH']) > 0:
        import pydevd_pycharm
        pydevd_pycharm.settrace('localhost', port=9090, stdoutToServer=True, stderrToServer=True)

    dut._discover_all()
    log.debug(dut._sub_handles)
    noctb = NocTB(dut, log_lvl)
    noctb.setup_dut()
    log.info("----------------------------------------------------------------------------- Simulation!")

    await ClockCycles(dut.clk_i, 100)
    # loop that goes over every reasource !

    if pow(noctb.rsc_list.__len__(), 2) > pow(2, noctb.config["pckt_data_w"]):
        raise TestError("Pckt Data Width is not big enough to provide unique ID to each packet")

    multipliers = sample(range(pow(2, noctb.config["pckt_data_w"])), noctb.rsc_list.__len__()*noctb.resource_n)
    for sending_rsc in noctb.rsc_list:
        sources = sample(noctb.rsc_list, noctb.rsc_list.__len__())
        for rec_rsc in sources:
            await sending_rsc.send_packet_to_xy(multipliers[0],
                                                rec_rsc.config["row_cord"],
                                                rec_rsc.config["col_cord"])
            multipliers.pop(0)
            await sending_rsc.clear_rsc_output(True)
            await ClockCycles(dut.clk_i, 1)

    await ClockCycles(dut.clk_i, pow(2, noctb.config["fifo_depth_w"]))

    log.info("----------------------------------------------------------------------------- Results!")
    noctb.compare()


@cocotb.test()
async def test_allpaths_2(dut, log_lvl=INFO, cycles=100000):
    log = SimLog("test_allpaths_pckt_waits_in_fifo")
    log.setLevel(log_lvl)

    log.info("----------------------------------------------------------------------------- Setup!")
    if int(os.environ['DEBUG_ATTACH']) > 0:
        import pydevd_pycharm
        pydevd_pycharm.settrace('localhost', port=9090, stdoutToServer=True, stderrToServer=True)

    dut._discover_all()
    log.debug(dut._sub_handles)
    noctb = NocTB(dut, log_lvl)
    noctb.setup_dut()
    log.info("----------------------------------------------------------------------------- Simulation!")

    await ClockCycles(dut.clk_i, 100)
    # loop that goes over every reasource !

    if pow(noctb.rsc_list.__len__(), 2) > pow(2, noctb.config["pckt_data_w"]):
        raise TestError("Pckt Data Width is not big enough to provide unique ID to each packet")

    multipliers = sample(range(pow(2, noctb.config["pckt_data_w"])), noctb.rsc_list.__len__()*noctb.resource_n)
    for sending_rsc in noctb.rsc_list:
        sources = sample(noctb.rsc_list, noctb.rsc_list.__len__())
        for rec_rsc in sources:
            await sending_rsc.send_packet_to_xy(multipliers[0],
                                                rec_rsc.config["row_cord"],
                                                rec_rsc.config["col_cord"])
            multipliers.pop(0)
        await sending_rsc.clear_rsc_output(True)

    await ClockCycles(dut.clk_i, pow(2, noctb.config["fifo_depth_w"]))

    log.info("----------------------------------------------------------------------------- Results!")
    noctb.compare()

