import cocotb
from cocotb.monitors import BusMonitor
from cocotb.triggers import RisingEdge, ReadOnly

from logging import INFO, DEBUG

# TODO: Make a working version

class SWOMon(BusMonitor):
    _signals = ["busy_o", "pckt_sw_o", "pckt_r_o", "pckt_vld_r_o", "pckt_rd_sw_o"]

    def __init__(self, entity, name, clock, log_lvl=INFO, callback=None):
        self.entity = entity
        self.name = name
        self.clock = clock
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

        while True:
            # Capture the output data
            await clkedg
            await ro
            bus_values = self.bus.capture()
            busy_o = bus_values["busy_o"].value
            pckt_sw_o = bus_values["pckt_sw_o"].value
            pckt_r_o = bus_values["pckt_r_o"].value
            pckt_vld_r_o = bus_values["pckt_vld_r_o"].value
            pckt_rd_sw_o = bus_values["pckt_rd_sw_o"].value

            cycle_results = [busy_o, pckt_sw_o, pckt_r_o, pckt_vld_r_o, pckt_rd_sw_o]
            self.log.debug(f'T_o: {cycle_results}')
            self._recv(cycle_results)
