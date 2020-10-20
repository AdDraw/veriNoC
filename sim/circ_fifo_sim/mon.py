import cocotb
from cocotb.monitors import BusMonitor
from cocotb.triggers import RisingEdge, ReadOnly
from make import CNT_BITWIDTH, ALMOST_FULL_LEVEL, ALMOST_EMPTY_LEVEL, ENABLE_LOW_SAT, ENABLE_HIGH_SAT


class CNT_Mon(BusMonitor):
    _signals = ["dir_i", "rst_ni", "counter_o", "almost_full_o", "almost_empty_o"]

    def __init__(self, entity, name, clock, callback=None):
        self.entity = entity
        self.name = name
        self.clock = clock
        self.trans_recv = []
        BusMonitor.__init__(self, entity, name, clock, callback=callback)

    @cocotb.coroutine
    async def _monitor_recv(self):
        clkedg = RisingEdge(self.clock)
        ro = ReadOnly()
        i = 0
        counter = 0

        await ro
        while True:
            bus_values = self.bus.capture()
            dir_i = bus_values["dir_i"].value
            rst_ni = bus_values["rst_ni"].value
            counter_o = bus_values["counter_o"].value
            almost_full_o = bus_values["almost_full_o"].value
            almost_empty_o = bus_values["almost_empty_o"].value

            # Counter logic
            if rst_ni == 0:
                counter = 0
            else:
                if dir_i == 1:
                    if counter == (pow(2, CNT_BITWIDTH) - 1) :
                        counter = 0
                    else:
                        counter = counter + 1
                else:
                    if counter == 0:
                        counter = pow(2, CNT_BITWIDTH) - 1
                    else:
                        counter = counter - 1

            if ENABLE_LOW_SAT == 1:
                if counter <= ALMOST_EMPTY_LEVEL:
                    almost_empty = 1
                else:
                    almost_empty = 0
            else:
                almost_empty = 0

            if ENABLE_HIGH_SAT == 1:
                if counter >= ALMOST_FULL_LEVEL:
                    almost_full = 1
                else:
                    almost_full = 0
            else:
                almost_full = 0

            if rst_ni == 1:
                cycle_results = [counter, almost_full, almost_empty]
                self.trans_recv.append(cycle_results)
                i += 1
                if i > 1:
                    self._recv(self.trans_recv[i-2])

            await clkedg
            await ro
