import cocotb
from cocotb_bus.drivers import BusDriver
from cocotb.triggers import RisingEdge, ClockCycles, ReadOnly, FallingEdge, ReadWrite
from cocotb.binary import BinaryValue

from random import getrandbits
from logging import INFO, DEBUG

from math import log


class AllocDriver(BusDriver):
    _signals = ["flit_id_i", "rtr_res_i", "rtr_res_vld_i", "data_vld_i",
                "forward_node_rdy_i", "rst_ni"]

    _default_config = {
        "in_n": 5,
        "out_m": 5,
        "flit_id_w": 2,
        "out_chan_id": 1,
        "rtr_res_w": log(5, 2),
        "chan_sel_w": log(5, 2)
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

        self.bus.flit_id_i.setimmediatevalue(0)
        # self.bus.hop_count_i.setimmediatevalue(0)
        self.bus.rtr_res_i.setimmediatevalue(0)
        self.bus.rtr_res_vld_i.setimmediatevalue(0)
        self.bus.rst_ni.setimmediatevalue(1)
        self.bus.data_vld_i.setimmediatevalue(0)
        self.bus.forward_node_rdy_i.setimmediatevalue(0)

    async def send(self):
        await RisingEdge(self.clock)
        self.bus.flit_id_i <= 0b1001010111
        self.bus.data_vld_i <= 0b10001
        rtr_res = "001" + "000" + "000" + "001" + "000"
        self.bus.rtr_res_i <= BinaryValue(rtr_res, len(rtr_res), bigEndian=False)

        await RisingEdge(self.clock)
        await RisingEdge(self.clock)
        self.bus.flit_id_i <= 0
        self.bus.data_vld_i <= 0
        self.bus.rtr_res_i <= 0

    async def clear_vc_input(self, sync: bool = True):
        if sync is True:
            await RisingEdge(self.clock)
        self.bus.flit_id_i.setimmediatevalue(0)
        self.bus.rtr_res_i.setimmediatevalue(0)
        self.bus.rst_ni.setimmediatevalue(1)
        self.bus.data_vld_i.setimmediatevalue(0)
        self.bus.backpressure_fifo_full_i.setimmediatevalue(0)

    async def reset(self):
        await ClockCycles(self.clock, 5)
        self.bus.rst_ni <= 0
        await ClockCycles(self.clock, 5)
        self.bus.rst_ni <= 1
