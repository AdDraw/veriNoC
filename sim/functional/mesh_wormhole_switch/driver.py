from logging import DEBUG, INFO

from cocotb.triggers import RisingEdge
from cocotb_bus.drivers import BusDriver


class NodeVCDriver(BusDriver):
    _signals = ["data_i", "vld_i"]

    _default_config = {
        "node_radix": 5,
        "flit_id_w": 2,
        "flit_data_w": 8
    }

    def __init__(self, entity, name, clock, node_id, config=None, log_lvl=INFO):
        self.entity = entity
        self.name = name
        self.clock = clock
        self.id = node_id
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
            for i in range(self.config["node_radix"]):
                self.bus.data_i[i].setimmediatevalue(0)
                self.bus.vld_i[i].setimmediatevalue(0)
            self.log.info(f"NodeVCDriver {self.id} created!")
        else:
            self.bus.data_i[self.id].setimmediatevalue(0)
            self.bus.vld_i[self.id].setimmediatevalue(0)
            self.log.info(f"NodeVCDriver {self.id} created!")

    async def send_packet(self, packet, input_id=None):
        assert len(packet) > 1, f"Packet is not long enough, needs to have 2 flit, this has only {len(packet)}"
        if input_id is None:
          raise ValueError("input ID has to be set")

        await RisingEdge(self.clock)
        for flit in packet:
            self.bus.vld_i[input_id].setimmediatevalue(1)
            self.bus.data_i[input_id].setimmediatevalue(flit)
            while True:
              await RisingEdge(self.clock)
              if (self.entity.in_chan_rdy_o[input_id].value == 1):
                  break
        self.bus.vld_i[input_id].setimmediatevalue(0)
        self.bus.data_i[input_id].setimmediatevalue(0)

    async def clear_input(self, sync: bool = True):
        if sync is True:
            await RisingEdge(self.clock)
        self.bus.data_i[self.id].setimmediatevalue(0)
        self.bus.vld_i[self.id].setimmediatevalue(0)
