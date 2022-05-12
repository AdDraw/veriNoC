import cocotb
from cocotb.clock import Clock
from cocotb.result import TestSuccess, TestError, TestFailure
from cocotb.triggers import ClockCycles, RisingEdge, ReadOnly, FallingEdge, First
from cocotb.binary import BinaryValue
from cocotb.log import SimLog
from cocotb.regression import TestFactory

from driver import AllocDriver

import os
from collections import Counter

from random import getrandbits
from logging import INFO, DEBUG
from math import log

CLOCK_PERIOD_NS = int(os.environ["CLK_PERIOD"])


class AllocTB:
    def __init__(self, dut, log_lvl=INFO):
        self.dut = dut
        self.log = SimLog("alloctb")
        self.log.setLevel(log_lvl)

        self.config = {
            "in_n": int(os.environ["IN_N"]),
            "out_m": int(os.environ["OUT_M"]),
            "flit_id_w": int(os.environ["FLIT_ID_W"]),
            "out_chan_id": int(os.environ["OUT_CHAN_ID"]),
            "rtr_res_w": log(int(os.environ["OUT_M"]), 2),
            "chan_sel_w": log(int(os.environ["IN_N"]), 2)
        }

        assert self.dut.IN_N == self.config["in_n"], "Bad Value"
        assert self.dut.OUT_M == self.config["out_m"], "Bad Value"
        assert self.dut.FLIT_ID_W == self.config["flit_id_w"], "Bad Value"
        assert self.dut.OUT_CHAN_ID == self.config["out_chan_id"], "Bad Value"

        self.drv = AllocDriver(dut, "", dut.clk_i, self.config, log_lvl)
        self.packets_to_send = []
        self.packets_received = []

    def populate_packets_to_send(self, packet_n=10, packet_length=4):
        for i in range(packet_n):
            packet = [self.random_header_flit(self.row_addr_w, self.col_addr_w)]
            for j in range(packet_length-1):
                packet.append(self.random_body_flit(self.config["flit_data_w"]))  # body / payload
            packet.append(self.random_body_flit(self.config["flit_data_w"], flit_id="11"))  # tail
            self.packets_to_send.append(packet)

    def random_header_flit(self, row_addr_w, col_addr_w, header_id="10"):
        assert (row_addr_w + col_addr_w + len(header_id)) == self.config["flit_w"], "Total lenght of Header Flit != FLIT_W"
        row_addr = BinaryValue(getrandbits(row_addr_w), row_addr_w, bigEndian=False).binstr
        col_addr = BinaryValue(getrandbits(col_addr_w), col_addr_w, bigEndian=False).binstr
        header_flit = header_id + row_addr + col_addr
        return BinaryValue(header_flit, len(header_flit), bigEndian=False).integer

    def random_body_flit(self, data_w, flit_id="01"):
        assert (data_w + len(flit_id)) == self.config["flit_w"], "Total lenght of Header Flit != FLIT_W"
        data = BinaryValue(getrandbits(data_w), data_w, bigEndian=False).binstr
        flit = flit_id + data
        return BinaryValue(flit, len(flit), bigEndian=False).integer

    def setup_dut(self, cycle_n):
        cocotb.fork(self.drv.reset())
        cocotb.fork(Clock(self.dut.clk_i, CLOCK_PERIOD_NS).start(cycles=cycle_n))

    async def AllocReader(self): # TODO: UPDATE TO ALLOCATOR
        risedge = RisingEdge(self.dut.clk_i)
        rdonly = ReadOnly()
        packet = []
        while True:
            await risedge
            await rdonly
            if self.dut.data_vld_o.value == 1:
                if self.dut.data_o.value.binstr[0:2] == "10":  # header
                    packet = []
                    await FallingEdge(self.dut.clk_i)
                    self.dut.chan_rdy_i <= 1
                    self.dut.chan_alloc_i <= 1
                packet.append(int(self.dut.data_o.value))
                if self.dut.data_o.value.binstr[0:2] == "11": # tail
                    self.packets_received.append(packet)
                    await FallingEdge(self.dut.clk_i)
                    self.dut.chan_rdy_i <= 0
                    self.dut.chan_alloc_i <= 0
                    if self.packets_received.__len__() == self.packets_to_send.__len__():
                        break

        self.dut.chan_rdy_i <= 0
        self.dut.chan_alloc_i <= 0

    def compare(self):
        mismatches = 0

        if self.packets_received.__len__() != self.packets_to_send.__len__():
            self.log.error(f"Not enough packets were received")
            raise TestFailure

        for pr_id, packet_r in enumerate(self.packets_received):
            if Counter(packet_r) != Counter(self.packets_to_send[pr_id]):
                mismatches += 1

        if mismatches > 0:
            self.log.error(f"Mismatches occured {mismatches}/{self.packets_to_send.__len__()}")
            for pr_id, packet_r in enumerate(self.packets_received):
                if Counter(packet_r) != Counter(self.packets_to_send[pr_id]):
                    self.log.info(f"{packet_r} != {self.packets_to_send[pr_id]}")
            raise TestFailure
        else:
            self.log.info(f"All {self.packets_to_send.__len__()} packets were sent and received properly")
            raise TestSuccess


@cocotb.test()
async def simple_test(dut, log_lvl=INFO, cycles=10000):
    cocotb.log.info("----------------------------------------------------------------------------- Simulation Started!")
    alloctb = AllocTB(dut, log_lvl)
    alloctb.setup_dut(cycle_n=cycles)
    await ClockCycles(dut.clk_i, 10)
    await alloctb.drv.send()
    await ClockCycles(dut.clk_i, 100)
    raise TestSuccess("Sim finished sucessfully")


# @cocotb.test()
# async def random_test(dut, log_lvl=INFO, packet_n=10, packet_length=4, cycles=10000):
#     """
#     We send N packets to the Virtual Channel.
#     Simple DataReader tooks out data from VC for comparison with send data.
#
#     :param dut: Design Under test, should be tb (but under tb wrapper there is vritual channel module)
#     :param log_lvl: INFO or DEBUG
#     :param cycles: maximum number of cycles this testcase can run for
#     :return: nothing ( testcase result is stored in 'results.xml' file )
#     """
#     cocotb.log.info(
#         "----------------------------------------------------------------------------- Simulation Started!")
#     alloctb = VCTB(dut, log_lvl)
#     alloctb.setup_dut(cycle_n=cycles)
#     await ClockCycles(dut.clk_i, 10)
#     clocks = cocotb.fork(ClockCycles(dut.clk_i, packet_length*packet_n*1000)._wait())
#     alloctb.populate_packets_to_send(packet_n=packet_n, packet_length=packet_length)
#
#     vc_reader = cocotb.fork(alloctb.VCReader())
#     for packet in alloctb.packets_to_send:
#         await alloctb.vc_drv.send_packet(packet)
#
#     await First(clocks, vc_reader)
#     alloctb.compare()
#
# tf = TestFactory(random_test)
# tf.add_option("packet_n", [10, 100, 200, 500])
# tf.add_option("packet_length", [2, 4, 10])
# tf.generate_tests()
