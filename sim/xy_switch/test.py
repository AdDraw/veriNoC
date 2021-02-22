import cocotb
from cocotb.clock import Clock
from cocotb.result import TestSuccess, TestError
from cocotb.triggers import ClockCycles, RisingEdge
from cocotb.scoreboard import Scoreboard

from driver import SWPacketDriver
from mon_i import SWIMon
from mon_o import SWOMon

from fifo_imon import FifoIMon

from logging import INFO, DEBUG
import os

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
        - output registers hold intermediate values // eee not really

        Communication with other swiches or resources is done through FIFO handshaking

        Data from within the resource comes at the lowest priority.
    """
    def __init__(self, dut, log_lvl=INFO):
        self.dut = dut
        self.dut._discover_all()
        # cocotb.log.info(f"SubHandles: {self.dut._sub_handles}")

        self.config = {
            "packet_x_addr_w": int(os.environ["PACKET_X_ADDR_W"]),
            "packet_y_addr_w": int(os.environ["PACKET_Y_ADDR_W"]),
            "packet_data_w": int(os.environ["PACKET_DATA_W"]),
            "packet_w": int(os.environ["PACKET_W"]),
            "neighbours_n": int(os.environ["PORT_N"]),
            "fifo_depth_w": int(os.environ["IN_FIFO_DEPTH_W"]),
            "x_cord": int(os.environ["X_CORD"]),
            "y_cord": int(os.environ["Y_CORD"])
        }

        self.expected_out = []
        self.sw_drv = SWPacketDriver(dut, "", dut.clk_i, self.config, log_lvl)
        self.sw_i_mon = SWIMon(dut, "", dut.clk_i, self.config, log_lvl, callback=self.mon_callback)
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
async def overflow_underflow_test(dut, log_lvl=INFO, cycles=1000):
    cocotb.log.info("----------------------------------------------------------------------------- Simulation Started!")

    if int(os.environ['DEBUG_ATTACH']) > 0:
        import pydevd_pycharm
        pydevd_pycharm.settrace('localhost', port=9090, stdoutToServer=True, stderrToServer=True)

    swtb = SWTB(dut.xy_switch_inst, log_lvl)
    swtb.setup_dut(cycle_n=cycles)

    # Clear FIFO inputs
    await swtb.sw_drv.clear_sw_input()

    await ClockCycles(dut.clk_i, 10)

    # Reset The FIFO
    # await swtb.sw_drv.reset_sw()

    await ClockCycles(dut.clk_i, 2)

    await RisingEdge(dut.clk_i)
    dut.nxt_fifo_full_i <= pow(2, 5) - 1

    await send5way(swtb)
    await send5way(swtb)
    await send5way(swtb)
    await send5way(swtb)
    await send5way(swtb)
    await send5way(swtb)
    await send5way(swtb)
    await send5way(swtb)
    await send5way(swtb)

    await ClockCycles(dut.clk_i, 10)

    dut.nxt_fifo_full_i <= 0

    await ClockCycles(dut.clk_i, 100)

    raise TestSuccess("Sim finished sucessfully")


async def send5way(swtb):
    await swtb.sw_drv.write_to_single_input(0, 1, 1)  # from Reasource to Resource
    await swtb.sw_drv.write_to_single_input(1, 0, 1)  # sfromend left
    await swtb.sw_drv.write_to_single_input(2, 2, 1)  # send right
    await swtb.sw_drv.write_to_single_input(3, 1, 2)  # send down
    await swtb.sw_drv.write_to_single_input(4, 1, 0)  # send up
