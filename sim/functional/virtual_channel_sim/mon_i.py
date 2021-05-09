import cocotb
from cocotb_bus.monitors import BusMonitor
from cocotb.triggers import RisingEdge, ReadOnly

from logging import INFO, DEBUG
import os


class FifoIMon(BusMonitor):
    _signals = ["wr_en_i", "rd_en_i", "data_i", "rst_ni"]

    def __init__(self, entity, name, clock, log_lvl=INFO, callback=None):
        self.entity = entity
        self.name = name
        self.clock = clock
        self.trans_recv = []
        self.fifo_depth_width = int(os.environ["FIFO_DEPTH_WIDTH"])
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
        fifo = []

        wr_ptr = 0
        wr_ptr_nxt = 0
        wr_ptr_plus_one = 1

        rd_ptr = 0
        rd_ptr_nxt = 0

        underflow = 0
        underflow_nxt = 0

        overflow = 0
        overflow_nxt = 0

        data_o = 0
        data_nxt = 0

        for number in range(2**self.fifo_depth_width):
            fifo.append(0)

        while True:
            # Capture the input data
            await clkedg
            await ro

            bus_values = self.bus.capture()
            wr_en_i = bus_values["wr_en_i"].value
            rd_en_i = bus_values["rd_en_i"].value
            data_i = bus_values["data_i"].value
            rst_ni = bus_values["rst_ni"].value

            self.log.debug(f"\nIn Bus {bus_values}")

            if rst_ni == 0:
                empty = 1
                full = 0
                data_o = 0
                wr_ptr = 0
                wr_ptr_plus_one = 1

                rd_ptr = 0
                underflow = 0
                overflow = 0
                for addr in range(2**self.fifo_depth_width):
                    fifo[addr] = 0

                data_nxt = 0
                wr_ptr_nxt = 0
                rd_ptr_nxt = 0
                underflow_nxt = 0
                overflow_nxt = 0

            else:
                data_o = data_nxt
                wr_ptr = wr_ptr_nxt
                rd_ptr = rd_ptr_nxt
                underflow = underflow_nxt
                overflow = overflow_nxt

                self.log.debug(f"wr_ptr: {wr_ptr}, rd_ptr: {rd_ptr}")

                if wr_ptr_plus_one == rd_ptr:
                    full = 1
                else:
                    full = 0

                if wr_ptr == rd_ptr:
                    empty = 1
                else:
                    empty = 0

                # FIFO write
                if wr_en_i:
                    if full == 0 or rd_en_i:
                        fifo[wr_ptr] = data_i
                        wr_ptr_nxt += 1
                        overflow_nxt = 0
                    else:
                        overflow_nxt = 1

                # FIFO read
                if rd_en_i:
                    if empty == 0:
                        data_nxt = fifo[rd_ptr]
                        rd_ptr_nxt += 1
                        underflow_nxt = 0
                    else:
                        underflow_nxt = 1

                if wr_ptr_nxt == 2**self.fifo_depth_width:
                    wr_ptr_nxt = 0
                    wr_ptr_plus_one = 1
                elif wr_ptr_nxt == 2**self.fifo_depth_width - 1:
                    wr_ptr_plus_one = 0
                else:
                    wr_ptr_plus_one = wr_ptr_nxt + 1

                if rd_ptr_nxt == 2**self.fifo_depth_width:
                    rd_ptr_nxt = 0

                if full == 0:
                    overflow = 0

                if empty == 0:
                    underflow = 0

            cycle_results = {"data": data_o, "empty": empty, "full": full, "underflow": underflow, "overflow": overflow}
            self.log.debug(f"T_i: {cycle_results}")
            self._recv(cycle_results)
