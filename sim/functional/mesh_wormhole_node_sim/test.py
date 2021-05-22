import cocotb
from cocotb.clock import Clock
from cocotb.result import TestSuccess, TestError, TestFailure
from cocotb.triggers import ClockCycles, RisingEdge, ReadOnly, FallingEdge, First, Combine
from cocotb.binary import BinaryValue
from cocotb.log import SimLog
from cocotb.regression import TestFactory

from driver import NodeVCDriver

import os
from collections import Counter

from random import getrandbits, randint
from logging import INFO, DEBUG
from math import log

CLOCK_PERIOD_NS = int(os.environ["CLK_PERIOD"])


class WormholeNodeTB:
    def __init__(self, dut, log_lvl=INFO):
        self.dut = dut
        self.log = SimLog("worm_node_tb")
        self.log.setLevel(log_lvl)

        self.config = {
            "in_n": int(os.environ["IN_N"]),
            "out_m": int(os.environ["OUT_M"]),
            "flit_id_w": int(os.environ["FLIT_ID_W"]),
            "flit_data_w": int(os.environ["FLIT_DATA_W"]),
            "hop_cnt_w": int(os.environ["HOP_CNT_W"]),
            "row_cord":int(os.environ["ROW_CORD"]),
            "row_addr_w":int(os.environ["ROW_ADDR_W"]),
            "col_cord":int(os.environ["COL_CORD"]),
            "col_addr_w":int(os.environ["COL_ADDR_W"]),
            "buffer_depth_w":int(os.environ["BUFFER_DEPTH_W"]),
            "flit_w": int(os.environ["FLIT_ID_W"]) + int(os.environ["FLIT_DATA_W"])
        }

        assert self.dut.IN_N == self.config["in_n"], "Bad Value"
        assert self.dut.OUT_M == self.config["out_m"], "Bad Value"
        assert self.dut.FLIT_ID_W == self.config["flit_id_w"], "Bad Value"
        assert self.dut.HOP_CNT_W == self.config["hop_cnt_w"], "Bad Value"
        assert self.dut.FLIT_DATA_W == self.config["flit_data_w"], "Bad Value"
        assert self.dut.ROW_CORD == self.config["row_cord"], "Bad Value"
        assert self.dut.ROW_ADDR_W == self.config["row_addr_w"], "Bad Value"
        assert self.dut.COL_CORD == self.config["col_cord"], "Bad Value"
        assert self.dut.COL_ADDR_W == self.config["col_addr_w"], "Bad Value"
        assert self.dut.BUFFER_DEPTH_W == self.config["buffer_depth_w"], "Bad Value"

        self.drv = NodeVCDriver(dut, "in_chan", dut.clk_i, -1, self.config, log_lvl)

        self.packets_to_send = []
        self.packets_received = []
        self.dut.out_chan_rdy_i.setimmediatevalue(0x1F)
        self.dut.rst_ni.setimmediatevalue(1)

    def populate_packets_to_send(self, packet_n=10, packet_length=4):
        for i in range(packet_n):
            packet = [self.gen_header_flit(self.config["row_addr_w"],
                                           self.config["col_addr_w"],
                                           self.config["hop_cnt_w"])]
            for j in range(packet_length-1):
                packet.append(self.gen_body_flit(self.config["flit_data_w"]))  # body / payload
            packet.append(self.gen_body_flit(self.config["flit_data_w"], flit_id="11"))  # tail
            self.packets_to_send.append(packet)

    def gen_header_flit(self, row_addr_w, col_addr_w, hop_cnt_w, row=0, col=0, hop_cnt=0, header_id="10", random=True):
        assert (row_addr_w + col_addr_w + hop_cnt_w + len(header_id)) == self.config["flit_w"], f"Total lenght of Header Flit != FLIT_W"

        if random:
            row_addr = BinaryValue(getrandbits(row_addr_w), row_addr_w, bigEndian=False).binstr
            col_addr = BinaryValue(getrandbits(col_addr_w), col_addr_w, bigEndian=False).binstr
            hop_cnt = BinaryValue(getrandbits(hop_cnt_w), hop_cnt_w, bigEndian=False).binstr
        else:
            assert 0 > row or row <= 2**self.config["row_addr_w"]-1, "Row Destination Address is too big for the Width provided"
            row_addr = BinaryValue(row, row_addr_w, bigEndian=False).binstr
            assert 0 > col or col <= 2 ** self.config["col_addr_w"] - 1, "Col Destination Address is too big for the Width provided"
            col_addr = BinaryValue(col, col_addr_w, bigEndian=False).binstr
            assert 0 > hop_cnt or hop_cnt <= 2 ** self.config["hop_cnt_w"] - 1, "HopCount is too big for the Width provided"
            hop_cnt = BinaryValue(hop_cnt, hop_cnt_w, bigEndian=False).binstr

        header_flit = header_id + row_addr + col_addr + hop_cnt
        return BinaryValue(header_flit, len(header_flit), bigEndian=False).integer

    def gen_body_flit(self, data_w, flit_id="01", data=0, random=True):
        assert (data_w + len(flit_id)) == self.config["flit_w"], "Total lenght of Header Flit != FLIT_W"
        if random:
            data = BinaryValue(getrandbits(data_w), data_w, bigEndian=False).binstr
        else:
            assert 0 > data or data <= 2 ** self.config["flit_data_w"] - 1, "Data is too big for the Width provided"
            data = BinaryValue(data, data_w, bigEndian=False).binstr
        flit = flit_id + data
        return BinaryValue(flit, len(flit), bigEndian=False).integer

    def setup_dut(self, cycle_n):
        cocotb.fork(self.reset_dut(self.dut.rst_ni, active_high=False))
        # cocotb.fork(Clock(self.dut.clk_i, CLOCK_PERIOD_NS).start(cycles=cycle_n))

    # async def Reader(self):
    #     risedge = RisingEdge(self.dut.clk_i)
    #     rdonly = ReadOnly()
    #     packet = []
    #     while True:
    #         await risedge
    #         await rdonly
    #         if self.dut.data_vld_o.value == 1:
    #             if self.dut.data_o.value.binstr[0:2] == "10":  # header
    #                 packet = []
    #                 await FallingEdge(self.dut.clk_i)
    #                 self.dut.chan_rdy_i <= 1
    #                 self.dut.chan_alloc_i <= 1
    #             packet.append(int(self.dut.data_o.value))
    #             if self.dut.data_o.value.binstr[0:2] == "11": # tail
    #                 self.packets_received.append(packet)
    #                 await FallingEdge(self.dut.clk_i)
    #                 self.dut.chan_rdy_i <= 0
    #                 self.dut.chan_alloc_i <= 0
    #                 if self.packets_received.__len__() == self.packets_to_send.__len__():
    #                     break
    #
    #     self.dut.chan_rdy_i <= 0
    #     self.dut.chan_alloc_i <= 0

    async def reset_dut(self, rst_sig, active_high=True, clk_cyc_n=5):
        await ClockCycles(self.dut.clk_i, clk_cyc_n)
        if active_high:
            rst_sig <= 1
        else:
            rst_sig <= 0
        await ClockCycles(self.dut.clk_i, clk_cyc_n)
        if active_high:
            rst_sig <= 0
        else:
            rst_sig <= 1

    # def compare(self):
    #     mismatches = 0
    #
    #     if self.packets_received.__len__() != self.packets_to_send.__len__():
    #         self.log.error(f"Not enough packets were received")
    #         raise TestFailure
    #
    #     for pr_id, packet_r in enumerate(self.packets_received):
    #         if Counter(packet_r) != Counter(self.packets_to_send[pr_id]):
    #             mismatches += 1
    #
    #     if mismatches > 0:
    #         self.log.error(f"Mismatches occured {mismatches}/{self.packets_to_send.__len__()}")
    #         for pr_id, packet_r in enumerate(self.packets_received):
    #             if Counter(packet_r) != Counter(self.packets_to_send[pr_id]):
    #                 self.log.info(f"{packet_r} != {self.packets_to_send[pr_id]}")
    #         raise TestFailure
    #     else:
    #         self.log.info(f"All {self.packets_to_send.__len__()} packets were sent and received properly")
    #         raise TestSuccess


