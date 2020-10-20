import platform
from logging import INFO, DEBUG
import cocotb
from cocotb.clock import Clock
from cocotb.result import TestSuccess, TestError
from cocotb.triggers import ClockCycles, Timer, RisingEdge, FallingEdge,  ReadOnly
from random import getrandbits as randbits

@cocotb.test()
async def test_controlled(dut, log_lvl=INFO, cycles=100):
    cocotb.log.info("---------------------------------------------------------------------------- Setup Stage Started!")
    cocotb.log.info("Python version: " + platform.python_version())
    cocotb.log.setLevel(log_lvl)

    cocotb.log.info("----------------------------------------------------------------------------- Simulation Started!")

    cocotb.fork(Clock(dut.clk_i, 100).start(cycles=cycles))

    dut.rst_ni <= 0

    await ClockCycles(dut.clk_i, 10)
    dut.rst_ni <= 1

    for i in range(11):
        await FallingEdge(dut.clk_i)
        dut.wr_en_i <= 1
        dut.rd_en_i <= 0
        dut.data_i <= randbits(8)

    dut.wr_en_i <= 0
    await ClockCycles(dut.clk_i, 10)

    for i in range(11):
        await FallingEdge(dut.clk_i)
        dut.rd_en_i <= 1
        dut.wr_en_i <= 0

    dut.rd_en_i <= 0
    await ClockCycles(dut.clk_i, 10)

    cocotb.log.info("---------------------------------------------------------------------------- Simulation Finished!")
    raise TestSuccess("Sim finished sucessfully")


@cocotb.test()
async def test_rand(dut, log_lvl=INFO, cycles=100):
    cocotb.log.info("---------------------------------------------------------------------------- Setup Stage Started!")
    cocotb.log.info("Python version: " + platform.python_version())
    cocotb.log.setLevel(log_lvl)

    cocotb.log.info("----------------------------------------------------------------------------- Simulation Started!")

    cocotb.fork(Clock(dut.clk_i, 100).start(cycles=cycles))

    dut.rst_ni <= 0

    await ClockCycles(dut.clk_i, 10)
    dut.rst_ni <= 1

    for i in range(20):
        await FallingEdge(dut.clk_i)
        dut.wr_en_i <= randbits(1)
        dut.rd_en_i <= randbits(1)
        dut.data_i <= randbits(8)

    dut.rd_en_i <= 0
    dut.wr_en_i <= 0
    await ClockCycles(dut.clk_i, 10)

    cocotb.log.info("---------------------------------------------------------------------------- Simulation Finished!")
    raise TestSuccess("Sim finished sucessfully")
