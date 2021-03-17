from cocotb.drivers import BusDriver
from cocotb.triggers import RisingEdge, ClockCycles, ReadOnly
from cocotb.binary import BinaryValue
from cocotb.result import TestError

from random import getrandbits, sample
from logging import INFO, DEBUG


class SWPacketDriver(BusDriver):
    _signals = ["pckt_sw_i", "wr_en_sw_i", "nxt_fifo_full_i", "nxt_fifo_overflow_i"]

    _default_config = {
        "packet_x_addr_w": 2,
        "packet_y_addr_w": 2,
        "packet_data_w": 8,
        "packet_w": 12,
        "neighbours_n": 5,
        "fifo_depth_w": 2,
        "x_cord": 0,
        "y_cord": 0,
        "sw_config": 0
    }

    def __init__(self, entity, name, clock, config=None, log_lvl=INFO):
        self.entity = entity
        self.name = name
        self.clock = clock
        self.packet_id = 0
        self.sent_packets = 0

        if config is None:
            self.config = self._default_config
        else:
            self.config = config

        BusDriver.__init__(self, entity, name, clock)
        if log_lvl == DEBUG:
            self.log.setLevel(DEBUG)
        else:
            self.log.setLevel(INFO)

        # Reset Input signals
        self.bus.pckt_sw_i.setimmediatevalue(0)
        self.bus.wr_en_sw_i.setimmediatevalue(0)
        self.bus.nxt_fifo_full_i.setimmediatevalue(0)
        self.bus.nxt_fifo_overflow_i.setimmediatevalue(0)

    async def gen_rand_full(self, n):
        for i in range(n):
            await RisingEdge(self.clock)
            self.bus.nxt_fifo_full_i <= getrandbits(self.config["neighbours_n"])

    async def write_to_single_input(self, input_id, x_dest, y_dest):
        if 0 > input_id > 2**self.config["neighbours_n"]:
            raise TestError("input id is not correct")

        await RisingEdge(self.clock)

        self.sent_packets += 1
        self.packet_id += 1

        packet = self.packet_id
        packet |= (x_dest << self.config["packet_data_w"])
        packet |= (y_dest << (self.config["packet_data_w"] + self.config["packet_x_addr_w"]))
        packets = BinaryValue(0, self.config["neighbours_n"]*self.config["packet_w"], bigEndian=False)
        packets |= (packet << input_id * self.config["packet_w"])

        self.bus.pckt_sw_i <= packets
        self.bus.wr_en_sw_i <= BinaryValue(1 << input_id, self.config["neighbours_n"], bigEndian=False)

    async def write_to_n_inputs(self, n):
        await RisingEdge(self.clock)

        self.sent_packets += n
        sources = sample(range(self.config["neighbours_n"]-1), n)
        packets = BinaryValue(0, self.config["neighbours_n"] * self.config["packet_w"], bigEndian=False)
        wr_en = 0

        for source in sources:
            x_dest = getrandbits(self.config["packet_x_addr_w"])
            y_dest = getrandbits(self.config["packet_y_addr_w"])
            self.packet_id += 1

            packet = self.packet_id
            packet |= (x_dest << self.config["packet_data_w"])
            packet |= (y_dest << (self.config["packet_data_w"] + self.config["packet_x_addr_w"]))

            wr_en += 1 << source
            packets |= (packet << source * self.config["packet_w"])

        self.bus.pckt_sw_i <= packets
        self.bus.wr_en_sw_i <= BinaryValue(wr_en, self.config["neighbours_n"], bigEndian=False)

    async def clear_sw_input(self, sync: bool = True):
        if sync is True:
            await RisingEdge(self.clock)
            self.bus.pckt_sw_i <= 0
            self.bus.wr_en_sw_i <= 0
            self.bus.nxt_fifo_full_i <= 0
            self.bus.nxt_fifo_overflow_i <= 0

    def reset(self):
        self.packet_id = 0
        self.sent_packets = 0