def gen_packet(tb, row, col, packet_length=4):
    packet = [tb.gen_header_flit(tb.config["row_addr_w"],
                                 tb.config["col_addr_w"],
                                 tb.config["hop_cnt_w"],
                                 row=row, col=col, random=False)]
    for j in range(packet_length - 1):
        packet.append(tb.gen_body_flit(tb.config["flit_data_w"]))  # body / payload
    packet.append(tb.gen_body_flit(tb.config["flit_data_w"], flit_id="11"))  # tail
    tb.packets_to_send.append(packet)
    return packet


def xy_route(tb, row, col, RESOURCE=0, LEFT=1, UP=2, RIGHT=3, DOWN=4):
    row_cord = tb.config["row_cord"]
    col_cord = tb.config["col_cord"]
    assert tb.config["out_m"] == 5, "Wrong number of outputs"
    if col == col_cord:
        if row == row_cord:
            return RESOURCE
        elif row < row_cord:
            return UP
        else:
            return DOWN
    else:
        if col > col_cord:
            return RIGHT
        else:
            return LEFT


def xy_deroute(tb, output_id, RESOURCE=0, LEFT=1, UP=2, RIGHT=3, DOWN=4):
    row_cord = tb.config["row_cord"]
    col_cord = tb.config["col_cord"]
    assert tb.config["out_m"] == 5, "Wrong number of outputs"
    if output_id == RESOURCE:
        return [row_cord, col_cord]
    if output_id == LEFT:
        return [row_cord, col_cord - 1]
    if output_id == RIGHT:
        return [row_cord, col_cord + 1]
    if output_id == UP:
        return [row_cord - 1, col_cord]
    if output_id == DOWN:
        return [row_cord + 1, col_cord]


async def test_input(tb, input_id, output_id):
    cocotb.log.debug(f"START: packet I:{input_id}->O:{output_id}")
    row = xy_deroute(tb, output_id)[0]
    col = xy_deroute(tb, output_id)[1]
    packet = gen_packet(tb, row, col, packet_length=4)
    await tb.drv.send_packet(packet, input_id=input_id)
    cocotb.log.debug(f"END  : packet I:{input_id} -> O:{output_id}")


