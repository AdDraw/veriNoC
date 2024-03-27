import os
from collections import Counter
from logging import DEBUG, INFO
from random import getrandbits, randint

import cocotb
from cocotb.log import SimLog
from cocotb.regression import TestFactory
from cocotb.result import TestFailure, TestSuccess
from cocotb.triggers import ClockCycles, Combine, ReadOnly, RisingEdge
from driver import NodeVCDriver
from utils.functions import *

CLOCK_PERIOD_NS = int(os.environ["CLK_PERIOD"])


class WormholeNodeTB:
  def __init__(self, dut, log_lvl=INFO):
    self.dut = dut
    self.log = SimLog("worm_node_tb")
    self.log.setLevel(log_lvl)

    self.config = {
      "node_radix": int(os.environ["NODE_RADIX"]),
      "flit_id_w": int(os.environ["FLIT_ID_W"]),
      "flit_data_w": int(os.environ["FLIT_DATA_W"]),
      "row_cord":int(os.environ["ROW_CORD"]),
      "row_addr_w":int(os.environ["ROW_ADDR_W"]),
      "col_cord":int(os.environ["COL_CORD"]),
      "col_addr_w":int(os.environ["COL_ADDR_W"]),
      "buffer_depth_w":int(os.environ["BUFFER_DEPTH_W"]),
      "flit_w": int(os.environ["FLIT_ID_W"]) + int(os.environ["FLIT_DATA_W"])
    }

    assert self.dut.NODE_RADIX == self.config["node_radix"], "Bad Value"
    assert self.dut.FLIT_ID_W == self.config["flit_id_w"], "Bad Value"
    assert self.dut.FLIT_DATA_W == self.config["flit_data_w"], "Bad Value"
    assert self.dut.ROW_CORD == self.config["row_cord"], "Bad Value"
    assert self.dut.ROW_ADDR_W == self.config["row_addr_w"], "Bad Value"
    assert self.dut.COL_CORD == self.config["col_cord"], "Bad Value"
    assert self.dut.COL_ADDR_W == self.config["col_addr_w"], "Bad Value"
    assert self.dut.BUFFER_DEPTH_W == self.config["buffer_depth_w"], "Bad Value"

    self.drv = NodeVCDriver(dut, "in_chan", dut.clk_i, -1, self.config, log_lvl)

    self.packets_to_send = []
    self.packets_received = []
    self.dut.out_chan_rdy_i.setimmediatevalue(0x1F)
    self.dut.rst_ni.setimmediatevalue(1)

  def setup_dut(self, cycle_n, bp=False):
    cocotb.start_soon(self.reset_dut(self.dut.rst_ni, active_high=False, clk_cyc_n=cycle_n))
    readers = []
    for out_chan in range(self.config["node_radix"]):
      readers.append(cocotb.start_soon(self.node_out_chan_reader(out_chan, cycle_n=cycle_n*2)))
    if bp:
      bp = []
      for i in range(self.config["node_radix"]):
        bp.append(cocotb.start_soon(self.backpressure_gen(cycle_n=cycle_n*2)))

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

  async def node_out_chan_reader(self, i, cycle_n=10):
    risedge = RisingEdge(self.dut.clk_i)
    rdonly = ReadOnly()

    await ClockCycles(self.dut.clk_i, cycle_n)

    packet = []
    while True:
      await risedge
      await rdonly
      if self.dut.out_chan_vld_o[i].value == 1:
        if self.dut.out_chan_data_o[i].value.binstr[0:2] == "10":  # header
          packet = []
        packet.append(int(self.dut.out_chan_data_o[i].value))
        if self.dut.out_chan_data_o[i].value.binstr[0:2] == "11":  # tail
          self.packets_received.append({"out_chan": i, "packet": packet})

  async def backpressure_gen(self, cycle_n=10):
    risedge = RisingEdge(self.dut.clk_i)
    await ClockCycles(self.dut.clk_i, cycle_n)
    while True:
      await risedge
      self.dut.out_chan_rdy_i <= getrandbits(self.config["node_radix"])

  def compare(self):
    mismatches = 0
    received = sorted(self.packets_received, key=lambda k: k['out_chan'])
    sent = sorted(self.packets_to_send, key=lambda k: k['out_chan'])
    temp_sent = sent.copy()

    if received.__len__() != sent.__len__():
      self.log.error(f"Not enough packets were received {received.__len__()} vs {sent.__len__()} sent")
      raise TestFailure

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
      self.log.info(f"All {sent.__len__()} packets were sent and received properly")
      raise TestSuccess


async def simple_test(dut, log_lvl=INFO, bp=False):
  tb = WormholeNodeTB(dut, log_lvl)
  tb.setup_dut(cycle_n=5, bp=bp)
  await ClockCycles(dut.clk_i, 10)
  for i in range(tb.config["node_radix"]):
    for j in range(tb.config["node_radix"]):
      await test_input(tb, i, j)
    await ClockCycles(dut.clk_i, 10)
  await ClockCycles(dut.clk_i, 1000)
  tb.compare()
  raise TestSuccess("Sim finished sucessfully")


