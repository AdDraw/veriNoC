import cocotb
from cocotb.monitors import BusMonitor
from cocotb.triggers import RisingEdge, ReadOnly
from cocotb.binary import BinaryValue


from logging import INFO, DEBUG
import os

import numpy as np

# TODO: Make a working version


class SWIMon(BusMonitor):
    _signals = ["pckt_sw_i", "pckt_vld_sw_i", "pckt_r_i", "pckt_vld_r_i", "rst_ni"]

    def __init__(self, entity, name, clock, log_lvl=INFO, callback=None):
        self.entity = entity
        self.name = name
        self.clock = clock
        self.trans_recv = []

        self.packet_x_addr_width = int(os.environ["PACKET_X_ADDR_W"])
        self.packet_y_addr_width = int(os.environ["PACKET_Y_ADDR_W"])
        self.packet_data_width = int(os.environ["PACKET_DATA_W"])
        self.packet_width = int(os.environ["PACKET_W"])
        self.neighbours_n = int(os.environ["NEIGHBOURS_N"])

        BusMonitor.__init__(self, entity, name, clock, callback=callback)
        if log_lvl == DEBUG:
            self.log.setLevel(DEBUG)
        else:
            self.log.setLevel(INFO)

    @cocotb.coroutine
    async def _monitor_recv(self):
        # Monitor Init
        clkedg = RisingEdge(self.clock)
        ro = ReadOnly()

        # Wires
        tmp_pckt = 0

        # Output Wires
        busy_o = 0

        # Output Regs
        pckt_sw_o = np.zeros(4)
        pckt_sw_nxt = np.zeros(4)
        pckt_vld_sw_o = np.zeros(4)
        pckt_vld_sw_nxt = np.zeros(4)
        pckt_rd_sw_o = np.zeros(4)
        pckt_rd_sw_nxt = np.zeros(4)

        pckt_r_o = 0
        pckt_r_nxt = 0
        pckt_vld_r_o = 0
        pckt_vld_r_nxt = 0
        pckt_rd_r_o = 0
        pckt_rd_r_nxt = 0

        # for number in range(self.neighbours_n):
        #     pckt_sw_o.append(0)
        #     pckt_sw_nxt.append(0)
        #     pckt_vld_sw_o.append(0)
        #     pckt_vld_sw_nxt.append(0)
        #
        #     pckt_r_o.append(0)
        #     pckt_r_nxt.append(0)
        #     pckt_vld_r_o.append(0)
        #     pckt_vld_r_nxt.append(0)

        while True:
            # Capture the input data
            await clkedg
            await ro

            bus_values = self.bus.capture()
            pckt_sw_i = bus_values["pckt_sw_i"].value
            pckt_vld_sw_i = bus_values["pckt_vld_sw_i"].value
            pckt_r_i = bus_values["pckt_r_i"].value
            pckt_vld_r_i = bus_values["pckt_vld_r_i"].value
            rst_ni = bus_values["rst_ni"].value

            self.log.debug(f"\nIn Bus {bus_values}")

            # if rst_ni == 0:
            #     # Wires
            #     tmp_pckt = 0
            #
            #     # Output Wires
            #     busy_o = 0
            #
            #     # Output Regs
            #     pckt_sw_o = np.zeros(4)
            #     pckt_sw_nxt = np.zeros(4)
            #     pckt_vld_sw_o = np.zeros(4)
            #     pckt_vld_sw_nxt = np.zeros(4)
            #     pckt_rd_sw_o = np.zeros(4)
            #     pckt_rd_sw_nxt = np.zeros(4)
            #
            #     pckt_r_o = 0
            #     pckt_r_nxt = 0
            #     pckt_vld_r_o = 0
            #     pckt_vld_r_nxt = 0
            #     pckt_rd_r_o = 0
            #     pckt_rd_r_nxt = 0
            #
            # else:
            #     pckt_r_o = pckt_r_nxt
            #     pckt_rd_r_o = pckt_rd_r_nxt
            #     pckt_vld_r_o = pckt_vld_r_nxt
            #
            #     pckt_sw_o = pckt_sw_nxt
            #     pckt_vld_sw_o = pckt_vld_sw_nxt
            #     pckt_rd_sw_o = pckt_rd_sw_nxt
            #
            #     # tmp packet assingment
            #     if ()
            #
            #
            #     # FIFO write
            #     if wr_en_i:
            #         if full == 0 or rd_en_i:
            #             fifo[wr_ptr] = data_i
            #             wr_ptr_nxt += 1
            #             overflow_nxt = 0
            #         else:
            #             overflow_nxt = 1
            #
            #     # FIFO read
            #     if rd_en_i:
            #         if empty == 0:
            #             data_nxt = fifo[rd_ptr]
            #             rd_ptr_nxt += 1
            #             underflow_nxt = 0
            #         else:
            #             underflow_nxt = 1
            #
            #     if wr_ptr_nxt == 2**self.fifo_depth_width:
            #         wr_ptr_nxt = 0
            #         wr_ptr_plus_one = 1
            #     elif wr_ptr_nxt == 2**self.fifo_depth_width - 1:
            #         wr_ptr_plus_one = 0
            #     else:
            #         wr_ptr_plus_one = wr_ptr_nxt + 1
            #
            #     if rd_ptr_nxt == 2**self.fifo_depth_width:
            #         rd_ptr_nxt = 0
            #
            # cycle_results = [pckt_rd_sw_o, pckt_sw_o, pckt_vld_sw_o, pckt_r_o, pckt_vld_r_o, pckt_rd_r_o, busy_o]
            # self.log.debug(f"T_i: {cycle_results}")
            # self._recv(cycle_results)
            self._recv([0])
