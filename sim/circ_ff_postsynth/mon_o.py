import cocotb
from cocotb.monitors import BusMonitor
from cocotb.triggers import RisingEdge, ReadOnly

from logging import INFO, DEBUG


class FifoOMon(BusMonitor):
    _signals = ["data_o", "empty_o", "full_o", "underflow_o", "overflow_o"]

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
            data_o = bus_values["data_o"].value
            empty_o = bus_values["empty_o"].value
            full_o = bus_values["full_o"].value
            underflow_o = bus_values["underflow_o"].value
            overflow_o = bus_values["overflow_o"].value

            cycle_results = [data_o, empty_o, full_o, underflow_o, overflow_o]
            self.log.debug(f'T_o: {cycle_results}')
            self._recv(cycle_results)
