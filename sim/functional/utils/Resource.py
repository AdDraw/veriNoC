from cocotb_bus.drivers import BusDriver
from cocotb_bus.monitors import BusMonitor
from cocotb.triggers import RisingEdge, ReadOnly, ReadWrite
from cocotb.binary import BinaryValue
from cocotb.log import SimLog
from cocotb.utils import get_sim_time
from cocotb import fork

from logging import INFO, DEBUG


class Resource(BusDriver, BusMonitor):
    _signals = ["rsc_pckt_i", "rsc_wren_i", "rsc_full_i", "rsc_ovrflw_i",
                "noc_pckt_o", "noc_wren_o", "noc_full_o", "noc_ovrflw_o"]

    _default_config = {
        "packet_col_addr_w": 2,
        "packet_row_addr_w": 2,
        "pckt_data_w": 8,
        "packet_w": 12,
        "fifo_depth_w": 2,
        "row_n": 3,
        "col_m": 3,
        "col_cord": 0,
        "row_cord": 0
    }

    def __init__(self, entity, name, clock, config=None, callback=None, log_lvl=INFO):
        self.entity = entity
        self.name = name
        self.clock = clock

        self.sent_packets = []
        self.dropped_packet_n = 0
        self.received_pckts = []
        self.bad_route = []

        self.que = []

        if config is None:
            self.config = self._default_config
        else:
            self.config = config

        self.id = self.config["row_cord"]*self.config["col_m"] + self.config["col_cord"]

        BusMonitor.__init__(self, entity, name, clock, callback=callback)
        BusDriver.__init__(self, entity, name, clock)

        self.log = SimLog(f"rsc_{self.id}")
        if log_lvl == DEBUG:
            self.log.setLevel(DEBUG)
        else:
            self.log.setLevel(INFO)

        self.log.debug(f"Created RSC({self.config['row_cord']},{self.config['col_cord']}) with RSC_ID={self.id}! {self.config}")

        # Reset Input signals
        self.bus.rsc_pckt_i[self.id].setimmediatevalue(0)
        self.bus.rsc_wren_i[self.id].setimmediatevalue(0)
        self.bus.rsc_full_i[self.id].setimmediatevalue(0)
        self.bus.rsc_ovrflw_i[self.id].setimmediatevalue(0)

        fork(self.input_que())

    def send_packet_to_xy(self, data, row_dest, col_dest):
        assert 0 <= row_dest < self.config["row_n"], "Wrong row_dest value"
        assert 0 <= col_dest < self.config["col_m"], "Wrong col_dest value"
        self.que.append({"data": data, "row_dest": row_dest, "col_dest": col_dest})
        time = get_sim_time(units="ns")
        self.sent_packets.append({"source": self.id,
                                  "sink": row_dest*self.config['row_n'] + col_dest,
                                  "row_dest": row_dest,
                                  "col_dest": col_dest,
                                  "data": data,
                                  "time": time})

    async def input_que(self):
        while True:
            while True:
                if len(self.que) != 0:
                    data = self.que[0]["data"]
                    row_dest = self.que[0]["row_dest"]
                    col_dest = self.que[0]["col_dest"]
                    packet = data
                    packet |= (col_dest << self.config["pckt_data_w"])
                    packet |= (row_dest << (self.config["pckt_data_w"] + self.config["packet_col_addr_w"]))
                    await ReadWrite()
                    if self.bus.noc_full_o[self.id].value == 0:
                        self.bus.rsc_pckt_i[self.id] <= packet
                        self.bus.rsc_wren_i[self.id] <= 1
                        self.que.pop(0)
                        break
                    else:
                        await RisingEdge(self.clock)
                        await self.clear_rsc_output(sync=False)
                else:
                    await RisingEdge(self.clock)
                    await self.clear_rsc_output(sync=False)
            await RisingEdge(self.clock)
            await self.clear_rsc_output(sync=False)

    async def clear_rsc_output(self, sync: bool = True):
        if sync is True:
            await RisingEdge(self.clock)
        self.bus.rsc_pckt_i[self.id] <= 0
        self.bus.rsc_wren_i[self.id] <= 0
        self.bus.rsc_full_i[self.id] <= 0
        self.bus.rsc_ovrflw_i[self.id] <= 0

    async def reset_rsc(self):
        self.sent_packets = 0
        self.bad_route = 0
        await self.clear_rsc_output()

    async def _monitor_recv(self):
        while True:
            await RisingEdge(self.clock)
            await ReadOnly()

            time = get_sim_time(units="ns")

            self.bus.capture()
            if self.bus.noc_wren_o[self.id].value == 1:
                packet = self.bus.noc_pckt_o[self.id].value.binstr
                self.log.debug(f"RSC({self.config['row_cord']},{self.config['col_cord']}): Received a pckt {packet}!")

                row_addr = BinaryValue(packet[0:self.config["packet_row_addr_w"]],
                                       self.config["packet_row_addr_w"], bigEndian=False).value

                col_addr = BinaryValue(packet[self.config['packet_row_addr_w']:self.config['packet_row_addr_w'] +
                                       self.config['packet_col_addr_w']], self.config["packet_col_addr_w"],
                                       bigEndian=False).value

                data = BinaryValue(packet[self.config['packet_row_addr_w'] + self.config['packet_col_addr_w']
                                   :self.config['packet_w']], self.config["pckt_data_w"], bigEndian=False).value

                if not(col_addr == self.config["col_cord"] and row_addr == self.config["row_cord"]):
                    self.bad_route.append({"sink": self.id, "row_dest": row_addr, "col_dest": col_addr,
                                           "data": data, "time": time})
                    self.log.debug(f"RSC({self.config['row_cord']},{self.config['col_cord']}):"
                                   f" Received Badly Routed Packet row_addr: {row_addr}, col_addr:{col_addr},"
                                   f" source {data}")
                else:
                    self.received_pckts.append({"sink": self.id, "row_dest": row_addr, "col_dest": col_addr,
                                                "data": data, "time": time})

                    self._recv({"sink": self.id, "row_dest": row_addr, "col_dest": col_addr,
                                "data": data, "time": time})
