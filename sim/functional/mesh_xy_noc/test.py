import cocotb
from cocotb.result import TestSuccess
from cocotb.triggers import ClockCycles, RisingEdge
from logging import INFO, DEBUG
from cocotb.log import SimLog
import os

from Resource import Resource

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
            "fifo_depth_w": int(os.environ["FIFO_DEPTH_W"])
        }

        self.received = []
        self.rsc_list = []

        for row_id in range(self.config["row_n"]):
            for col_id in range(self.config["col_m"]):
                self.config_rsc = {
                    "row_n": int(os.environ["ROW_N"]),
                    "col_m": int(os.environ["COL_M"]),
                    "pckt_data_w": int(os.environ["PCKT_DATA_W"]),
                    "fifo_depth_w": int(os.environ["FIFO_DEPTH_W"]),
                    "packet_x_addr_w": 2,
                    "packet_y_addr_w": 2,
                    "packet_w": 12,
                    "x_cord": col_id,
                    "y_cord": row_id
                }

                self.rsc_list.append(Resource(dut, "", dut.clk_i, self.config_rsc, callback=self.mon_callback))

    def mon_callback(self, t):
        self.received.append(t)

    def setup_dut(self):
        cocotb.fork(self.reset_hdl())
        self.dut.rst_ni <= 0
        for i in range(3 * 3):
            self.dut.rsc_pckt_i[i] <= 0
        self.dut.rsc_full_i <= 0
        self.dut.rsc_ovrflw_i <= 0
        self.dut.rsc_wren_i <= 0

    def reset_swtb(self):
        for rsc in self.rsc_list:
            rsc.clear_rsc_output(True)

    async def reset_hdl(self):
        await RisingEdge(self.dut.clk_i)
        self.dut.rst_ni <= 0

        await ClockCycles(self.dut.clk_i, 5)
        self.dut.rst_ni <= 1

    def compare(self):

        packets_sent = 0
        for rsc in self.rsc_list:
            packets_sent += rsc.sent_packets
        packets_received = self.received.__len__()
        if packets_received != packets_sent:
            self.log.error(f"Numbers of packets sent and received in the whole NOC is not the same "
                           f"R/S {packets_received}/{packets_sent}")

            for rid, rec in enumerate(self.received):
                self.log.error(f"{rid}:{rec}")
        else:
            self.log.info(f"all packets were routed! rec/sent: {packets_received}/{packets_sent}")
        raise TestSuccess()


@cocotb.test()
async def test(dut, log_lvl=INFO, cycles=100000):
    log = SimLog("test")
    log.setLevel(log_lvl)
    log.info("----------------------------------------------------------------------------- Simulation Started!")

    if int(os.environ['DEBUG_ATTACH']) > 0:
        import pydevd_pycharm
        pydevd_pycharm.settrace('localhost', port=9090, stdoutToServer=True, stderrToServer=True)

    dut._discover_all()
    log.info(dut._sub_handles)
    noctb = NocTB(dut, log_lvl)
    noctb.setup_dut()

    await ClockCycles(dut.clk_i, 100)

    for i in range(9):
        await noctb.rsc_list[i].send_packet_to_xy(i, 0, 1)
        await noctb.rsc_list[i].send_packet_to_xy(i, 0, 2)
        await noctb.rsc_list[i].send_packet_to_xy(i, 1, 0)
        await noctb.rsc_list[i].send_packet_to_xy(i, 1, 1)
        await noctb.rsc_list[i].send_packet_to_xy(i, 1, 2)
        await noctb.rsc_list[i].send_packet_to_xy(i, 2, 0)
        await noctb.rsc_list[i].send_packet_to_xy(i, 2, 1)
        await noctb.rsc_list[i].send_packet_to_xy(i, 2, 2)
        await noctb.rsc_list[i].clear_rsc_output(True)

    await ClockCycles(dut.clk_i, 100)

    noctb.compare()

    raise TestSuccess("jojo")
