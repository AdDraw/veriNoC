import cocotb
from cocotb.clock import Clock
from cocotb.result import TestSuccess, TestError, TestFailure
from cocotb.triggers import ClockCycles, RisingEdge, Combine
from driver import SWPacketDriver
from mon_i import SWIMon
from mon_o import SWOMon
from logging import INFO, DEBUG
from cocotb.log import SimLog
from cocotb.regression import TestFactory
import os
from random import randint, getrandbits, sample

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

        self.log = SimLog("swtb")
        self.log.setLevel(log_lvl)

        self.config = {
            "packet_x_addr_w": int(os.environ["PACKET_COL_ADDR_W"]),
            "packet_y_addr_w": int(os.environ["PACKET_ROW_ADDR_W"]),
            "packet_data_w": int(os.environ["PACKET_DATA_W"]),
            "packet_w": int(os.environ["PACKET_W"]),
            "neighbours_n": int(os.environ["PORT_N"]),
            "fifo_depth_w": int(os.environ["IN_FIFO_DEPTH_W"]),
            "x_cord": int(os.environ["COL_CORD"]),
            "y_cord": int(os.environ["ROW_CORD"])
        }

        self.run_stats = []

        self.expected_out = []
        self.seen_out = []
        self.sw_drv = SWPacketDriver(dut, "", dut.clk_i, self.config, log_lvl)
        self.sw_i_mon = SWIMon(dut, "", dut.clk_i, self.config, log_lvl, callback=self.mon_i_callback)
        self.sw_o_mon = SWOMon(dut, "", dut.clk_i, self.config, log_lvl, callback=self.mon_o_callback)

    def setup_dut(self, cycle_n):
        cocotb.fork(self.reset_hdl())

    def reset_swtb(self):
        self.expected_out = []
        self.seen_out = []
        self.sw_drv.reset()
        self.sw_i_mon.reset()
        self.sw_o_mon.reset()

    async def reset_hdl(self):
        await RisingEdge(self.dut.clk_i)
        self.dut.rst_ni <= 0

        await ClockCycles(self.dut.clk_i, 5)
        self.dut.rst_ni <= 1

    def mon_i_callback(self, t):
        self.expected_out.append(t)

    def mon_o_callback(self, t):
        self.seen_out.append(t)

    def compare(self):
        self.log.info("\n------- Simulation Statistics ---------\n")

        self.log.debug(f"Expected Packets N {self.expected_out.__len__()}")
        self.expected_out = sorted(self.expected_out, key=lambda k: k['id'])
        for rid, record in enumerate(self.expected_out):
            self.log.debug(f"{rid}. expected {record}")

        full_input = self.expected_out.copy()
        for record in self.sw_i_mon.loss_packets:
            full_input.append(record)
        full_input = sorted(full_input, key=lambda k: k['id'])
        self.log.debug(f"Lenght of Full {full_input.__len__()}")

        # for rid, record in enumerate(full_input):
        #     self.log.info(f"{rid}. full {record}")

        sorted_seen = sorted(self.seen_out, key=lambda k: k['id'])
        self.log.info(f"Lenght of received packets {sorted_seen.__len__()}")
        for rid, rd2 in enumerate(sorted_seen):
            if rid < self.expected_out.__len__():
                if rd2["id"] == self.expected_out[rid]["id"]:
                    self.log.debug(f"compare {rd2}, {self.expected_out[rid]}")
                else:
                    self.log.debug(f"compare {rd2}, {self.expected_out[rid]}")
            else:
                self.log.error(f"compare {rd2}, This packet was not expected")

        dropped_pckt_n = self.sw_drv.sent_packets - self.sw_o_mon.packets_received
        if dropped_pckt_n == self.sw_i_mon.loss_packets.__len__():
            self.log.info(f"Correctly dropped {self.sw_i_mon.loss_packets.__len__()} packets"
                          f" out of {self.sw_drv.sent_packets} sent packets")
        else:
            self.log.error(f"Dropped {dropped_pckt_n} packets "
                           f"instead of expected {self.sw_i_mon.loss_packets.__len__()} packets!"
                           f" from {self.sw_drv.sent_packets} sent packets")

        if len(self.expected_out) == len(sorted_seen):
            self.log.info(f"Correct number of packets was routed {len(sorted_seen)}/{len(self.expected_out)}")

            fail_cnt = 0
            att_cnt = 0
            should_not_be_sent_cnt = 0
            for r_e, r_s in zip(self.expected_out, sorted_seen):
                if r_e != r_s:
                    if r_e["dst"] == "error" and r_s["dst"] == 0:
                        should_not_be_sent_cnt += 1
                    else:
                        self.log.warning(f"{fail_cnt}: {r_e} != {r_s}")
                        fail_cnt += 1
                att_cnt += 1

            if fail_cnt > 0:
                raise TestFailure(f"Incorrectly routed packets {fail_cnt}/{att_cnt}")
            else:
                self.log.info("All packets that were not dropped were properly routed!")
                if (should_not_be_sent_cnt > 0):
                    self.log.info(f"By mistake, sent {should_not_be_sent_cnt} wrongly addressed packets,"
                                  f" but they were handled properly(send to RESOURCE[TODO: make it smarter])")
                raise TestSuccess(f"All packets that were not dropped were properly routed!")
        else:
            raise TestFailure(f"Incorrect number of packets was routed {len(sorted_seen)}/{len(self.expected_out)}")


@cocotb.test()
async def test_rand_single_input(dut, log_lvl=INFO, transaction_w=8, with_nxt_fifo_rand=True, cycles=100000):
    cocotb.log.info("----------------------------------------------------------------------------- Simulation Started!")

    if int(os.environ['DEBUG_ATTACH']) > 0:
        import pydevd_pycharm
        pydevd_pycharm.settrace('localhost', port=9090, stdoutToServer=True, stderrToServer=True)

    swtb = SWTB(dut.xy_switch_inst, log_lvl)
    swtb.setup_dut(cycle_n=cycles)

    # Clear FIFO inputs
    swtb.reset_swtb()

    await swtb.sw_drv.clear_sw_input()
    await swtb.reset_hdl()

    await ClockCycles(dut.clk_i, 10)

    if transaction_w <= swtb.config["packet_data_w"]:
        transaction_n = pow(2, transaction_w) - 1
    else:
        transaction_n = pow(2, swtb.config["packet_data_w"]) - 1

    for i in range(transaction_n):
        src = randint(0, swtb.config["neighbours_n"]-1)
        x_dest = getrandbits(swtb.config["packet_x_addr_w"])
        y_dest = getrandbits(swtb.config["packet_y_addr_w"])
        await swtb.sw_drv.write_to_single_input(input_id=src, x_dest=x_dest, y_dest=y_dest)

    await swtb.sw_drv.clear_sw_input(True)

    await ClockCycles(dut.clk_i, 100)

    swtb.compare()

if int(os.environ["TESTFACTORY"]):
    tf = TestFactory(test_function=test_rand_single_input)
    tf.add_option(name='transaction_w', optionlist=[*range(10)])
    tf.generate_tests()