@cocotb.test()
async def simple_test(dut, log_lvl=INFO, cycles=10000):
    cocotb.log.info("----------------------------------------------------------------------------- Simulation Started!")
    tb = WormholeNodeTB(dut, log_lvl)
    tb.setup_dut(cycle_n=cycles)
    await ClockCycles(dut.clk_i, 10)
    for i in range(tb.config["in_n"]):
        for j in range(3):
            await test_input(tb, i, j)
            await ClockCycles(dut.clk_i, 10)
    raise TestSuccess("Sim finished sucessfully")


@cocotb.test()
async def competetive_test(dut, log_lvl=INFO, cycles=10000):
    cocotb.log.info("----------------------------------------------------------------------------- Simulation Started!")
    tb = WormholeNodeTB(dut, log_lvl)
    tb.setup_dut(cycle_n=cycles)
    await ClockCycles(dut.clk_i, 10)

    for j in range(tb.config["out_m"]):
        waiters = []
        for i in range(tb.config["in_n"]):
            waiters.append(cocotb.fork(test_input(tb, i, j)))
        await ClockCycles(dut.clk_i, 10)
        await Combine(*waiters)
    raise TestSuccess("Sim finished sucessfully")


@cocotb.test()
async def multi_output_no_compete(dut, log_lvl=INFO, cycles=10000):
    cocotb.log.info("----------------------------------------------------------------------------- Simulation Started!")
    tb = WormholeNodeTB(dut, log_lvl)
    tb.setup_dut(cycle_n=cycles)
    await ClockCycles(dut.clk_i, 10)

    waiters = []
    for i in range(tb.config["in_n"]):
        waiters.append(cocotb.fork(test_input(tb, i, i)))
    await Combine(*waiters)
    await ClockCycles(dut.clk_i, 10)
    raise TestSuccess("Sim finished sucessfully")


@cocotb.test()
async def multi_output_compete(dut, log_lvl=INFO, cycles=10000):
    cocotb.log.info("----------------------------------------------------------------------------- Simulation Started!")
    tb = WormholeNodeTB(dut, log_lvl)
    tb.setup_dut(cycle_n=cycles)
    await ClockCycles(dut.clk_i, 10)

    for j in range(tb.config["out_m"]):
        for num in range(tb.config["in_n"]):
            if num != 0:
                waiters = []
                for i in range(tb.config["in_n"]):
                    if i % num == 0:
                        waiters.append(cocotb.fork(test_input(tb, i, i)))
                    else:
                        waiters.append(cocotb.fork(test_input(tb, i, j)))
                await Combine(*waiters)
                await ClockCycles(dut.clk_i, 10)
        await ClockCycles(dut.clk_i, 10)
    await ClockCycles(dut.clk_i, 10)
    raise TestSuccess("Sim finished sucessfully")


@cocotb.test()
async def random_single_input_at_a_time(dut, log_lvl=INFO, packet_n=30, packet_length=4, cycles=10000):
    cocotb.log.info("----------------------------------------------------------------------------- Simulation Started!")
    tb = WormholeNodeTB(dut, log_lvl)
    tb.setup_dut(cycle_n=cycles)
    await ClockCycles(dut.clk_i, 10)
    # clocks = cocotb.fork(ClockCycles(dut.clk_i, packet_length*packet_n*5)._wait())
    tb.populate_packets_to_send(packet_n=packet_n, packet_length=packet_length)

    # vc_reader = cocotb.fork(alloctb.VCReader())
    for packet in tb.packets_to_send:
        driver_id = randint(0,4)
        await tb.drv.send_packet(packet, driver_id)

    raise TestSuccess("Asap")

@cocotb.test()
async def random_multi_input_at_a_time(dut, log_lvl=INFO, packet_n=30, packet_length=4, cycles=10000):
    cocotb.log.info("----------------------------------------------------------------------------- Simulation Started!")
    tb = WormholeNodeTB(dut, log_lvl)
    tb.setup_dut(cycle_n=cycles)
    await ClockCycles(dut.clk_i, 10)
    # clocks = cocotb.fork(ClockCycles(dut.clk_i, packet_length*packet_n*10)._wait())

    in_n = tb.config["in_n"]
    tb.populate_packets_to_send(packet_n=packet_n*in_n, packet_length=packet_length)

    pckt_size = int(len(tb.packets_to_send)/in_n)
    pckts = tb.packets_to_send
    # vc_reader = cocotb.fork(alloctb.VCReader())

    for packet in range(pckt_size):
        waiters = []
        for i in range(tb.config["in_n"]):
            waiters.append(cocotb.fork(tb.drv.send_packet(pckts[(packet*in_n)+i], i)))
        await Combine(*waiters)
    # alloctb.compare()
    raise TestSuccess("Asap")

# tf = TestFactory(random_test)
# # tf.add_option("packet_n", [10, 100])
# tf.add_option("packet_length", [2, 4, 8])
# tf.generate_tests()
