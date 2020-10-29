import cocotb
from cocotb.clock import Clock
from cocotb.result import TestSuccess, TestError
from cocotb.triggers import ClockCycles
from cocotb.scoreboard import Scoreboard

from driver import SWPacketDriver
from mon_i import SWIMon
from mon_o import SWOMon

from logging import INFO, DEBUG

CLOCK_PERIOD_NS = 10


class SWTB:
    def __init__(self, dut, log_lvl=INFO):
        self.dut = dut
        self.sw_drv = SWPacketDriver(dut, "", dut.clk_i, log_lvl)
        self.sw_i_mon = SWIMon(dut, "", dut.clk_i, log_lvl, callback=self.mon_callback)
        self.sw_o_mon = SWOMon(dut, "", dut.clk_i, log_lvl)
        self.expected = []
        self.sb = Scoreboard(dut, fail_immediately=True)
        self.sb.add_interface(self.sw_o_mon, self.expected)

    def setup_dut(self, cycle_n):
        cocotb.fork(self.sw_drv.reset_sw())
        cocotb.fork(Clock(self.dut.clk_i, CLOCK_PERIOD_NS).start(cycles=cycle_n))

    def mon_callback(self, t):
        self.expected.append(t)


@cocotb.test()
async def overflow_underflow_test(dut, log_lvl=INFO, cycles=10000):
    cocotb.log.info("----------------------------------------------------------------------------- Simulation Started!")

    swtb = SWTB(dut, log_lvl)
    swtb.setup_dut(cycle_n=cycles)

    # Clear FIFO inputs
    await swtb.sw_drv.clear_sw_input()

    # Reset The FIFO
    await swtb.sw_drv.reset_sw()

    await ClockCycles(dut.clk_i, 2)

    # Reset The FIFO
    await swtb.sw_drv.reset_sw()

    await ClockCycles(dut.clk_i, 2)

    raise TestSuccess("Sim finished sucessfully")


@cocotb.test()
async def rand_access_test(dut, log_lvl=INFO, cycles=1000):
    cocotb.log.info("----------------------------------------------------------------------------- Simulation Started!")

    swtb = SWTB(dut, log_lvl)
    swtb.setup_dut(cycle_n=cycles)

    # Clear FIFO inputs
    await swtb.sw_drv.clear_sw_input()

    # Reset The FIFO
    await swtb.sw_drv.reset_sw()

    # Drive the data
    await swtb.sw_drv.n_rand_data_packets(int(cycles/10))

    await ClockCycles(dut.clk_i, 2)

    raise TestSuccess("Sim finished sucessfully")
