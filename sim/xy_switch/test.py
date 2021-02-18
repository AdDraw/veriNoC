import cocotb
from cocotb.clock import Clock
from cocotb.result import TestSuccess, TestError
from cocotb.triggers import ClockCycles, RisingEdge
from cocotb.scoreboard import Scoreboard

from driver import SWPacketDriver
from mon_i import SWIMon
from mon_o import SWOMon

from logging import INFO, DEBUG

CLOCK_PERIOD_NS = 10

class SWTB:
    """
        TB suite for a singular XY Switch
        inputs should be driven by FIFO drivers ( multiple or one )
        Monitors should look at the outputs

        XY Switch has:
        - input buffers done as circular FIFOs
        - XY routing
        - Static priority based input chooser (arbiter)
        - output registers hold intermediate values

        Communication with other swiches or resources is done through FIFO handshaking

        Data from within the resource comes at the lowest priority.
    """
    def __init__(self, dut, log_lvl=INFO):
        self.dut = dut
        self.expected_out = []
        self.sw_drv = SWPacketDriver(dut, "", dut.clk_i, log_lvl)
        # self.sw_i_mon = SWIMon(dut, "", dut.clk_i, log_lvl, callback=self.mon_callback)
        # self.sw_o_mon = SWOMon(dut, "", dut.clk_i, log_lvl)
        # self.sb = Scoreboard(dut, fail_immediately=False)
        # self.sb.add_interface(self.sw_o_mon, self.expected_out)

    def setup_dut(self, cycle_n):
        cocotb.fork(self.reset_sw())
        cocotb.fork(Clock(self.dut.clk_i, CLOCK_PERIOD_NS).start(cycles=cycle_n))

    async def reset_sw(self):
        await RisingEdge(self.dut.clk_i)
        self.dut.rst_ni <= 0

        await ClockCycles(self.dut.clk_i, 5)
        self.dut.rst_ni <= 1

    def mon_callback(self, t):
        self.expected_out.append(t)


@cocotb.test()
async def overflow_underflow_test(dut, log_lvl=INFO, cycles=10000):
    cocotb.log.info("----------------------------------------------------------------------------- Simulation Started!")

    swtb = SWTB(dut, log_lvl)
    swtb.setup_dut(cycle_n=cycles)

    # Clear FIFO inputs
    await swtb.sw_drv.clear_sw_input()

    await ClockCycles(dut.clk_i, 10)

    # Reset The FIFO
    # await swtb.sw_drv.reset_sw()

    await ClockCycles(dut.clk_i, 2)

    await RisingEdge(dut.clk_i)
    dut.nxt_fifo_full_i <= pow(2, 5) - 1

    await swtb.sw_drv.write_to_single_input(0, 1, 1, 1)  # from Reasource to Resource
    await swtb.sw_drv.write_to_single_input(1, 2, 0, 1)  # send left
    await swtb.sw_drv.write_to_single_input(2, 3, 2, 1)  # send right
    await swtb.sw_drv.write_to_single_input(3, 4, 1, 2)  # send down
    await swtb.sw_drv.write_to_single_input(4, 5, 1, 0)  # send up

    await swtb.sw_drv.write_to_single_input(0, 6, 1, 1)  # from Reasource to Resource
    await swtb.sw_drv.write_to_single_input(1, 7, 0, 1)  # send left
    await swtb.sw_drv.write_to_single_input(2, 8, 2, 1)  # send right
    await swtb.sw_drv.write_to_single_input(3, 9, 1, 2)  # send down
    await swtb.sw_drv.write_to_single_input(4, 10, 1, 0)  # send up

    await swtb.sw_drv.write_to_single_input(0, 11, 1, 1)  # from Reasource to Resource
    await swtb.sw_drv.write_to_single_input(1, 12, 0, 1)  # send left
    await swtb.sw_drv.write_to_single_input(2, 13, 2, 1)  # send right
    await swtb.sw_drv.write_to_single_input(3, 14, 1, 2)  # send down
    await swtb.sw_drv.write_to_single_input(4, 15, 1, 0)  # send up

    await ClockCycles(dut.clk_i, 10)

    dut.nxt_fifo_full_i <= 0

    await ClockCycles(dut.clk_i, 20)

    raise TestSuccess("Sim finished sucessfully")


# @cocotb.test()
# async def rand_access_test(dut, log_lvl=INFO, cycles=1000):
#     cocotb.log.info("----------------------------------------------------------------------------- Simulation Started!")
#
#     swtb = SWTB(dut, log_lvl)
#     swtb.setup_dut(cycle_n=cycles)
#
#     # Clear FIFO inputs
#     await swtb.sw_drv.clear_sw_input()
#
#     # Reset The FIFO
#     await swtb.sw_drv.reset_sw()
#
#     # Drive the data
#     await swtb.sw_drv.n_rand_data_packets(int(cycles/10))
#
#     await ClockCycles(dut.clk_i, 2)
#
#     raise TestSuccess("Sim finished sucessfully")
