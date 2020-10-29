from cocotb.drivers import BusDriver
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb.binary import BinaryValue
from cocotb.result import TestError

from random import getrandbits
from logging import INFO, DEBUG

import os

# TODO: Test if it works

class SWPacketDriver(BusDriver):
    _signals = ["pckt_sw_i", "pckt_vld_sw_i", "rst_ni"]

    def __init__(self, entity, name, clock, log_lvl=INFO):
        self.entity = entity
        self.name = name
        self.clock = clock
        BusDriver.__init__(self, entity, name, clock)
        if log_lvl == DEBUG:
            self.log.setLevel(DEBUG)
        else:
            self.log.setLevel(INFO)

        self.packet_x_addr_width = int(os.environ["PACKET_X_ADDR_W"])
        self.packet_y_addr_width = int(os.environ["PACKET_Y_ADDR_W"])
        self.packet_data_width = int(os.environ["PACKET_DATA_W"])
        self.packet_width = int(os.environ["PACKET_W"])
        self.neighbours_n = int(os.environ["NEIGHBOURS_N"])

        self.bus.pckt_sw_i.setimmediatevalue(0)
        self.bus.pckt_vld_sw_i.setimmediatevalue(0)

    async def n_rand_data_packets(self, n):
        for i in range(n):
            await RisingEdge(self.clock)
            self.bus.pckt_sw_i <= getrandbits(self.packet_width * self.neighbours_n)
            self.bus.pckt_vld_sw_i <= 1

    async def write_to_single_input(self, input_id, val, x, y):
        if 0 > input_id > 2**self.neighbours_n:
            raise TestError("input id is not correct")
        try:
            val = BinaryValue(val, self.packet_data_width, False)
        except False:
            raise TestError("val is not the correct size")
        try:
            x = BinaryValue(x, self.packet_data_width, False)
        except False:
            raise TestError("X addr is not the correct size")
        try:
            y = BinaryValue(y, self.packet_data_width, False)
        except False:
            raise TestError("Y addr is not the correct size")

        await RisingEdge(self.clock)
        packet = val
        packet |= (y << self.packet_data_width)
        packet |= (x << (self.packet_data_width + self.packet_y_addr_width))
        packets = BinaryValue(0, self.neighbours_n*self.packet_width, bigEndian=False)
        packets |= (packet << input_id * self.packet_width)
        self.bus.pckt_sw_i <= packets
        self.bus.pckt_vld_sw_i <= 1

    async def clear_sw_input(self, sync: bool = True):
        if sync is True:
            await RisingEdge(self.clock)
            self.bus.pckt_sw_i <= 0
            self.bus.pckt_vld_sw_i <= 1

    async def reset_sw(self):
        self.bus.rst_ni <= 0
        await ClockCycles(self.clock, 2)
        self.bus.rst_ni <= 1
