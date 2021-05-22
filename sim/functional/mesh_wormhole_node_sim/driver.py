from cocotb_bus.drivers import BusDriver
from cocotb.triggers import RisingEdge, ReadOnly, FallingEdge
from logging import INFO, DEBUG


class NodeVCDriver(BusDriver):
    _signals = ["data_i", "vld_i"]

    _default_config = {
        "in_n": 5,
        "out_m": 5,
        "flit_id_w": 2,
        "flit_data_w": 8,
        "hop_cnt_w": 4
    }

    def __init__(self, entity, name, clock, id, config=None, log_lvl=INFO):
        self.entity = entity
        self.name = name
        self.clock = clock
        self.id = id
        if config is None:
            self.config = self._default_config
        else:
            self.config = config

        BusDriver.__init__(self, entity, name, clock)
        if log_lvl == DEBUG:
            self.log.setLevel(DEBUG)
        else:
            self.log.setLevel(INFO)

        if self.id == -1:
            for i in range(self.config["in_n"]):
                self.bus.data_i[i].setimmediatevalue(0)
                self.bus.vld_i[i].setimmediatevalue(0)
            self.log.info(f"NodeVCDriver {self.id} created!")
        else:
            self.bus.data_i[self.id].setimmediatevalue(0)
            self.bus.vld_i[self.id].setimmediatevalue(0)
            self.log.info(f"NodeVCDriver {self.id} created!")

    async def send_packet(self, packet, input_id=None):
        i = 0
        assert len(packet) > 1, f"Packet is not long enough, needs to have 2 flit, this has only {len(packet)}"
        if input_id is None:
            assert self.id != -1, "DRIVER: This mode cannot be used when id=-1"
            while i != len(packet):
                await RisingEdge(self.clock)
                await ReadOnly()
                if self.entity.in_chan_rdy_o[self.id].value == 1:
                    await FallingEdge(self.clock)
                    self.bus.vld_i[self.id] <= 1
                    self.bus.data_i[self.id] <= packet[i]
                    i += 1
                else:
                    await FallingEdge(self.clock)
                    self.bus.vld_i[self.id] <= 0
                    self.bus.data_i[self.id] <= 0
            await FallingEdge(self.clock)
            self.bus.vld_i[self.id] <= 0
            self.bus.data_i[self.id] <= 0
        else:
            while i != len(packet):
                await RisingEdge(self.clock)
                await ReadOnly()
                if self.entity.in_chan_rdy_o[input_id].value == 1:
                    await FallingEdge(self.clock)
                    self.bus.vld_i[input_id] <= 1
                    self.bus.data_i[input_id] <= packet[i]
                    i += 1
                else:
                    await FallingEdge(self.clock)
                    self.bus.vld_i[input_id] <= 0
                    self.bus.data_i[input_id] <= 0
            await FallingEdge(self.clock)
            self.bus.vld_i[input_id] <= 0
            self.bus.data_i[input_id] <= 0

    async def clear_input(self, sync: bool = True):
        if sync is True:
            await RisingEdge(self.clock)
        self.bus.data_i[self.id].setimmediatevalue(0)
        self.bus.vld_i[self.id].setimmediatevalue(0)
