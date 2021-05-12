import cocotb
from cocotb.clock import Clock
from cocotb.result import TestSuccess, TestError
from cocotb.triggers import ClockCycles, RisingEdge
from cocotb_bus.scoreboard import Scoreboard

from driver import VCDriver
# from mon_i import FifoIMon
# from mon_o import FifoOMon

import os

from logging import INFO, DEBUG

CLOCK_PERIOD_NS = int(os.environ["CLK_PERIOD"])

class VCTB:
    def __init__(self, dut, log_lvl=INFO):
        self.dut = dut

        self.config = {
            "flit_data_w": int(os.environ["FLIT_DATA_W"]),
            "vc_depth_w": int(os.environ["VC_DEPTH_W"]),
            "flit_id_w": int(os.environ["FLIT_ID_W"]),
            "flit_w": int(os.environ["FLIT_DATA_W"]) + int(os.environ["FLIT_ID_W"])
        }

        assert self.dut.FLIT_DATA_W == self.config["flit_data_w"], "Bad Value"
        assert self.dut.VC_DEPTH_W == self.config["vc_depth_w"], "Bad Value"
        assert self.dut.FLIT_ID_W == self.config["flit_id_w"], "Bad Value"

        self.vc_drv = VCDriver(dut, "", dut.clk_i, self.config, log_lvl)
        # self.vc_i_mon = VCIMon(dut, "", dut.clk_i, log_lvl, callback=self.mon_callback)
        # self.vc_o_mon = VCOMon(dut, "", dut.clk_i, log_lvl)

    def setup_dut(self, cycle_n):
        cocotb.fork(self.vc_drv.reset())
        cocotb.fork(Clock(self.dut.clk_i, CLOCK_PERIOD_NS).start(cycles=cycle_n))

@cocotb.test()
async def basic_test(dut, log_lvl=INFO, cycles=10000):
    cocotb.log.info("----------------------------------------------------------------------------- Simulation Started!")
    vctb = VCTB(dut, log_lvl)
    vctb.setup_dut(cycle_n=cycles)
    await ClockCycles(dut.clk_i, 10)
    await vctb.vc_drv.send_packet(0)
    await vctb.vc_drv.send_packet(0)
    cocotb.log.info("Finished writing")
    if dut.header_o.value != 0:
        cocotb.log.info("1st packet")
        while dut.data_o.value != 0b1100000000:
            dut.chan_alloc_i <= 1
            dut.chan_rdy_i <= 1
            await RisingEdge(dut.clk_i)
    dut.chan_alloc_i <= 0
    dut.chan_rdy_i <= 0
    await RisingEdge(dut.data_vld_o)

    cocotb.log.info("DUN")
    await RisingEdge(dut.clk_i)

    if dut.header_o.value != 0:
        cocotb.log.info("2nd packet")
        while dut.data_o.value != 0b1100000000:
            dut.chan_alloc_i <= 1
            dut.chan_rdy_i <= 1
            await RisingEdge(dut.clk_i)
    dut.chan_alloc_i <= 0
    dut.chan_rdy_i <= 0

    await ClockCycles(dut.clk_i, 100)
    raise TestSuccess("Sim finished sucessfully")
