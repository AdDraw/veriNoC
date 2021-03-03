import cocotb
from cocotb.monitors import BusMonitor
from cocotb.triggers import RisingEdge, ReadOnly
import os


class CNT_Mon(BusMonitor):
    _signals = ["dir_i", "rst_ni", "counter_o", "almost_full_o", "almost_empty_o"]

    def __init__(self, entity, name, clock, callback=None):
        self.entity = entity
        self.name = name
        self.clock = clock
        self.trans_recv = []

        self.cnt_w = int(os.environ["CNT_BITWIDTH"])
        self.aempty_lvl = int(os.environ["ALMOST_EMPTY_LEVEL"])
        self.afull_lvl = int(os.environ["ALMOST_FULL_LEVEL"])
        self.en_low_sat = int(os.environ["ENABLE_LOW_SAT"])
        self.en_high_sat = int(os.environ["ENABLE_HIGH_SAT"])

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
                    if counter == (pow(2, self.cnt_w) - 1) :
                        counter = 0
                    else:
                        counter = counter + 1
                else:
                    if counter == 0:
                        counter = pow(2, self.cnt_w) - 1
                    else:
                        counter = counter - 1

            if self.en_low_sat == 1:
                if counter <= self.aempty_lvl:
                    almost_empty = 1
                else:
                    almost_empty = 0
            else:
                almost_empty = 0

            if self.en_high_sat == 1:
                if counter >= self.afull_lvl:
                    almost_full = 1
                else:
                    almost_full = 0
            else:
                almost_full = 0

            if rst_ni == 1:
                cycle_results = {"cnt":counter, "afull": almost_full, "aempty":almost_empty}
                self.trans_recv.append(cycle_results)
                i += 1
                if i > 1:
                    self._recv(self.trans_recv[i-2])

            await clkedg
            await ro
