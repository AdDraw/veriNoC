import cocotb
from cocotb.monitors import BusMonitor
from cocotb.triggers import RisingEdge, ReadOnly
from cocotb.binary import BinaryValue
from logging import INFO, DEBUG
import cocotb.handle
import numpy as np
from fifo_imon import FifoIMon


class SWIMon(BusMonitor):
    """
        Input monitor logs the values that appear at the input signals of the module
        Based on the internal mock imitation of the module provides calculated output values
    """

    _signals = ["pckt_sw_i", "wr_en_sw_i", "rst_ni", "nxt_fifo_full_i", "nxt_fifo_overflow_i"]

    _default_config = {
        "packet_x_addr_w": 2,
        "packet_y_addr_w": 2,
        "packet_data_w": 8,
        "packet_w": 12,
        "neighbours_n": 5,
        "fifo_depth_w": 2,
        "x_cord": 0,
        "y_cord": 0
    }

    def __init__(self, entity, name, clock, config=None, log_lvl=INFO, callback=None):
        self.entity = entity
        self.name = name
        self.clock = clock
        self.trans_recv = []

        if config is None:
            self.config = self._default_config
        else:
            self.config = config

        BusMonitor.__init__(self, entity, name, clock, callback=callback)
        if log_lvl == DEBUG:
            self.log.setLevel(DEBUG)
        else:
            self.log.setLevel(INFO)

        self.log.info(f"\nSwitch IMON Setup: {self.config}")

        # initialize INPUT FIFO cycle accurate tested models
        self.input_fifos = []
        for number in range(self.config["neighbours_n"]):
            self.fifo_config = {"fifo_depth_w": self.config["fifo_depth_w"],
                                "fifo_data_w": self.config["packet_w"],
                                "fifo_id": number}

            self.input_fifos.append(FifoIMon(self.entity.genfifo[number].x_input_fifo, "", self.entity.clk_i,
                                             config=self.fifo_config, log_lvl=INFO))

    @cocotb.coroutine
    async def _monitor_recv(self):
        # Monitor Init
        clkedg = RisingEdge(self.clock)
        ro = ReadOnly()

        # Output Regs
        pckt_sw_o = np.zeros(self.config["neighbours_n"])
        wr_en_sw_o = np.zeros(self.config["neighbours_n"])
        in_fifo_full_o = np.zeros(self.config["neighbours_n"])
        in_fifo_overflow_o = np.zeros(self.config["neighbours_n"])

        pckt_sw_nxt = np.zeros(self.config["neighbours_n"])
        wr_en_sw_nxt = np.zeros(self.config["neighbours_n"])
        in_fifo_full_nxt = np.zeros(self.config["neighbours_n"])
        in_fifo_overflow_nxt = np.zeros(self.config["neighbours_n"])

        pckt_in = np.zeros(self.config["neighbours_n"])
        wr_en_in = np.zeros(self.config["neighbours_n"])
        nxt_fifo_full_in = np.zeros(self.config["neighbours_n"])
        nxt_fifo_ovrflw_in = np.zeros(self.config["neighbours_n"])

        while True:
            # Capture the input data
            await clkedg
            await ro

            bus_values = self.bus.capture()
            pckt_sw_i = bus_values["pckt_sw_i"].value
            wr_en_sw_i = bus_values["wr_en_sw_i"].value
            nxt_fifo_overflow_i = bus_values["nxt_fifo_overflow_i"].value
            nxt_fifo_full_i = bus_values["nxt_fifo_full_i"].value
            rst_ni = bus_values["rst_ni"].value

            self.log.debug(f"\nIn Bus {bus_values}")

            if rst_ni == 0:
                # Output Regs
                pckt_sw_o = np.zeros(self.config["neighbours_n"])
                wr_en_sw_o = np.zeros(self.config["neighbours_n"])
                in_fifo_full = np.zeros(self.config["neighbours_n"])
                in_fifo_overflow = np.zeros(self.config["neighbours_n"])
            else:
                pckt_sw_o = pckt_sw_nxt
                wr_en_sw_o = wr_en_sw_nxt
                in_fifo_full_o = in_fifo_full_nxt
                in_fifo_overflow_o = in_fifo_overflow_nxt

                # Calculate NEXT VALUES

                # what happens when wr_en_sw_i is high (any) ?
                # FIFO_HAPPENS
                # how do i make FIFO work in this case

            cycle_results = [pckt_sw_o, wr_en_sw_o, in_fifo_full_o, in_fifo_overflow_o]
            self.log.debug(f"T_i: {cycle_results}")
            self._recv(cycle_results)
            self._recv([0])
