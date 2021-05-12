import cocotb
from cocotb_bus.drivers import BusDriver
from cocotb.triggers import RisingEdge, ClockCycles, ReadOnly, FallingEdge, ReadWrite
from cocotb.binary import BinaryValue

from random import getrandbits
from logging import INFO, DEBUG


class VCDriver(BusDriver):
    _signals = ["wr_en_i", "data_i", "chan_alloc_i", "chan_rdy_i", "rst_ni"]

    _default_config = {
        "flit_id_w": 2,
        "vc_depth_w": 2,
        "flit_data_w": 8,
        "flit_w": 10
    }

    def __init__(self, entity, name, clock, config=None, log_lvl=INFO):
        self.entity = entity
        self.name = name
        self.clock = clock

        if config is None:
            self.config = self._default_config
        else:
            self.config = config

        BusDriver.__init__(self, entity, name, clock)
        if log_lvl == DEBUG:
            self.log.setLevel(DEBUG)
        else:
            self.log.setLevel(INFO)

        self.data_zero = BinaryValue(0, self.config["flit_w"], bigEndian=False)
        self.bus.wr_en_i.setimmediatevalue(0)
        self.bus.chan_alloc_i.setimmediatevalue(0)
        self.bus.chan_rdy_i.setimmediatevalue(0)
        self.bus.rst_ni.setimmediatevalue(1)
        self.bus.data_i.setimmediatevalue(self.data_zero)

    async def send_simple_packet(self, val):
        header  = 0b1001010000 # 10, row_addr 1, col 1, hops 0 ( 1 )
        body    = 0b0100101010 # 01, data as 00101010          ( 0 or N)
        tail    = 0b1100000000 # 11, dont care                 ( 1 )

        await RisingEdge(self.clock)
        self.bus.wr_en_i <= 1
        self.bus.data_i  <= header

        self.log.info("HEJHEJ")

        await RisingEdge(self.clock)
        self.bus.wr_en_i <= 1
        self.bus.data_i <= body
        self.log.info("HEJHO")
        await RisingEdge(self.clock)
        self.bus.wr_en_i <= 1
        self.bus.data_i <= tail
        self.log.info("HEJHA")
        await RisingEdge(self.clock)
        self.bus.wr_en_i <= 0
        self.bus.data_i <= 0
        self.log.info("HEJHU")

    async def send_packet(self, packet):
        i = 0
        while i != len(packet):
            await RisingEdge(self.clock)
            await ReadOnly()
            if self.entity.rdy_o.value == 1:
                await FallingEdge(self.clock)
                self.bus.wr_en_i <= 1
                self.bus.data_i <= packet[i]
                i += 1
            else:
                await FallingEdge(self.clock)
                self.bus.wr_en_i <= 0
                self.bus.data_i <= 0


    async def clear_vc_input(self, sync: bool = True):
        if sync is True:
            await RisingEdge(self.clock)
        self.bus.wr_en_i.setimmediatevalue(0)
        self.bus.chan_alloc_i.setimmediatevalue(0)
        self.bus.chan_rdy_i.setimmediatevalue(0)
        self.bus.rst_ni.setimmediatevalue(1)
        self.bus.data_i.setimmediatevalue(self.data_zero)

    async def reset(self):
        await ClockCycles(self.clock, 5)
        self.bus.rst_ni <= 0
        await ClockCycles(self.clock, 5)
        self.bus.rst_ni <= 1
