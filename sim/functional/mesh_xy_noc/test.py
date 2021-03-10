import cocotb
from cocotb.result import TestSuccess
from cocotb.triggers import ClockCycles, RisingEdge
from logging import INFO, DEBUG
from cocotb.log import SimLog
import os

CLOCK_PERIOD_NS = 10


class NocTB:
    """
        TB suite for a MESH NOC with XY Routing
        inputs are to be driven from RESOURCES DRIVERS
        outputs should be checked by the RESOURCE MONITORS

        1)  check if everything correctly landed into the correct DESTINATION
            dst is defined by X_ADDR & Y_ADDR and those need to be equal to X_CORD & Y_CORD
            of the RESOURCE

        TODO: 2) Check for DeadLocks & LiveLocks
        TODO: 3) Check Latency & Collect Measurements

        Mesh NoC has:
        - N Rows of switches
        - M Columns of switches
        - Each switch is connected to min 2 neighboring switches
        - XY routing

        Data from within the resource comes at the lowest priority.
    """
    def __init__(self, dut, log_lvl=INFO):
        self.dut = dut
        self.dut._discover_all()

        self.log = SimLog("swtb")
        self.log.setLevel(log_lvl)

        self.config = {
            "row_n": int(os.environ["ROW_N"]),
            "col_m": int(os.environ["COL_M"]),
            "pckt_data_w": int(os.environ["PCKT_DATA_W"]),
            "fifo_depth_w": int(os.environ["FIFO_DEPTH_W"]),
        }

        # self.sw_drv = SWPacketDriver(dut, "", dut.clk_i, self.config, log_lvl)
        # self.sw_i_mon = SWIMon(dut, "", dut.clk_i, self.config, log_lvl)
        # self.sw_o_mon = SWOMon(dut, "", dut.clk_i, self.config, log_lvl)

    def setup_dut(self, cycle_n):
        cocotb.fork(self.reset_hdl())

        self.dut.rst_ni <= 0
        self.dut.rsc_pckt_o <= 0
        self.dut.rsc_full_o <= 0
        self.dut.rsc_ovrflw_o <= 0
        self.dut.rsc_wren_o <= 0

    # def reset_swtb(self):

    async def reset_hdl(self):
        await RisingEdge(self.dut.clk_i)
        self.dut.rst_ni <= 0

        await ClockCycles(self.dut.clk_i, 5)
        self.dut.rst_ni <= 1


@cocotb.test()
async def test(dut, log_lvl=INFO, cycles=100000):
    log = SimLog("test")
    log.setLevel(log_lvl)
    log.info("----------------------------------------------------------------------------- Simulation Started!")

    if int(os.environ['DEBUG_ATTACH']) > 0:
        import pydevd_pycharm
        pydevd_pycharm.settrace('localhost', port=9090, stdoutToServer=True, stderrToServer=True)

    noctb = NocTB(dut.inst_mesh_xy_noc, log_lvl)
    noctb.setup_dut(cycle_n=cycles)


    await ClockCycles(dut.clk_i, 100)


    # from 0,0 to 1,1
    await RisingEdge(dut.clk_i)
    dut.inst_mesh_xy_noc.rsc_pckt_o <= 1535
    dut.inst_mesh_xy_noc.rsc_wren_o <= 1

    await RisingEdge(dut.clk_i)
    dut.inst_mesh_xy_noc.rsc_pckt_o <= 0
    dut.inst_mesh_xy_noc.rsc_wren_o <= 0

    await ClockCycles(dut.clk_i, 100)


    # from 0,0 to 2,2
    await RisingEdge(dut.clk_i)
    dut.inst_mesh_xy_noc.rsc_pckt_o <= 0b101010101010
    dut.inst_mesh_xy_noc.rsc_wren_o <= 1

    await RisingEdge(dut.clk_i)
    dut.inst_mesh_xy_noc.rsc_pckt_o <= 0
    dut.inst_mesh_xy_noc.rsc_wren_o <= 0

    await ClockCycles(dut.clk_i, 100)


    # from 0,0 to 0,2
    await RisingEdge(dut.clk_i)
    dut.inst_mesh_xy_noc.rsc_pckt_o <= 0b001010111011
    dut.inst_mesh_xy_noc.rsc_wren_o <= 1

    await RisingEdge(dut.clk_i)
    dut.inst_mesh_xy_noc.rsc_pckt_o <= 0
    dut.inst_mesh_xy_noc.rsc_wren_o <= 0

    await ClockCycles(dut.clk_i, 100)


    # from 0,0 to 2,0
    await RisingEdge(dut.clk_i)
    dut.inst_mesh_xy_noc.rsc_pckt_o <= 0b100011001100
    dut.inst_mesh_xy_noc.rsc_wren_o <= 1

    await RisingEdge(dut.clk_i)
    dut.inst_mesh_xy_noc.rsc_pckt_o <= 0
    dut.inst_mesh_xy_noc.rsc_wren_o <= 0

    await ClockCycles(dut.clk_i, 100)

    raise TestSuccess("jojo")




