from cocotb_bus.monitors import BusMonitor
from cocotb.triggers import RisingEdge, ReadOnly
from cocotb.binary import BinaryValue
from logging import INFO, DEBUG
import cocotb.handle
import numpy as np
from fifo_imon import FifoIMon


CENTER  = 0
EDGE_RT = 1
EDGE_LT = 2
EDGE_RB = 3
EDGE_LB = 4
SIDE_R  = 5
SIDE_L  = 6
SIDE_T  = 7
SIDE_B  = 8

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
        "y_cord": 0,
        "sw_config": 0
    }

    def __init__(self, entity, name, clock, config=None, log_lvl=INFO, callback=None):
        self.entity = entity
        self.name = name
        self.clock = clock

        self.acc_packets = []
        self.loss_packets = []

        if config is None:
            self.config = self._default_config
        else:
            self.config = config

        self.port_n = self.config["neighbours_n"] - 1
        self.directions = {}
        self.sw_type = None
        self.sw_type_config(self.config["sw_config"])

        # initialize INPUT FIFO cycle accurate tested models
        self.input_fifos = []
        for number in range(self.config["neighbours_n"]):
            self.fifo_config = {"fifo_depth_w": self.config["fifo_depth_w"],
                                "fifo_data_w": self.config["packet_w"],
                                "fifo_id": number}

            self.input_fifos.append(FifoIMon(self.entity.genfifo[number].x_input_fifo, "", self.entity.clk_i,
                                             config=self.fifo_config, log_lvl=INFO))

        BusMonitor.__init__(self, entity, name, clock, callback=callback)
        if log_lvl == DEBUG:
            self.log.setLevel(DEBUG)
        else:
            self.log.setLevel(INFO)

        self.log.info(f"\nSwitch IMON Setup: {self.config}")
        self.log.info(f"SW CONFIG {self.sw_type} resulted in {self.directions}")

    @cocotb.coroutine
    async def _monitor_recv(self):
        # Monitor Init
        clkedg = RisingEdge(self.clock)
        ro = ReadOnly()

        in_fifo_full_cur = np.zeros(self.config["neighbours_n"])
        in_fifo_overflow_cur = np.zeros(self.config["neighbours_n"])
        in_fifo_rd_en_i_cur = np.zeros(self.config["neighbours_n"])

        while True:
            # Capture the input data
            await clkedg
            await ro

            for fifo_id, fifo in enumerate(self.input_fifos):
                in_fifo_full_cur[fifo_id] = fifo.cycle_returns["full"]
                in_fifo_overflow_cur[fifo_id] = fifo.cycle_returns["overflow"]
                in_fifo_rd_en_i_cur[fifo_id] = fifo.bus.capture()["rd_en_i"].value

            bus_values = self.bus.capture()
            pckt_sw_i = bus_values["pckt_sw_i"]
            wr_en_sw_i = bus_values["wr_en_sw_i"]
            rst_ni = bus_values["rst_ni"].value

            self.log.debug(f"SWIMON {bus_values}")

            for bid, wr_en in enumerate(wr_en_sw_i.binstr):
                if wr_en == "1" and rst_ni == 1:
                    string = pckt_sw_i.binstr
                    n = self.config["packet_w"]
                    packet_sw_i_split = [(string[i:i + n]) for i in range(0, len(string), n)]
                    chosen_pckt = packet_sw_i_split[bid]

                    data = BinaryValue(chosen_pckt[self.config['packet_y_addr_w'] + self.config['packet_x_addr_w']:self.config['packet_w']],
                                       self.config["packet_data_w"], bigEndian=False).value
                    x_addr = BinaryValue(chosen_pckt[self.config['packet_y_addr_w']:self.config['packet_y_addr_w'] + self.config['packet_x_addr_w']],
                                         self.config["packet_x_addr_w"], bigEndian=False).value
                    y_addr = BinaryValue(chosen_pckt[0:self.config["packet_y_addr_w"]],
                                         self.config["packet_y_addr_w"], bigEndian=False).value

                    if not in_fifo_full_cur[self.port_n-bid] or (in_fifo_full_cur[self.port_n-bid] and in_fifo_rd_en_i_cur[self.port_n-bid]):
                        # Router XY algorithm

                        if x_addr == self.config["x_cord"]:
                            if y_addr == self.config["y_cord"]:
                                dst = self.directions["resource"]
                            elif y_addr < self.config["y_cord"]:
                                dst = self.directions["up"]
                            else:
                                dst = self.directions["down"]
                        elif x_addr > self.config["x_cord"]:
                            dst = self.directions["right"]
                        else:
                            dst = self.directions["left"]

                        cycle_results = {"id": data, "dst": dst, "orig": chosen_pckt}
                        self.log.debug(f"Acc {self.acc_packets.__len__()}. {cycle_results}, src: {self.port_n-bid}")

                        self.acc_packets.append(cycle_results)
                        self._recv(cycle_results)

                    else:
                        cycle_results = {"id": data,
                                         "bid": self.port_n-bid,
                                         "full": in_fifo_full_cur[self.port_n-bid],
                                         "fifo_id": self.input_fifos[self.port_n-bid].config["fifo_id"],
                                         "ovrflow": in_fifo_overflow_cur[bid],
                                         "wr_en": wr_en_sw_i.binstr}

                        self.log.debug(f"Loss {cycle_results}")

                        self.loss_packets.append(cycle_results)

    def reset(self):
        self.acc_packets = []
        self.acc_packets = []

    def sw_type_config(self, sw_config):
        if sw_config == CENTER:
            self.sw_type = "CENTER"
            self.directions = {"resource": 0, "left": 1, "up": 2, "right": 3, "down": 4}
        elif sw_config == EDGE_LB:
            self.sw_type = "EDGE_LB"
            self.directions = {"resource": 0, "left": "error", "up": 1, "right": 2, "down": 0}
        elif sw_config == EDGE_LT:
            self.sw_type = "EDGE_LT"
            self.directions = {"resource": 0, "left": "error", "up": "error", "right": 1, "down": 2}
        elif sw_config == EDGE_RB:
            self.sw_type = "EDGE_RB"
            self.directions = {"resource": 0, "left": 1, "up": 2, "right": "error", "down": "error"}
        elif sw_config == EDGE_RT:
            self.sw_type = "EDGE_RT"
            self.directions = {"resource": 0, "left": 1, "up": "error", "right": "error", "down": 2}
        elif sw_config == SIDE_L:
            self.sw_type = "SIDE_L"
            self.directions = {"resource": 0, "left": "error", "up": 1, "right": 2, "down": 3}
        elif sw_config == SIDE_R:
            self.sw_type = "SIDE_R"
            self.directions = {"resource": 0, "left": 1, "up": 2, "right": "error", "down": 3}
        elif sw_config == SIDE_T:
            self.sw_type = "SIDE_T"
            self.directions = {"resource": 0, "left": 1, "up": "error", "right": 2, "down": 3}
        elif sw_config == SIDE_B:
            self.sw_type = "SIDE_B"
            self.directions = {"resource": 0, "left": 1, "up": 2, "right": 3, "down": "error"}
