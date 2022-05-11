import cocotb
from cocotb.clock import Clock
from cocotb.result import TestSuccess, TestError, TestFailure
from cocotb.triggers import ClockCycles, RisingEdge, ReadOnly, FallingEdge, First
from cocotb.binary import BinaryValue
from cocotb.log import SimLog
from cocotb.regression import TestFactory

from driver import VCDriver
from utils.functions import *

import os
from collections import Counter

from random import getrandbits
from logging import INFO, DEBUG

CLOCK_PERIOD_NS = int(os.environ["CLK_PERIOD"])


class VCTB:
    def __init__(self, dut, log_lvl=INFO):
        self.dut = dut
        self.log = SimLog("vctb")
        self.log.setLevel(log_lvl)

        self.config = {
            "flit_data_w": int(os.environ["FLIT_DATA_W"]),
            "vc_depth_w": int(os.environ["VC_DEPTH_W"]),
            "flit_id_w": int(os.environ["FLIT_ID_W"]),
            "row_cord": int(os.environ["ROW_CORD"]),
            "col_cord": int(os.environ["COL_CORD"]),
            "col_addr_w": int(os.environ["COL_ADDR_W"]),
            "row_addr_w": int(os.environ["ROW_ADDR_W"]),
            "out_n_w":int(os.environ["OUT_N_W"]),
            "flit_w": int(os.environ["FLIT_DATA_W"]) + int(os.environ["FLIT_ID_W"])
        }

        # header FLIT parameters
        self.row_addr_w = self.config["row_addr_w"]
        self.col_addr_w = self.config["col_addr_w"]

        assert self.dut.FLIT_DATA_W == self.config["flit_data_w"], "Bad Value"
        assert self.dut.VC_DEPTH_W == self.config["vc_depth_w"], "Bad Value"
        assert self.dut.FLIT_ID_W == self.config["flit_id_w"], "Bad Value"
        assert self.dut.ROW_CORD == self.config["row_cord"], "Bad Value"
        assert self.dut.COL_CORD == self.config["col_cord"], "Bad Value"
        assert self.dut.COL_ADDR_W == self.config["col_addr_w"], "Bad Value"
        assert self.dut.ROW_ADDR_W == self.config["row_addr_w"], "Bad Value"
        assert self.dut.OUT_N_W == self.config["out_n_w"], "Bad Value"

        self.vc_drv = VCDriver(dut, "", dut.clk_i, self.config, log_lvl)
        self.packets_to_send = []
        self.packets_received = []
        self.dut.chan_rdy_i.setimmediatevalue(0x1F)

    def populate_packets_to_send(self, packet_n=10, packet_length=4):
        for i in range(packet_n):
            packet = [self.random_header_flit(self.row_addr_w, self.col_addr_w)]
            for j in range(packet_length-1):
                packet.append(self.random_body_flit(self.config["flit_data_w"]))  # body / payload
            packet.append(self.random_body_flit(self.config["flit_data_w"], flit_id="11"))  # tail
            self.packets_to_send.append(packet)

    def random_header_flit(self, row_addr_w, col_addr_w, header_id="10"):
        assert (row_addr_w + col_addr_w + len(header_id)) <= self.config["flit_w"], "Total lenght of Header Flit != FLIT_W"
        row_addr = BinaryValue(getrandbits(row_addr_w), row_addr_w, bigEndian=False).binstr
        col_addr = BinaryValue(getrandbits(col_addr_w), col_addr_w, bigEndian=False).binstr

        nuller = null_string(self.config["flit_w"] - len(header_id) - row_addr_w - col_addr_w)
        header_flit = header_id + row_addr + col_addr + nuller
        return BinaryValue(header_flit, len(header_flit), bigEndian=False).integer

    def random_body_flit(self, data_w, flit_id="01"):
        assert (data_w + len(flit_id)) == self.config["flit_w"], "Total lenght of Header Flit != FLIT_W"
        data = BinaryValue(getrandbits(data_w), data_w, bigEndian=False).binstr
        flit = flit_id + data
        return BinaryValue(flit, len(flit), bigEndian=False).integer

    def setup_dut(self, cycle_n):
        cocotb.fork(self.vc_drv.reset())
        cocotb.fork(Clock(self.dut.clk_i, CLOCK_PERIOD_NS).start(cycles=cycle_n))

    async def VCReader(self):
        risedge = RisingEdge(self.dut.clk_i)
        rdonly = ReadOnly()
        packet = []
        while self.packets_received.__len__() != self.packets_to_send.__len__():
            while True:
                await risedge
                await rdonly
                if self.dut.data_vld_o.value == 1:
                    if self.dut.data_o.value.binstr[0:2] == "10":  # header
                        packet = []
                        await FallingEdge(self.dut.clk_i)
                        self.dut.chan_alloc_i <= 1

                    if self.dut.data_o.value.binstr[0:2] != "00":
                        packet.append(int(self.dut.data_o.value))

                    if self.dut.data_o.value.binstr[0:2] == "11": # tail
                        self.packets_received.append(packet)
                        await FallingEdge(self.dut.clk_i)
                        self.dut.chan_alloc_i <= 0
                        break

        await FallingEdge(self.dut.clk_i)
        self.dut.chan_rdy_i <= 0
        self.dut.chan_alloc_i <= 0

    def compare(self):
        mismatches = 0

        if self.packets_received.__len__() != self.packets_to_send.__len__():
            self.log.error(f"Not enough packets were received {self.packets_received.__len__()} vs {self.packets_to_send.__len__()} sent")
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
async def random_test(dut, log_lvl=INFO, packet_n=10, packet_length=4, cycles=10000):
    """
    We send N packets to the Virtual Channel.
    Simple DataReader tooks out data from VC for comparison with send data.

    :param dut: Design Under test, should be tb (but under tb wrapper there is vritual channel module)
    :param log_lvl: INFO or DEBUG
    :param cycles: maximum number of cycles this testcase can run for
    :return: nothing ( testcase result is stored in 'results.xml' file )
    """
    cocotb.log.info(
        "----------------------------------------------------------------------------- Simulation Started!")
    vctb = VCTB(dut, log_lvl)
    vctb.setup_dut(cycle_n=cycles)
    await ClockCycles(dut.clk_i, 10)
    clocks = cocotb.fork(ClockCycles(dut.clk_i, packet_length*packet_n*10)._wait())
    vctb.populate_packets_to_send(packet_n=packet_n, packet_length=packet_length)

    vc_reader = cocotb.fork(vctb.VCReader())
    for packet in vctb.packets_to_send:
        await vctb.vc_drv.send_packet(packet)
        await ClockCycles(dut.clk_i, 5)

    await First(clocks, vc_reader)
    vctb.compare()

tf = TestFactory(random_test)
tf.add_option("packet_n", [10, 100, 200])
tf.add_option("packet_length", [2, 4, 8, 16])
tf.generate_tests()
