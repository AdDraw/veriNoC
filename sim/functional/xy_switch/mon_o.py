import cocotb
from cocotb_bus.monitors import BusMonitor
from cocotb.triggers import RisingEdge, ReadOnly
from cocotb.binary import BinaryValue

from logging import INFO, DEBUG

# Output monitor that collects the data from the output signals of the module property
# Used to compare with the input monitor in the ScoreBoard object


class SWOMon(BusMonitor):
    _signals = ["in_fifo_full_o", "in_fifo_overflow_o", "wr_en_sw_o", "pckt_sw_o"]

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

        self.packets_received = 0

        if config is None:
            self.config = self._default_config
        else:
            self.config = config

        self.port_n = self.config["neighbours_n"] - 1

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

        self.packets_received = 0

        while True:
            # Capture the output data
            await clkedg
            await ro
            bus_values = self.bus.capture()

            wr_en_sw_o = bus_values["wr_en_sw_o"].binstr
            pckt_sw_o = bus_values["pckt_sw_o"].binstr

            for bid, wr_en_o in enumerate(wr_en_sw_o):
                if wr_en_o == "1":
                    self.packets_received += 1

                    self.log.debug(f"Numbers of received packets {self.packets_received}")

                    string = pckt_sw_o
                    n = self.config["packet_w"]
                    packet_sw_i_split = [(string[i:i + n]) for i in range(0, len(string), n)]

                    self.log.debug(packet_sw_i_split)

                    chosen_pckt = packet_sw_i_split[bid]

                    data = BinaryValue(chosen_pckt[self.config['packet_y_addr_w'] + self.config['packet_x_addr_w']:self.config['packet_w']],
                                       self.config["packet_data_w"], bigEndian=False).value

                    cycle_results = {"id": data, "dst": self.port_n - bid, "orig": chosen_pckt}
                    self.log.debug(f'T_o: {cycle_results}')
                    self._recv(cycle_results)

    def reset(self):
        self.packets_received = 0