async def competetive_test(dut, log_lvl=INFO, bp=False):
  tb = WormholeNodeTB(dut, log_lvl)
  tb.setup_dut(cycle_n=5, bp=bp)
  await ClockCycles(dut.clk_i, 10)
  for j in range(tb.config["node_radix"]):
    waiters = []
    for i in range(tb.config["node_radix"]):
      waiters.append(cocotb.start_soon(test_input(tb, i, j)))
    await ClockCycles(dut.clk_i, 10)
    await Combine(*waiters)
  await ClockCycles(dut.clk_i, 1000)
  tb.compare()
  raise TestSuccess("Sim finished sucessfully")


async def multi_output_no_compete(dut, log_lvl=INFO, bp=False):
  tb = WormholeNodeTB(dut, log_lvl)
  tb.setup_dut(cycle_n=5, bp=bp)
  await ClockCycles(dut.clk_i, 10)
  waiters = []
  for i in range(tb.config["node_radix"]):
    waiters.append(cocotb.start_soon(test_input(tb, i, i)))
  await Combine(*waiters)
  await ClockCycles(dut.clk_i, 1000)
  tb.compare()
  raise TestSuccess("Sim finished sucessfully")


async def multi_output_compete(dut, log_lvl=INFO, bp=False):
  tb = WormholeNodeTB(dut, log_lvl)
  tb.setup_dut(cycle_n=5, bp=bp)
  await ClockCycles(dut.clk_i, 10)

  for j in range(tb.config["node_radix"]):
    for num in range(tb.config["node_radix"]):
      if num != 0:
        waiters = []
        for i in range(tb.config["node_radix"]):
          if i % num == 0:
            waiters.append(cocotb.start_soon(test_input(tb, i, i)))
          else:
            waiters.append(cocotb.start_soon(test_input(tb, i, j)))
        await Combine(*waiters)
        await ClockCycles(dut.clk_i, 10)
    await ClockCycles(dut.clk_i, 10)
  await ClockCycles(dut.clk_i, 1000)
  tb.compare()
  raise TestSuccess("Sim finished sucessfully")


async def random_single_input_at_a_time(dut, log_lvl=INFO, packet_n=30, packet_length=4, bp=False):
  tb = WormholeNodeTB(dut, log_lvl)
  tb.setup_dut(cycle_n=5, bp=bp)
  await ClockCycles(dut.clk_i, 10)
  populate_packets_to_send(tb, packet_n=packet_n, packet_length=packet_length)

  for packet in tb.packets_to_send:
    driver_id = randint(0, tb.config["node_radix"]-1)
    await tb.drv.send_packet(packet["packet"], driver_id)
  await ClockCycles(dut.clk_i, 1000)
  tb.compare()
  raise TestSuccess("Sim finished sucessfully")


async def random_multi_input_at_a_time(dut, log_lvl=INFO, packet_n=30, packet_length=4, bp=False):
  tb = WormholeNodeTB(dut, log_lvl)
  tb.setup_dut(cycle_n=5)
  await ClockCycles(dut.clk_i, 10)

  in_n = tb.config["node_radix"]
  populate_packets_to_send(tb, packet_n=packet_n*in_n, packet_length=packet_length)

  pckt_size = int(len(tb.packets_to_send)/in_n)
  pckts = tb.packets_to_send

  if bp:
    bp = []
    for i in range(tb.config["node_radix"]):
      bp.append(cocotb.start_soon(tb.backpressure_gen(i)))

  for packet in range(pckt_size):
    waiters = []
    for i in range(tb.config["node_radix"]):
      waiters.append(cocotb.start_soon(tb.drv.send_packet(pckts[(packet*in_n)+i]["packet"], i)))
    await Combine(*waiters)
  await ClockCycles(dut.clk_i, 1000)
  tb.compare()
  raise TestSuccess("Sim finished sucessfully")


tf = TestFactory(simple_test)
tf.add_option("bp", [False, True])
tf.generate_tests()

tf = TestFactory(competetive_test)
tf.add_option("bp", [False, True])
tf.generate_tests()

tf = TestFactory(multi_output_compete)
tf.add_option("bp", [False, True])
tf.generate_tests()

tf = TestFactory(multi_output_no_compete)
tf.add_option("bp", [False, True])
tf.generate_tests()

tf = TestFactory(random_single_input_at_a_time)
tf.add_option("bp", [False, True])
tf.add_option("packet_n", [10, 100, 200])
tf.add_option("packet_length", [2, 4, 8])
tf.generate_tests()

tf = TestFactory(random_multi_input_at_a_time)
tf.add_option("bp", [False, True])
tf.add_option("packet_n", [10, 100, 200])
tf.add_option("packet_length", [2, 4, 8])
tf.generate_tests()
