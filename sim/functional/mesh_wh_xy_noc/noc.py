from utils.data_units import Packet, all_ones
from cocotb.triggers import RisingEdge, FallingEdge, ClockCycles, ReadOnly
from cocotb.result import TestSuccess, TestFailure
from logging import INFO, DEBUG
from cocotb.log import SimLog
import os
from collections import Counter
from driver import ChanDriver
from utils.data_units import Packet, all_ones
from utils.functions import *


class WHNoCTB:
  def __init__(self, dut, log_lvl=INFO):
    self.dut = dut
    self.dut._discover_all()
    self.log = SimLog("mesh_wh_xy_noc")
    self.log.setLevel(log_lvl)

    self.config = {
      "ps": int(os.environ["SYNTH"]),
      "node_radix": int(os.environ["NODE_RADIX"]),
      "flit_id_w": int(os.environ["FLIT_ID_W"]),
      "row_n": int(os.environ["ROW_N"]),
      "col_m": int(os.environ["COL_M"]),
      "channel_w": int(os.environ["CHANNEL_W"]),
      "node_buffer_depth_w": int(os.environ["NODE_BUFFER_DEPTH_W"])
    }

    assert self.dut.NODE_RADIX == self.config["node_radix"], "Bad Value"
    assert self.dut.NODE_BUFFER_DEPTH_W == self.config["node_buffer_depth_w"], "Bad Value"
    assert self.dut.FLIT_ID_W == self.config["flit_id_w"], "Bad Value"
    assert self.dut.ROW_N == self.config["row_n"], "Bad Value"
    assert self.dut.COL_M == self.config["col_m"], "Bad Value"
    assert self.dut.CHANNEL_W == self.config["channel_w"], "Bad Value"

    self.log.info(f"Created NocTB! {self.config}")
    self.drv = ChanDriver(dut, "in_chan", dut.clk_i, -1, self.config, log_lvl)

    self.packets_to_send = []
    self.packets_sent = []
    self.packets_received = []
    self.client_n = int(self.dut.ROW_N) * int(self.dut.COL_M)
    self.log.info(f"CLIENT N = {self.client_n}")

    self.max_lenght = 200

    self.last_warm_up_id = 0
    self.max_acc_traffic_ratio = 1
    self.acc_traffic_ratio = 0
    self.min_acc_traffic_ratio = 1
    self.capture_period = 0
    self.injection_ratio = 1

    self.packet = Packet( self.config["row_n"],
                          self.config["col_m"],
                          self.max_lenght,
                          self.config["channel_w"],
                          self.config["flit_id_w"])

    self.risedge = RisingEdge(self.dut.clk_i)
    self.rdonly = ReadOnly()

    for i in range(self.client_n):
      self.dut.in_chan_data_i[i].setimmediatevalue(0)
    self.dut.in_chan_vld_i.setimmediatevalue(0)
    self.dut.out_chan_rdy_i.setimmediatevalue(all_ones(self.client_n))
    self.dut.rst_ni.setimmediatevalue(1)

  def setup_dut(self, cycle_n, bp=False):
    cocotb.fork(self.reset_dut(self.dut.rst_ni, active_high=False, clk_cyc_n=cycle_n))
    readers = []
    for out_chan in range(self.client_n):
      readers.append(cocotb.fork(self.node_out_chan_reader(out_chan, cycle_n=cycle_n*2)))
    if bp:
      bp = []
      for i in range(self.client_n):
        bp.append(cocotb.fork(self.backpressure_gen(cycle_n=cycle_n*2)))

  async def node_out_chan_reader(self, i, cycle_n=10):
    await ClockCycles(self.dut.clk_i, cycle_n)
    packet = []
    while True:
      await self.risedge
      await self.rdonly
      if self.dut.out_chan_vld_o[i].value == 1:
        if self.dut.out_chan_data_o[i].value.binstr[0:2] == "10":  # header
          packet = []
        packet.append(int(self.dut.out_chan_data_o[i].value))
        if self.dut.out_chan_data_o[i].value.binstr[0:2] == "11":  # tail
          self.packets_received.append({"node": i, "packet": packet})

  async def backpressure_gen(self, cycle_n=10):
    await ClockCycles(self.dut.clk_i, cycle_n)
    while True:
      await self.risedge
      self.dut.out_chan_rdy_i <= getrandbits(self.client_n)

  async def reset_dut(self, rst_sig, active_high=True, clk_cyc_n=5):
    await ClockCycles(self.dut.clk_i, clk_cyc_n)
    if active_high:
      rst_sig <= 1
    else:
      rst_sig <= 0
    await ClockCycles(self.dut.clk_i, clk_cyc_n)
    if active_high:
      rst_sig <= 0
    else:
      rst_sig <= 1

  async def network_0load_wait(self, timeout=4000, cycle_step=500):
    self.log.info("...waiting...")
    cycles_spent = 0
    while True:
      empty_ques = True
      for i_id in range(self.client_n):
        if self.drv.que[i_id].__len__() != 0:
          empty_ques = False
          break
      if empty_ques:
        await ClockCycles(self.dut.clk_i, cycle_step)
        self.log.warning(f"{self.packets_received.__len__()}/{len(self.packets_to_send)}")
        cycles_spent += cycle_step
        if len(self.packets_to_send) == self.packets_received.__len__():
          break
        else:
          if cycles_spent == timeout:
            raise TimeoutError
      else:
        await ClockCycles(self.dut.clk_i, 100)

  def addr_to_id(self, addr, alg_route="xy"):
    if alg_route == "xy":
      row_id = addr[0]
      col_id = addr[1]
      return row_id * self.config["col_m"] + col_id
    else:
      self.log.error("This Topology is not yet supported")

  def id_to_addr(self, x_id, alg_route="xy"):
    if alg_route == "xy":
      row_id, col_id = divmod(x_id, self.config["col_m"])
      return [row_id, col_id]
    else:
      self.log.error("This Topology is not yet supported")

  async def compare(self, timeout=4000, cycle_step=500):
    await self.network_0load_wait(timeout=timeout, cycle_step=cycle_step)
    mismatches = 0
    sent = sorted(self.packets_to_send, key=lambda k: k['node'])
    received = sorted(self.packets_received, key=lambda k: k['node'])
    temp_sent = sent.copy()

    for pr_id, packet_r in enumerate(received):
      if packet_r not in temp_sent:
        mismatches += 1
      else:
        pre_len = len(temp_sent)
        self.log.debug(f"PRE POP len of temp_sent{len(temp_sent)}")
        self.log.debug(f"{packet_r} at {pr_id} matched! Removing temp_sent packet")
        temp_sent.remove(packet_r)
        post_len = len(temp_sent)
        self.log.debug(f"POST POP len of temp_sent{len(temp_sent)}")
        if pre_len != post_len + 1:
          self.log.error("Too many were removed !")
          raise TestFailure

    if mismatches > 0:
      self.log.error(f"Mismatches occured {mismatches}/{sent.__len__()} sent")
      for pr_id, packet_r in enumerate(received):
        if Counter(packet_r) != Counter(sent[pr_id]):
          self.log.info(f"{pr_id}. {packet_r} != {sent[pr_id]}")
      raise TestFailure
    else:
      self.log.info(f"All {sent.__len__()}/{received.__len__()} packets were sent and received properly")
      raise TestSuccess
