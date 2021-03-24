import cocotb
from cocotb_bus.drivers import BusDriver
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb.binary import BinaryValue

from random import getrandbits
from logging import INFO, DEBUG

import os


class FifoDriver(BusDriver):
    _signals = ["wr_en_i", "rd_en_i", "data_i", "rst_ni"]

    def __init__(self, entity, name, clock, log_lvl=INFO):
        self.entity = entity
        self.name = name
        self.clock = clock
        BusDriver.__init__(self, entity, name, clock)
        if log_lvl == DEBUG:
            self.log.setLevel(DEBUG)
        else:
            self.log.setLevel(INFO)
        self.fifo_depth_width = int(os.environ["FIFO_DEPTH_WIDTH"])
        self.data_width = int(os.environ["DATA_WIDTH"])
        self.data_zero = BinaryValue(0, n_bits=self.data_width, bigEndian=False)
        self.bus.wr_en_i.setimmediatevalue(0)
        self.bus.rd_en_i.setimmediatevalue(0)
        self.bus.data_i.setimmediatevalue(self.data_zero)

    async def n_rand_transactions(self, n):
        for i in range(n):
            await RisingEdge(self.clock)
            self.bus.wr_en_i <= getrandbits(1)
            self.bus.rd_en_i <= getrandbits(1)
            self.bus.data_i <= getrandbits(self.data_width)

    async def n_rand_transactions_reset(self, n):
        for i in range(n):
            await RisingEdge(self.clock)
            self.bus.wr_en_i <= getrandbits(1)
            self.bus.rd_en_i <= getrandbits(1)
            self.bus.data_i <= getrandbits(self.data_width)
            self.bus.rst_ni <= getrandbits(1)

    async def write_fifo(self, val):
        await RisingEdge(self.clock)
        self.bus.wr_en_i <= 1
        self.bus.data_i <= val

    async def read_fifo(self):
        await RisingEdge(self.clock)
        self.bus.rd_en_i <= 1

    async def clear_fifo_input(self, sync: bool = True):
        if sync is True:
            await RisingEdge(self.clock)
        self.bus.wr_en_i <= 0
        self.bus.data_i <= self.data_zero
        self.bus.rd_en_i <= 0

    async def fill_fifo(self):
        """
        Sends FIFO_DEPTH write transactions sequentially with random data_i values
        :return: None
        """
        for i in range(2**self.fifo_depth_width-1):
            await RisingEdge(self.clock)
            self.bus.wr_en_i <= 1
            self.bus.data_i <= getrandbits(self.data_width)

    async def empty_fifo(self):
        """
        Sends FIFO_DEPTH read transactions sequentially regardless of FIFO fullness
        :return: None
        """
        for i in range(2**self.fifo_depth_width-1):
            self.bus.rd_en_i <= 1

        await self.clear_fifo_input()

    async def reset_fifo(self):
        self.bus.rst_ni <= 0
        await ClockCycles(self.clock, 2)
        self.bus.rst_ni <= 1
