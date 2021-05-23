import cocotb
from cocotb.result import TestSuccess, TestFailure
from cocotb.triggers import ClockCycles, RisingEdge, ReadOnly, Combine, FallingEdge
from cocotb.binary import BinaryValue
from cocotb.log import SimLog
from cocotb.regression import TestFactory

from driver import NodeVCDriver

import os
from collections import Counter

from random import getrandbits, randint
from logging import INFO, DEBUG

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

            header = self.gen_header_flit(self.config["row_addr_w"],
                                          self.config["col_addr_w"],
                                          self.config["hop_cnt_w"])
            packet = [header[0]]
            out_chan = xy_route(self, row=header[1], col=header[2])

            for j in range(packet_length-1):
                packet.append(self.gen_body_flit(self.config["flit_data_w"]))  # body / payload
            packet.append(self.gen_body_flit(self.config["flit_data_w"], flit_id="11"))  # tail

            self.packets_to_send.append({"out_chan": out_chan, "packet": packet})

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
        if random:
            return [BinaryValue(header_flit, len(header_flit), bigEndian=False).integer,
                    BinaryValue(row_addr, len(row_addr), bigEndian=False).integer,
                    BinaryValue(col_addr, len(col_addr), bigEndian=False).integer]
        else:
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

    def setup_dut(self, cycle_n, bp=False):
        cocotb.fork(self.reset_dut(self.dut.rst_ni, active_high=False, clk_cyc_n=cycle_n))
        readers = []
        for out_chan in range(self.config["out_m"]):
            readers.append(cocotb.fork(self.node_out_chan_reader(out_chan, cycle_n=cycle_n*2)))
        if bp:
            bp = []
            for i in range(self.config["out_m"]):
                bp.append(cocotb.fork(self.backpressure_gen(cycle_n=cycle_n*2)))

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

    async def node_out_chan_reader(self, i, cycle_n=10):
        risedge = RisingEdge(self.dut.clk_i)
        rdonly = ReadOnly()

        await ClockCycles(self.dut.clk_i, cycle_n)

        packet = []
        while True:
            await risedge
            await rdonly
            if self.dut.out_chan_vld_o[i].value == 1:
                if self.dut.out_chan_data_o[i].value.binstr[0:2] == "10":  # header
                    packet = []
                packet.append(int(self.dut.out_chan_data_o[i].value))
                if self.dut.out_chan_data_o[i].value.binstr[0:2] == "11":  # tail
                    self.packets_received.append({"out_chan": i, "packet": packet})

    async def backpressure_gen(self, cycle_n=10):
        risedge = RisingEdge(self.dut.clk_i)
        await ClockCycles(self.dut.clk_i, cycle_n)
        while True:
            await risedge
            self.dut.out_chan_rdy_i <= getrandbits(self.config["out_m"])

    def compare(self):
        mismatches = 0
        received = sorted(self.packets_received, key=lambda k: k['out_chan'])
        sent = sorted(self.packets_to_send, key=lambda k: k['out_chan'])
        temp_sent = sent.copy()

        if received.__len__() != sent.__len__():
            self.log.error(f"Not enough packets were received {received.__len__()} vs {sent.__len__()} sent")
            raise TestFailure

        for pr_id, packet_r in enumerate(received):
            if packet_r not in temp_sent:
                mismatches += 1
            else:
                pre_len = len(temp_sent)
                self.log.debug(f"PRE POP len of temp_sent{len(temp_sent)}")
                self.log.debug(f"{packet_r} at {pr_id} matched! Removing temp_sent packet")
                temp_sent.remove(packet_r)
                post_len = len(temp_sent)
                self.log.debug(f"POST POP len of temp_sent{len(temp_sent)}")
                if pre_len != post_len + 1:
                    self.log.error("Too many were removed !")
                    raise TestFailure

        if mismatches > 0:
            self.log.error(f"Mismatches occured {mismatches}/{sent.__len__()} sent")
            for pr_id, packet_r in enumerate(received):
                if Counter(packet_r) != Counter(sent[pr_id]):
                    self.log.info(f"{pr_id}. {packet_r} != {sent[pr_id]}")
            raise TestFailure
        else:
            self.log.info(f"All {sent.__len__()} packets were sent and received properly")
            raise TestSuccess


def gen_packet(tb, row, col, packet_length=4):
    packet = [tb.gen_header_flit(tb.config["row_addr_w"],
                                 tb.config["col_addr_w"],
                                 tb.config["hop_cnt_w"],
                                 row=row, col=col, random=False)]
    for j in range(packet_length - 1):
        packet.append(tb.gen_body_flit(tb.config["flit_data_w"]))  # body / payload
    packet.append(tb.gen_body_flit(tb.config["flit_data_w"], flit_id="11"))  # tail

    out_chan = xy_route(tb, row, col)

    tb.packets_to_send.append({"out_chan": out_chan, "packet": packet})
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


