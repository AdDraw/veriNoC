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
from utils.noc_metrics import NoCMetrics
import numpy as np
from cocotb.utils import get_sim_steps, get_time_from_sim_steps, get_sim_time, _get_simulator_precision
import time
import json
from utils.address import NodeAddr
from utils.traffic_pattern import TrafficPattern
METRICS_FILENAME = str(os.environ["METRICS_FILENAME"])


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
    self.measurement_packets = []
    self.packets_to_time = []
    self.packets_sent = []
    self.packets_received = []
    self.client_n = int(self.dut.ROW_N) * int(self.dut.COL_M)
    self.log.info(f"CLIENT N = {self.client_n}")
    self.clk_period = int(os.environ["CLK_PERIOD"])
    self.max_lenght = 20
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

    self.dim = [self.config["row_n"], self.config["col_m"]]
    self.tp = TrafficPattern(self.dim)

    self.risedge = RisingEdge(self.dut.clk_i)
    self.rdonly = ReadOnly()

    for i in range(self.client_n):
      self.dut.in_chan_data_i[i].setimmediatevalue(0)
    self.dut.in_chan_vld_i.setimmediatevalue(0)
    self.dut.out_chan_rdy_i.setimmediatevalue(all_ones(self.client_n))
    self.dut.rst_ni.setimmediatevalue(1)

  def setup_dut(self, cycle_n, bp=False, reader_en=True):
    cocotb.fork(self.reset_dut(self.dut.rst_ni, active_high=False, clk_cyc_n=cycle_n))
    if reader_en:
      readers = []
      for out_chan in range(self.client_n):
        readers.append(cocotb.fork(self.node_out_chan_reader(out_chan, cycle_n=cycle_n*2)))
    if bp:
      bp = []
      for i in range(self.client_n):
        bp.append(cocotb.fork(self.backpressure_gen(cycle_n=cycle_n*2)))

  async def node_out_chan_reader(self, i, cycle_n=10, time=False):
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
          packet_rec = {"node": i, "packet": packet}
          if time:
            packet_rec["time_out"] = get_sim_time(units = "ns")
          self.packets_received.append(packet_rec)

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


  async def throughput(self, cycles, injection_ratio=0.1, plen=4):
    await ClockCycles(self.dut.clk_i, cycles)
    flow_arr_r = []
    count = 0

    flit_expected = cycles*self.client_n*injection_ratio
    packets_expected = flit_expected/plen
    packet_expected_true = len(self.measurement_packets)
    flit_expected_true = len(self.measurement_packets) * plen
    flit_max_possible = cycles*self.client_n
    packets_max_possible = cycles*self.client_n/plen
    # self.log.info(f" fe {flit_expected}, pe  {packets_expected}")
    # self.log.info(f"fet {flit_expected_true}, pet {packet_expected_true}")

    packets_throughput = []
    for packet_rec in self.packets_received:
      for packet_count in self.measurement_packets:
        if packet_count["packet"] == packet_rec["packet"]:
          packets_throughput.append(packet_rec)
          count += 1
          source = packet_count["node_src"]
          sink = packet_rec["node"]
          flow_arr_r.append([source, sink])
          break
    flow_arr_s = []
    for packet_sent in self.measurement_packets:
      source = packet_sent["node_src"]
      sink = packet_sent["node_dest"]
      flow_arr_s.append([source, sink])
    flow_arr_r_occ = {}
    flow_map = []
    for flow in flow_arr_r:
      if flow not in flow_map:
        flow_map.append(flow)
        flow_arr_r_occ.update({f"{flow}": flow_arr_r.count(flow)})
    flow_arr_s_occ = {}
    flow_map = []
    for flow in flow_arr_s:
      if flow not in flow_map:
        flow_map.append(flow)
        flow_arr_s_occ.update({f"{flow}": flow_arr_s.count(flow)})
    flow_acc_traffic = {}
    for flow in flow_arr_r_occ.keys():
      flow_acc_traffic.update({f"{flow}": flow_arr_r_occ[flow]/flow_arr_s_occ[flow]})
    accepted_traffic = []
    for flow in flow_acc_traffic.items():
      accepted_traffic.append(flow[1])
    avg_acc_traffic = np.asarray(accepted_traffic).mean()
    min_acc_traffic = np.asarray(accepted_traffic).min()
    max_acc_traffic = np.asarray(accepted_traffic).max()
    self.noc_metrics.accepted_traffic = avg_acc_traffic * injection_ratio
    self.noc_metrics.min_accepted_traffic = min_acc_traffic * injection_ratio
    self.noc_metrics.max_accepted_traffic = max_acc_traffic * injection_ratio
    flit_r = 0
    for packet in packets_throughput:
      flit_r += len(packet["packet"])
    flit_s = 0
    for packet in self.measurement_packets:
      flit_s += len(packet["packet"])

    # self.log.warning(f"packets to count should be {(cycles*self.client_n)/4}")
    # self.log.warning(f"throughput {count}/{len(self.measurement_packets)}")
    # self.log.warning(f"TR = {100*(flit_r/(self.client_n*cycles))}%, {flit_r}/{(self.client_n*cycles)}")
    # self.log.warning(f"TS = {100*(flit_s/(self.client_n*cycles))}%, {flit_s}/{(self.client_n*cycles)}")
    # self.log.warning(f"{(flit_r/flit_s)*100}%, {(flit_r/flit_s)*100*injection_ratio}")

  async def drain(self):
    while True:
      packet_times_rec = []
      for packet_rec in self.packets_received:
        for packet_sent in self.measurement_packets:
          if packet_rec["packet"] == packet_sent["packet"]:
            packet_times_rec.append({"got": packet_rec["time_out"],
                                     "sent": packet_sent["time_in"],
                                     "input_i": packet_sent["node_src"],
                                     "output_is": packet_sent["node_dest"],
                                     "output_ir": packet_rec["node"],
                                     "packet": packet_rec["packet"]
                                     }
                                     )
            break

      timed_packets = len(packet_times_rec)
      self.log.info(f"waiting for packets... {timed_packets}/{len(self.measurement_packets)}")
      if (timed_packets == len(self.measurement_packets)):
        latencies = []
        lat_sum = 0
        for packet in packet_times_rec:
          latency = packet["got"] - packet["sent"]
          if latency > self.noc_metrics.max_packet_latency:
            self.noc_metrics.max_packet_latency = latency
          if latency < self.noc_metrics.min_packet_latency:
            self.noc_metrics.min_packet_latency = latency
          latencies.append(latency)
          lat_sum += latency

        self.noc_metrics.avg_packet_latency = lat_sum/len(packet_times_rec)
        self.noc_metrics.print()

        self.json_dump(self.noc_metrics.json_gen(), METRICS_FILENAME)

        raise TestSuccess()
      else:
        await ClockCycles(self.dut.clk_i, 500)

  def json_dump(self, metrics: dict, filename) -> None:
    if os.path.exists(filename):
      # Update JSON in the file
      self.log.info(f"Updating JSON({filename}) with {metrics['name']}.")
      with open(filename, 'r') as outfile:
          old_metrics = json.load(outfile)
          old_metrics["testcases"].append(metrics)
      with open(filename, 'w') as outfile:
          json.dump(old_metrics, outfile)
    else:
      self.log.info(f"Creating JSON({filename}).")
      with open(filename, 'w') as outfile:
        # initialize JSON
        json_file = {"noc_type": "mesh_wh_noc_xy",
                     "date": f"{time.asctime()}"}
        json_file.update(self.config)
        json_file.update({"testcases": []})
        json_file["testcases"].append(metrics)
        json.dump(json_file, outfile)

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

  async def meas_phase(self, phase, period, packet_injection_rate, traffic_pattern, plen):

    assert phase in ["drain", "measurement", "warmup"], "PHASE IS INCORRECT"
    if phase == "drain":
      while True:
        for input_i in range(self.client_n):
          if bernouli(packet_injection_rate):
            if traffic_pattern == "u_rand":
              dest_node = self.tp.uniform_random(input_i)
            elif traffic_pattern == "complement":
              dest_node = self.tp.bit_permutation(input_i)
            elif traffic_pattern == "hotspot":
              dest_node = self.tp.hotspot(input_i)
            elif traffic_pattern == "nearest_neighbor":
              dest_node = self.tp.nearest_neighbor(input_i)
            elif traffic_pattern == "locality":
              dest_node = self.tp.locality(input_i)
            else:
              print("This traffic pattern is not supported")
              raise ValueError
            packet = self.packet.gen_packet(dest_node.addr, lenght=plen)
            x = self.drv.send_packet_from(input_i, packet)
        await RisingEdge(self.dut.clk_i)
    else:
      for i in range(period):
        for input_i in range(self.client_n):
          if bernouli(packet_injection_rate):
            if traffic_pattern == "u_rand":
              dest_node = self.tp.uniform_random(input_i)
            elif traffic_pattern == "complement":
              dest_node = self.tp.bit_permutation(input_i)
            elif traffic_pattern == "hotspot":
              dest_node = self.tp.hotspot(input_i)
            elif traffic_pattern == "nearest_neighbor":
              dest_node = self.tp.nearest_neighbor(input_i)
            elif traffic_pattern == "locality":
              dest_node = self.tp.locality(input_i)
            else:
              print("This traffic pattern is not supported")
              raise ValueError
            packet = self.packet.gen_packet(dest_node.addr, lenght=plen)
            x = self.drv.send_packet_from(input_i, packet)
            self.packets_to_send.append({"node": dest_node.id, "packet": x["packet"] })
            if phase == "measurement":
                self.measurement_packets.append({"node_src": input_i, "node_dest": dest_node.id, "packet": x["packet"], "time_in": x["time"]})

        await RisingEdge(self.dut.clk_i)
