import cocotb
from cocotb.monitors import BusMonitor
from cocotb.triggers import RisingEdge, ReadOnly

from logging import INFO, DEBUG

# TODO: Make a working version

# Output monitor that collects the data from the output signals of the module property
# Used to compare with the input monitor in the ScoreBoard object
class SWOMon(BusMonitor):
    _signals = [ "in_fifo_full_o", "in_fifo_overflow_o", "wr_en_sw_o", "pckt_sw_o"]

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
            in_fifo_full_o = bus_values["in_fifo_full_o"].value
            in_fifo_overflow_o = bus_values["in_fifo_overflow_o"].value
            wr_en_sw_o = bus_values["wr_en_sw_o"].value
            pckt_sw_o = bus_values["pckt_sw_o"].value

            cycle_results = [in_fifo_full_o, in_fifo_overflow_o, wr_en_sw_o, pckt_sw_o]
            self.log.debug(f'T_o: {cycle_results}')
            self._recv(cycle_results)
