from cocotb.drivers import BusDriver
from cocotb.triggers import RisingEdge, ClockCycles, ReadOnly
from cocotb.binary import BinaryValue
from cocotb.result import TestError

from random import getrandbits
from logging import INFO, DEBUG

import os

# TODO: Test if it works


class SWPacketDriver(BusDriver):
    _signals = ["pckt_sw_i", "wr_en_sw_i", "nxt_fifo_full_i", "nxt_fifo_overflow_i"]

    def __init__(self, entity, name, clock, log_lvl=INFO):
        self.entity = entity
        self.name = name
        self.clock = clock
        BusDriver.__init__(self, entity, name, clock)
        if log_lvl == DEBUG:
            self.log.setLevel(DEBUG)
        else:
            self.log.setLevel(INFO)

        # Load Parameter Values
        self.packet_x_addr_width = int(os.environ["PACKET_X_ADDR_W"])
        self.packet_y_addr_width = int(os.environ["PACKET_Y_ADDR_W"])
        self.packet_data_width = int(os.environ["PACKET_DATA_W"])
        self.packet_width = int(os.environ["PACKET_W"])
        self.neighbours_n = int(os.environ["PORT_N"])

        # Reset Input signals
        self.bus.pckt_sw_i.setimmediatevalue(0)
        self.bus.wr_en_sw_i.setimmediatevalue(0)
        self.bus.nxt_fifo_full_i.setimmediatevalue(0)
        self.bus.nxt_fifo_overflow_i.setimmediatevalue(0)

    async def n_rand_data_packets(self, n):
        for i in range(n):
            await RisingEdge(self.clock)
            self.bus.pckt_sw_i <= getrandbits(self.packet_width * self.neighbours_n)

    async def write_to_single_input(self, input_id, packet_data, x_dest, y_dest):
        if 0 > input_id > 2**self.neighbours_n:
            raise TestError("input id is not correct")

        packet = packet_data
        packet |= (y_dest << self.packet_data_width)
        packet |= (x_dest << (self.packet_data_width + self.packet_y_addr_width))
        packets = BinaryValue(0, self.neighbours_n*self.packet_width, bigEndian=False)
        packets |= (packet << input_id * self.packet_width)

        self.bus.pckt_sw_i <= packets
        self.bus.wr_en_sw_i <= BinaryValue(1 << input_id, self.neighbours_n, bigEndian=False)
        await RisingEdge(self.clock)

        self.bus.pckt_sw_i <= BinaryValue(0, self.neighbours_n*self.packet_width, bigEndian=False)
        self.bus.wr_en_sw_i <= BinaryValue(0, self.neighbours_n, bigEndian=False)


    async def clear_sw_input(self, sync: bool = True):
        if sync is True:
            await RisingEdge(self.clock)
            self.bus.pckt_sw_i <= 0
            self.bus.wr_en_sw_i <= 0
