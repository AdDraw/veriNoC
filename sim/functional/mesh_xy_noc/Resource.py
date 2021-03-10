from abc import ABC

from cocotb.drivers import BusDriver
from cocotb.monitors import BusMonitor
from cocotb.triggers import RisingEdge, ClockCycles, ReadOnly, FallingEdge
from cocotb.binary import BinaryValue

from random import getrandbits
from logging import INFO, DEBUG


class Resource(BusDriver, BusMonitor):
    _signals = ["rsc_pckt_i", "rsc_wren_i", "rsc_full_i", "rsc_ovrflw_i",
                "noc_pckt_o", "noc_wren_o", "noc_full_o", "noc_ovrflw_o"]

    _default_config = {
        "packet_x_addr_w": 2,
        "packet_y_addr_w": 2,
        "pckt_data_w": 8,
        "packet_w": 12,
        "fifo_depth_w": 2,
        "row_n": 3,
        "col_m": 3,
        "x_cord": 0,
        "y_cord": 0
    }

    def __init__(self, entity, name, clock, config=None, callback=None, log_lvl=INFO):
        self.entity = entity
        self.name = name
        self.clock = clock

        self.sent_packets = 0
        self.bad_route = 0

        if config is None:
            self.config = self._default_config
        else:
            self.config = config

        self.resource_id = self.config["x_cord"] + self.config["y_cord"]*self.config["row_n"]

        BusMonitor.__init__(self, entity, name, clock, callback=callback)
        BusDriver.__init__(self, entity, name, clock)
        if log_lvl == DEBUG:
            self.log.setLevel(DEBUG)
        else:
            self.log.setLevel(INFO)

        # Reset Input signals

        self.log.info(f"Created RSC({self.config['y_cord']},{self.config['x_cord']}) with RSC_ID={self.resource_id}!")

        self.bus.rsc_pckt_i[self.resource_id].setimmediatevalue(0)
        self.bus.rsc_wren_i[self.resource_id].setimmediatevalue(0)
        self.bus.rsc_full_i[self.resource_id].setimmediatevalue(0)
        self.bus.rsc_ovrflw_i[self.resource_id].setimmediatevalue(0)

    async def send_packet_to_xy(self, data, y_dest, x_dest):
        await RisingEdge(self.clock)

        self.bus.capture()

        if self.entity.noc_full_o[self.resource_id].value == 1:
            await FallingEdge(self.entity.noc_full_o[self.resource_id])

        self.sent_packets += 1
        packet = data
        packet |= (y_dest << self.config["pckt_data_w"])
        packet |= (x_dest << (self.config["pckt_data_w"] + self.config["packet_y_addr_w"]))

        self.bus.rsc_pckt_i[self.resource_id] <= packet
        self.bus.rsc_wren_i[self.resource_id] <= 1

    async def clear_rsc_output(self, sync: bool = True):
        if sync is True:
            await RisingEdge(self.clock)
        self.bus.rsc_pckt_i[self.resource_id] <= 0
        self.bus.rsc_wren_i[self.resource_id] <= 0
        self.bus.rsc_full_i[self.resource_id] <= 0
        self.bus.rsc_ovrflw_i[self.resource_id] <= 0

    def reset(self):
        self.sent_packets = 0
        self.bad_route = 0

    async def _monitor_recv(self):
        while True:
            await RisingEdge(self.clock)
            await ReadOnly()
            self.bus.capture()
            if self.bus.noc_wren_o[self.resource_id].value == 1:
                packet = self.bus.noc_pckt_o[self.resource_id].value.binstr
                self.log.warning(f"RSC({self.config['y_cord']},{self.config['x_cord']}): Received a pckt "
                                 f"{packet}!")

                x_addr = BinaryValue(packet[:self.config["packet_y_addr_w"]],
                                     self.config["packet_x_addr_w"], bigEndian=False).value
                y_addr = BinaryValue(packet[self.config["packet_y_addr_w"]:-self.config["pckt_data_w"]],
                                     self.config["packet_y_addr_w"], bigEndian=False).value

                if not(x_addr == self.config["x_cord"] and y_addr == self.config["y_cord"]):
                    self.bad_route += 1
                    self.log.error(f"RSC({self.config['y_cord']},{self.config['x_cord']}):"
                                   f" Received Badly Routed Packet y_addr: {y_addr}, x_addr:{x_addr}")

                self._recv({"y_addr": y_addr, "x_addr": x_addr, "y_cord": self.config['y_cord'], "x_cord": self.config['x_cord'] })
