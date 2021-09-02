from cocotb_bus.drivers import BusDriver
from cocotb.triggers import RisingEdge, ClockCycles, ReadOnly, FallingEdge
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
        "y_cord": 0
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

    async def write_to_single_input(self, input_id, x_dest, y_dest, random=False):
        if 0 > input_id > 2**self.config["neighbours_n"]:
            raise TestError("input id is not correct")

        if random is False:
            x_dest = x_dest
            y_dest = y_dest
        else:
            x_dest = getrandbits(self.config["packet_x_addr_w"])
            y_dest = getrandbits(self.config["packet_y_addr_w"])

        while True:
            await RisingEdge(self.clock)
            await ReadOnly()
            if self.bus.nxt_fifo_full_i[input_id].value != 1:
                await FallingEdge(self.clock)
                self.sent_packets += 1
                self.packet_id += 1
                packet = self.packet_id
                packet |= (x_dest << self.config["packet_data_w"])
                packet |= (y_dest << (self.config["packet_data_w"] + self.config["packet_x_addr_w"]))
                packets = BinaryValue(0, self.config["neighbours_n"]*self.config["packet_w"], bigEndian=False)
                packets |= (packet << input_id * self.config["packet_w"])
                self.bus.pckt_sw_i <= packets
                self.bus.wr_en_sw_i <= BinaryValue(1 << input_id, self.config["neighbours_n"], bigEndian=False)
                break
            else:
                await FallingEdge(self.clock)
                self.bus.pckt_sw_i <= 0
                self.bus.wr_en_sw_i <= 0
        await FallingEdge(self.clock)
        self.bus.pckt_sw_i <= 0
        self.bus.wr_en_sw_i <= 0

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
