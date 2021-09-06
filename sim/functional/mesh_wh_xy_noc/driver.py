from cocotb_bus.drivers import BusDriver
from cocotb.triggers import RisingEdge, ReadOnly, FallingEdge
from logging import INFO, DEBUG
from cocotb.utils import get_sim_steps, get_time_from_sim_steps, get_sim_time, _get_simulator_precision
from cocotb import fork

class ChanDriver(BusDriver):
  _signals = ["data_i", "vld_i"]

  def __init__(self, entity, name, clock, node_id, config=None, log_lvl=INFO):
    self.entity = entity
    self.name = name
    self.clock = clock
    self.id = node_id
    self.config = config
    self.row_n = self.config["row_n"]
    self.col_m = self.config["col_m"]
    self.client_n = self.row_n * self.col_m
    self.que = self.client_n * [ [] ]

    BusDriver.__init__(self, entity, name, clock)
    if log_lvl == DEBUG:
        self.log.setLevel(DEBUG)
    else:
        self.log.setLevel(INFO)
    if self.id == -1:
        for i in range(self.client_n):
            self.bus.data_i[i].setimmediatevalue(0)
            self.bus.vld_i[i].setimmediatevalue(0)
        self.log.info(f"NodeVCDriver {self.id} created!")
    else:
        self.bus.data_i[self.id].setimmediatevalue(0)
        self.bus.vld_i[self.id].setimmediatevalue(0)
        self.log.info(f"NodeVCDriver {self.id} created!")
    for i in range(self.client_n):
      fork(self.input_que(i))

  def send_packet_from(self, input_id, packet):
    assert 0 <= input_id < self.client_n, "Input ID is too big"
    assert len(packet) > 1, f"Packet is not long enough, needs to have 2 flit, this has only {len(packet)}"
    self.que[input_id].append(packet)
    time = get_sim_time(units = "ns")
    return {"source": input_id,
            "time": time,
            "packet": packet}

  async def input_que(self, in_n):
    while True:
      if len(self.que[in_n]) != 0:
        if self.que[in_n][0] is None:
          self.que[in_n].pop(0)
        packet = self.que[in_n][0]
        self.que[in_n].pop(0)
        i = 0
        while i != len(packet):
          await RisingEdge(self.clock)
          await ReadOnly()
          if self.entity.in_chan_rdy_o[in_n].value == 1:
            await FallingEdge(self.clock)
            self.bus.vld_i[in_n] <= 1
            self.bus.data_i[in_n] <= packet[i]
            i += 1
          else:
            await FallingEdge(self.clock)
            self.bus.vld_i[in_n] <= 0
            self.bus.data_i[in_n] <= 0
        await FallingEdge(self.clock)
        self.bus.vld_i[in_n] <= 0
        self.bus.data_i[in_n] <= 0
      else:
        await RisingEdge(self.clock)
        self.bus.vld_i[in_n] <= 0
        self.bus.data_i[in_n] <= 0

  async def clear_input(self, sync: bool = True):
      if sync is True:
          await RisingEdge(self.clock)
      self.bus.data_i[self.id].setimmediatevalue(0)
      self.bus.vld_i[self.id].setimmediatevalue(0)
