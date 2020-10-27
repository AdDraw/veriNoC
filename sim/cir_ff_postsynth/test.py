import cocotb
from cocotb.clock import Clock
from cocotb.result import TestSuccess, TestError
from cocotb.triggers import ClockCycles
from cocotb.scoreboard import Scoreboard

from driver import FifoDriver
from mon_i import FifoIMon
from mon_o import FifoOMon

from logging import INFO, DEBUG

CLOCK_PERIOD_NS = 10


class FifoTB:
    def __init__(self, dut, log_lvl=INFO):
        self.dut = dut
        self.fifo_drv = FifoDriver(dut, "", dut.clk_i, log_lvl)
        self.fifo_i_mon = FifoIMon(dut, "", dut.clk_i, log_lvl, callback=self.mon_callback)
        self.fifo_o_mon = FifoOMon(dut, "", dut.clk_i, log_lvl)
        self.expected_out = []
        self.sb = Scoreboard(dut, fail_immediately=True)
        self.sb.add_interface(self.fifo_o_mon, self.expected_out)

    def setup_dut(self, cycle_n):
        cocotb.fork(self.fifo_drv.reset_fifo())
        cocotb.fork(Clock(self.dut.clk_i, CLOCK_PERIOD_NS).start(cycles=cycle_n))

    def mon_callback(self, t):
        self.expected_out.append(t)


@cocotb.test()
async def overflow_underflow_test(dut, log_lvl=INFO, cycles=10000):
    cocotb.log.info("----------------------------------------------------------------------------- Simulation Started!")

    fftb = FifoTB(dut, log_lvl)
    fftb.setup_dut(cycle_n=cycles)

    # Clear FIFO inputs
    await fftb.fifo_drv.clear_fifo_input()

    # Reset The FIFO
    await fftb.fifo_drv.reset_fifo()

    # Drive the data
    await fftb.fifo_drv.fill_fifo()

    # Read the data
    await fftb.fifo_drv.empty_fifo()

    await ClockCycles(dut.clk_i, 2)

    # Reset The FIFO
    await fftb.fifo_drv.reset_fifo()

    await ClockCycles(dut.clk_i, 2)

    raise TestSuccess("Sim finished sucessfully")


@cocotb.test()
async def rand_access_test(dut, log_lvl=INFO, cycles=1000):
    cocotb.log.info("----------------------------------------------------------------------------- Simulation Started!")

    fftb = FifoTB(dut, log_lvl)
    fftb.setup_dut(cycle_n=cycles)

    # Clear FIFO inputs
    await fftb.fifo_drv.clear_fifo_input()

    # Reset The FIFO
    await fftb.fifo_drv.reset_fifo()

    # Drive the data
    await fftb.fifo_drv.n_rand_transactions(int(cycles/10))
    await fftb.fifo_drv.n_rand_transactions_reset(int(cycles/10))

    await ClockCycles(dut.clk_i, 2)

    raise TestSuccess("Sim finished sucessfully")
