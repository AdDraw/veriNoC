import platform
from logging import INFO, DEBUG
import cocotb
from cocotb.clock import Clock
from cocotb.result import TestSuccess, TestError
from cocotb.triggers import ClockCycles, Timer, RisingEdge, ReadOnly
from cocotb.scoreboard import Scoreboard
from mon import CNT_Mon
from random import getrandbits as randbits

@cocotb.coroutine
def reset_dut(reset_n, duration):
    reset_n <= 0
    yield Timer(duration, units='ns')
    reset_n <= 1
    reset_n._log.info("Reset complete")


@cocotb.test()
async def test(dut, log_lvl=INFO, cycles=4000):
    reset_n = dut.rst_ni
    dut.dir_i <= 1

    await reset_dut(reset_n, 100)
    dut._log.info("After reset")
    clock = cocotb.fork(Clock(dut.clk_i, 10, 'ns').start(cycles=10))
    await clock
    dut.dir_i <= 1
    clock = cocotb.fork(Clock(dut.clk_i, 10, 'ns').start(cycles=10))
    await clock
    dut.dir_i <= 0
    clock = cocotb.fork(Clock(dut.clk_i, 10, 'ns').start(cycles=100))
    await clock

    await reset_dut(reset_n, 10)
    raise TestSuccess('Sim finished sucessfully')

@cocotb.test()
async def test(dut, log_lvl=INFO, cycles=4010):
    cocotb.log.info("---------------------------------------------------------------------------- Setup Stage Started!")
    cocotb.log.info("Python version: " + platform.python_version())
    cocotb.log.setLevel(log_lvl)

    cocotb.log.info("----------------------------------------------------------------------------- Simulation Started!")

    que = []

    sb = Scoreboard(dut)
    cocotb.fork(Clock(dut.clk_i, 1000).start(cycles=cycles))

    dut.dir_i <= 0
    dut.rst_ni <= 0

    await ClockCycles(dut.clk_i, 10)
    dut.dir_i <= 0
    dut.rst_ni <= 1

    monitor = CNT_Mon(dut, "", dut.clk_i)
    sb.add_interface(monitor, que)

    for i in range(cycles-10):
        await RisingEdge(dut.clk_i)
        dut.dir_i <= randbits(1)
        await ReadOnly()
        counter_res = dut.counter_o.value.integer
        almost_full = dut.almost_full_o.value.integer
        almost_empty = dut.almost_empty_o.value.integer
        measured_res = [counter_res, almost_full, almost_empty]
        que.append(measured_res)

    cocotb.log.info("---------------------------------------------------------------------------- Simulation Finished!")
    raise TestSuccess("Sim finished sucessfully")