async def test_input(tb, input_id, output_id, packet_lenght=4):
    cocotb.log.debug(f"START: packet I:{input_id}->O:{output_id}")
    row = xy_deroute(tb, output_id)[0]
    col = xy_deroute(tb, output_id)[1]
    packet = gen_packet(tb, row, col, packet_lenght)
    await tb.drv.send_packet(packet, input_id=input_id)
    cocotb.log.debug(f"END  : packet I:{input_id} -> O:{output_id}")


@cocotb.test()
async def simple_test(dut, log_lvl=INFO, bp=False):
    tb = WormholeNodeTB(dut, log_lvl)
    tb.setup_dut(cycle_n=5, bp=bp)
    await ClockCycles(dut.clk_i, 10)
    for i in range(tb.config["in_n"]):
        for j in range(tb.config["out_m"]):
            await test_input(tb, i, j)
            await ClockCycles(dut.clk_i, 10)
    await ClockCycles(dut.clk_i, 1000)
    tb.compare()
    raise TestSuccess("Sim finished sucessfully")


@cocotb.test()
async def competetive_test(dut, log_lvl=INFO, bp=False):
    tb = WormholeNodeTB(dut, log_lvl)
    tb.setup_dut(cycle_n=5, bp=bp)
    await ClockCycles(dut.clk_i, 10)
    for j in range(tb.config["out_m"]):
        waiters = []
        for i in range(tb.config["in_n"]):
            waiters.append(cocotb.fork(test_input(tb, i, j)))
        await ClockCycles(dut.clk_i, 10)
        await Combine(*waiters)
    await ClockCycles(dut.clk_i, 1000)
    tb.compare()
    raise TestSuccess("Sim finished sucessfully")


@cocotb.test()
async def multi_output_no_compete(dut, log_lvl=INFO, bp=False):
    tb = WormholeNodeTB(dut, log_lvl)
    tb.setup_dut(cycle_n=5, bp=bp)
    await ClockCycles(dut.clk_i, 10)
    waiters = []
    for i in range(tb.config["in_n"]):
        waiters.append(cocotb.fork(test_input(tb, i, i)))
    await Combine(*waiters)
    await ClockCycles(dut.clk_i, 1000)
    tb.compare()
    raise TestSuccess("Sim finished sucessfully")


@cocotb.test()
async def multi_output_compete(dut, log_lvl=INFO, bp=False):
    tb = WormholeNodeTB(dut, log_lvl)
    tb.setup_dut(cycle_n=5, bp=bp)
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
    await ClockCycles(dut.clk_i, 1000)
    tb.compare()
    raise TestSuccess("Sim finished sucessfully")


@cocotb.test()
async def random_single_input_at_a_time(dut, log_lvl=INFO, packet_n=30, packet_length=4, bp=False):
    tb = WormholeNodeTB(dut, log_lvl)
    tb.setup_dut(cycle_n=5, bp=bp)
    await ClockCycles(dut.clk_i, 10)
    tb.populate_packets_to_send(packet_n=packet_n, packet_length=packet_length)

    for packet in tb.packets_to_send:
        driver_id = randint(0, tb.config["out_m"]-1)
        await tb.drv.send_packet(packet["packet"], driver_id)
    await ClockCycles(dut.clk_i, 1000)
    tb.compare()
    raise TestSuccess("Sim finished sucessfully")


@cocotb.test()
async def random_multi_input_at_a_time(dut, log_lvl=INFO, packet_n=30, packet_length=4, bp=False):
    tb = WormholeNodeTB(dut, log_lvl)
    tb.setup_dut(cycle_n=5)
    await ClockCycles(dut.clk_i, 10)

    in_n = tb.config["in_n"]
    tb.populate_packets_to_send(packet_n=packet_n*in_n, packet_length=packet_length)

    pckt_size = int(len(tb.packets_to_send)/in_n)
    pckts = tb.packets_to_send

    if bp:
        bp = []
        for i in range(tb.config["out_m"]):
            bp.append(cocotb.fork(tb.backpressure_gen(i)))

    for packet in range(pckt_size):
        waiters = []
        for i in range(tb.config["in_n"]):
            waiters.append(cocotb.fork(tb.drv.send_packet(pckts[(packet*in_n)+i]["packet"], i)))
        await Combine(*waiters)
    await ClockCycles(dut.clk_i, 1000)
    tb.compare()
    raise TestSuccess("Sim finished sucessfully")


tf = TestFactory(simple_test)
tf.add_option("bp", [False, True])
tf.generate_tests()

tf = TestFactory(competetive_test)
tf.add_option("bp", [False, True])
tf.generate_tests()

tf = TestFactory(multi_output_compete)
tf.add_option("bp", [False, True])
tf.generate_tests()

tf = TestFactory(multi_output_no_compete)
tf.add_option("bp", [False, True])
tf.generate_tests()

tf = TestFactory(random_single_input_at_a_time)
tf.add_option("bp", [False, True])
tf.add_option("packet_n", [10, 100, 200])
tf.add_option("packet_length", [2, 4, 8])
tf.generate_tests()

tf = TestFactory(random_multi_input_at_a_time)
tf.add_option("bp", [False, True])
tf.add_option("packet_n", [10, 100, 200])
tf.add_option("packet_length", [2, 4, 8])
tf.generate_tests()
