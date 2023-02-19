from secrets import randbits
import cocotb
from cocotb.clock import Clock
from cocotb.result import TestSuccess
from cocotb.triggers import ClockCycles, RisingEdge, ReadWrite, ReadOnly, FallingEdge

import os

def blip(signal, val):
    signal.setimmediatevalue(val)

@cocotb.test()
async def simple_test(dut):
    cocotb.log.info("----- Simulation Started!")
    clk_obj = Clock(dut.clk_i, 10)
    clk = cocotb.fork(clk_obj.start())
    dut.rst_ni.setimmediatevalue(0)
    await ClockCycles(dut.clk_i, 10)
    dut.rst_ni.setimmediatevalue(1)

    await RisingEdge(dut.clk_i)
    await ReadWrite()

    n = int(os.environ["IN_N"])

    blip(dut.req_i, randbits(n))
    for i in range(10):
        await RisingEdge(dut.clk_i)
        await ReadOnly()
        print(f"{dut.priority_robin.value} AND {dut.req_i.value} => {dut.grant_w.value} : {dut.grant_o.value.integer}")
        await FallingEdge(dut.clk_i)
        await ReadWrite()
        blip(dut.req_i, randbits(n))

    await ClockCycles(dut.clk_i, 10)
    raise TestSuccess("Sim finished sucessfully")

