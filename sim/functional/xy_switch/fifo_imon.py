import cocotb
from cocotb_bus.monitors import BusMonitor
from cocotb.triggers import RisingEdge, ReadOnly

from logging import INFO, DEBUG


class FifoIMon(BusMonitor):
    _signals = ["wr_en_i", "rd_en_i", "data_i", "rst_ni"]

    _default_config = {
            "fifo_depth_w": 4,
            "fifo_data_w": 8,
            "fifo_id": 0
    }

    def __init__(self, entity, name, clock, config=None, log_lvl=INFO, callback=None):
        self.entity = entity
        self.name = name
        self.clock = clock
        self.trans_recv = []

        self.cycle_returns = {}

        self.config = self._default_config.copy()
        for configoption, value in config.items():
            self.config[configoption] = value

        BusMonitor.__init__(self, entity, name, clock, callback=callback)
        if log_lvl == DEBUG:
            self.log.setLevel(DEBUG)
        else:
            self.log.setLevel(INFO)

        self.log.info(f"FIFO IMON created: {self.config}")

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

        for number in range(2**self.config["fifo_depth_w"]):
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
                for addr in range(2**self.config["fifo_depth_w"]):
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

                if wr_ptr_nxt == 2**self.config["fifo_depth_w"]:
                    wr_ptr_nxt = 0
                    wr_ptr_plus_one = 1
                elif wr_ptr_nxt == 2**self.config["fifo_depth_w"] - 1:
                    wr_ptr_plus_one = 0
                else:
                    wr_ptr_plus_one = wr_ptr_nxt + 1

                if rd_ptr_nxt == 2**self.config["fifo_depth_w"]:
                    rd_ptr_nxt = 0

            cycle_results = {"data_o": data_o,
                             "empty": empty,
                             "full": full,
                             "underflow": underflow,
                             "overflow": overflow}

            self.log.debug(f"FIFO {self.config['fifo_id']}, T_i: {cycle_results}")

            self.cycle_returns = cycle_results

            self._recv([0])
