# COCOTB imports
import time

import cocotb
from cocotb.result import TestSuccess, TestFailure
from cocotb.triggers import ClockCycles, RisingEdge
from logging import INFO, DEBUG
from cocotb.log import SimLog
from cocotb.regression import TestFactory
from cocotb.binary import BinaryValue
# Global Imports
import os
from random import sample, randint, random
from math import log, ceil
import math
import numpy as np
import json

from utils.functions import *
import utils.bit_permutation as bit_p
import utils.digit_permutation as digit_p
from utils.Resource import Resource

CLK_PERIOD = int(os.environ["CLK_PERIOD"])
METRICS_FILENAME = str(os.environ["METRICS_FILENAME"])


class NocTB:
    """
        TB suite for a MESH NOC with XY Routing
        inputs are to be driven from RESOURCES DRIVERS
        outputs should be checked by the RESOURCE MONITORS

        1)  check if everything correctly landed into the correct DESTINATION
            dst is defined by X_ADDR & Y_ADDR and those need to be equal to X_CORD & Y_CORD
            of the RESOURCE

        Mesh NoC has:
        - N Rows of switches
        - M Columns of switches
        - Each switch is connected to min 2 neighboring switches
        - XY routing

        Data from within the resource comes at the lowest priority.
    """

    def __init__(self, dut, log_lvl=INFO):
        self.dut = dut
        self.dut._discover_all()

        self.log = SimLog("noctb")
        self.log.setLevel(log_lvl)

        self.config = {
            "ps": int(os.environ["SYNTH"]),
            "row_n": int(os.environ["ROW_N"]),
            "col_m": int(os.environ["COL_M"]),
            "pckt_data_w": int(os.environ["PCKT_DATA_W"]),
            "fifo_depth_w": int(os.environ["FIFO_DEPTH_W"]),
            "col_addr_w": ceil(log(int(os.environ["COL_M"]), 2)),
            "row_addr_w": ceil(log(int(os.environ["ROW_N"]), 2)),
            "clk_period": int(os.environ["CLK_PERIOD"])
        }

        self.log.info(f"Created NocTB! {self.config}")

        self.sent = []
        self.rsc_list = []
        self.last_warm_up_id = 0
        self.resource_n = self.config["row_n"] * self.config["col_m"]
        self.clk_period = self.config["clk_period"]
        self.max_acc_traffic_ratio = 1
        self.acc_traffic_ratio = 0
        self.min_acc_traffic_ratio = 1
        self.capture_period = 1000
        self.injection_ratio = 1

        self.received = []
        self.received_separate = []

        for row_id in range(self.config["row_n"]):
            for col_id in range(self.config["col_m"]):
                self.config_rsc = {
                    "row_n": int(os.environ["ROW_N"]),
                    "col_m": int(os.environ["COL_M"]),
                    "pckt_data_w": int(os.environ["PCKT_DATA_W"]),
                    "fifo_depth_w": int(os.environ["FIFO_DEPTH_W"]),
                    "packet_col_addr_w": ceil(log(int(os.environ["COL_M"]), 2)),
                    "packet_row_addr_w": ceil(log(int(os.environ["ROW_N"]), 2)),
                    "packet_w": ceil(log(int(os.environ["COL_M"]), 2)) + ceil(log(int(os.environ["ROW_N"]), 2)) + int(
                        os.environ["PCKT_DATA_W"]),
                    "col_cord": col_id,
                    "row_cord": row_id
                }

                self.rsc_list.append(Resource(dut, "", dut.clk_i, self.config_rsc, callback=self.mon_callback))
                self.received_separate.append([])

    def mon_callback(self, t):
        self.received.append(t)
        self.received_separate[t["sink"]].append(t)

    async def setup_dut(self):
        await self.reset_hdl()
        for rsc in self.rsc_list:
            await rsc.clear_rsc_output(sync=False)
        await ClockCycles(self.dut.clk_i, 2)

    async def reset_hdl(self, cycle_n=5):
        self.dut.rst_ni <= 0
        await ClockCycles(self.dut.clk_i, cycle_n)
        self.dut.rst_ni <= 1
        await ClockCycles(self.dut.clk_i, cycle_n)

    async def network_0load_wait(self, timeout=4000, cycle_step=500):
        self.log.info("...waiting...")
        cycles_spent = 0
        while True:
            empty_ques = True
            for rsc in self.rsc_list:
                if rsc.que.__len__() != 0:
                    empty_ques = False
            if empty_ques:
                await ClockCycles(self.dut.clk_i, cycle_step)
                packets_sent = 0
                for rsc in self.rsc_list:
                    packets_sent += rsc.sent_packets.__len__()
                self.log.info(f"{self.received.__len__()}/{packets_sent}")
                cycles_spent += cycle_step
                if packets_sent == self.received.__len__():
                    break
                else:
                    if cycles_spent == timeout:
                        raise TimeoutError
            else:
                await RisingEdge(self.dut.clk_i)

    async def warm_up(self, warm_up_period=1000, injection_rate=0.5):
        j = 1
        for i in range(warm_up_period):
            for rsc in self.rsc_list:
                if bernouli(injection_rate):
                    row = randint(0, self.config["row_n"] - 1)
                    col = randint(0, self.config["col_m"] - 1)
                    self.last_warm_up_id = j
                    rsc.send_packet_to_xy(i, row, col)
                    j += 1
            await RisingEdge(self.dut.clk_i)

    async def throughput(self, capture_period, injection_ratio):
        # Wait for capture_period
        # Calculate received/sent ratio
        for i in range(capture_period):
            await RisingEdge(self.dut.clk_i)

        self.aggregate_packets(do_print=False)
        sent_tmp = self.sent.copy()
        rec_tmp = self.received.copy()
        sent_sorted = sorted(sent_tmp, key=lambda k: k['data'])
        rec_sorted = sorted(rec_tmp, key=lambda k: k['data'])

        flow_arr_r = []
        for rec_pckt in rec_sorted:
            for sent_pckt in sent_sorted:
                if rec_pckt['data'] == sent_pckt['data']:
                    source = sent_pckt['source']
                    sink = rec_pckt['sink']
                    flow_arr_r.append([source, sink])
                    break
            else:
                print(f"{rec_pckt['data']} not found!")

        flow_arr_s = []
        for packet_sent in sent_sorted:
            source = packet_sent['source']
            sink = packet_sent['sink']
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

        self.capture_period = capture_period
        self.injection_ratio = injection_ratio
        self.acc_traffic_ratio = avg_acc_traffic * injection_ratio
        self.min_acc_traffic_ratio = min_acc_traffic * injection_ratio
        self.max_acc_traffic_ratio = max_acc_traffic * injection_ratio

        self.log.info(f"min_TRAFFIC {min_acc_traffic * injection_ratio} vs {injection_ratio}")
        self.log.info(f"AVG_TRAFFIC {avg_acc_traffic * injection_ratio} vs {injection_ratio}")
        self.log.info(f"max_TRAFFIC {max_acc_traffic * injection_ratio} vs {injection_ratio}")

    def network_stats(self, received_pckts, sent_pckts):
        total_time = 0
        total_hops = 0
        min_time = pow(2, 20)
        max_time = -1
        shortest_path = pow(2, 20)
        longest_path = -1

        received_tmp = received_pckts.copy()
        sent_and_received = []
        for sent_pckt in sent_pckts:
            s_col_dest = sent_pckt["col_dest"]
            s_row_dest = sent_pckt["row_dest"]
            s_data = sent_pckt["data"]
            s_time = sent_pckt["time"]
            checked = 0
            if s_data >= self.last_warm_up_id:
                for rp_idx, rec_pckt in enumerate(received_tmp):
                    r_col_dest = rec_pckt["col_dest"]
                    r_row_dest = rec_pckt["row_dest"]
                    r_data = rec_pckt["data"]
                    r_time = rec_pckt["time"]
                    if s_col_dest == r_col_dest and s_row_dest == r_row_dest and s_data == r_data:
                        received_tmp.pop(rp_idx)
                        time_diff = r_time - s_time

                        assert time_diff > 0, "badval"

                        s_row_cord, s_col_cord = divmod(sent_pckt["source"], self.config["col_m"])
                        r_row_cord, r_col_cord = divmod(rec_pckt["sink"], self.config["col_m"])
                        sent_and_received.append({"from": [sent_pckt["source"], s_row_cord, s_col_cord],
                                                  "to": [rec_pckt["sink"], r_row_cord, r_col_cord],
                                                  "time": time_diff})
                        if s_row_cord > r_row_cord:
                            vert_hops = s_row_cord - r_row_cord
                        else:
                            vert_hops = r_row_cord - s_row_cord
                        if s_col_cord > r_col_cord:
                            hor_hops = s_col_cord - r_col_cord
                        else:
                            hor_hops = r_col_cord - s_col_cord
                        hops_req = 1 + hor_hops + vert_hops
                        if hops_req < shortest_path:
                            shortest_path = hops_req
                        if hops_req > longest_path:
                            longest_path = hops_req
                        self.log.debug(sent_and_received[-1])
                        if time_diff < min_time:
                            min_time = time_diff
                        if time_diff > max_time:
                            max_time = time_diff

                        total_time += time_diff
                        total_hops += hops_req
                        checked = 1
                        break
                if not checked:
                    raise TestFailure(f"sent_packet not received {sent_pckt}")

        avg_packet_latency = total_time / sent_and_received.__len__()
        stats = {
            "sr_len": sent_and_received.__len__(),
            "avg_latency_ns": avg_packet_latency,
            "avg_latency_cyc": avg_packet_latency / self.clk_period,
            "min_latency": min_time,
            "max_latency": max_time,
            "total_time": total_time,
            "total_hops": total_hops,
            "avg_time_per_hop": total_time / total_hops,
            "avg_cyc_per_hop": (total_time / total_hops) / self.clk_period,
            "max_path": longest_path,
            "min_path": shortest_path,
            "avg_path": total_hops / len(sent_pckts)
        }
        return stats

    def aggregate_packets(self, do_print=True):
        self.sent = []

        for rsc in self.rsc_list:
            for sent_pckt in rsc.sent_packets:
                self.sent.append(sent_pckt)

        if do_print:
            for rsc in self.rsc_list:
                self.log.info(f"RSC {rsc.id} sent  {rsc.sent_packets.__len__()} /"
                              f" {rsc.sent_packets.__len__() / self.sent.__len__() * 100} | "
                              f"rec {rsc.received_pckts.__len__()/self.received.__len__() * 100}")

    async def compare(self, testcase_name, add_to_json=True):
        self.log.info(f"START COMPARISON")
        await self.network_0load_wait()
        self.log.info("------------------------------------------------------------------------- Final!")

        self.aggregate_packets()

        packets_sent = self.sent.__len__() #- (self.last_warm_up_id+1)
        packets_received = self.received.__len__() #- (self.last_warm_up_id+1)

        if packets_received != packets_sent:
            raise TestFailure(f"Numbers of packets sent and received in the whole NOC is not the same "
                              f"rec: {packets_received} != sent: {packets_sent}")
        else:
            self.log.debug(f"Number of received packets matches the sent packet count rec/sent: "
                           f"{packets_received}/{packets_sent}")

            stats = self.network_stats(self.received, self.sent)

            # check correctness (and what was sent and received)
            if stats["sr_len"] == packets_sent:
                self.log.debug(f"All sent packets were properly received "
                               f"{stats['sr_len']}/{packets_sent}")

                self.log.debug("1. LifeTime:")
                self.log.info(f"   - Average packet lifetime: {stats['avg_latency_ns']:.2f} ns")
                self.log.info(f"   - Average packet lifetime: {stats['avg_latency_cyc']:.2f} cycles "
                               f"(CLK_PERIOD = {self.clk_period} ns)")

                self.log.info(f"   - Min packet lifetime    : {stats['min_latency']} ns")
                self.log.info(f"   - Max packet lifetime    : {stats['max_latency']} ns")

                self.log.debug("2. Hops:")
                self.log.debug(f"   - Total Hops             : {stats['total_time']} "
                               f"(with included hops from Resource to Switch)")
                self.log.debug(f"   - Average Time per Hop   : {stats['avg_time_per_hop']:.2f} ns"
                               f"| {stats['avg_cyc_per_hop']:.2f} cyc")
                self.log.debug(f"   - Longest packet path    : {stats['max_path']} hops")
                self.log.debug(f"   - Shortest packet path   : {stats['min_path']} hops")
                self.log.debug(f"   - Average packet path    : {stats['avg_path']:.2f} hops")

                if add_to_json:
                    self.log.debug("Dumping Metrics")
                    metrics = {f"name": testcase_name,
                               "packets_sent": packets_sent,
                               "packets_received": packets_received,
                               "avg_packet_latency_ns": stats['avg_latency_ns'],
                               "avg_packet_latency_cyc": stats['avg_latency_cyc'],
                               "min_packet_latency_ns": stats['min_latency'],
                               "max_packet_latency_ns": stats['max_latency'],
                               "total_hops": stats['total_hops'],
                               "avg_time_per_hop": stats['avg_time_per_hop'],
                               "avg_cyc_per_hop": stats['avg_cyc_per_hop'],
                               "min_hop_path": stats['min_path'],
                               "max_hop_path": stats['max_path'],
                               "avg_hop_path": stats['avg_path'],
                               "accepted_traffic": self.acc_traffic_ratio,
                               "min_accepted_traffic": self.min_acc_traffic_ratio,
                               "max_accepted_traffic": self.max_acc_traffic_ratio,
                               "offered_traffic": self.injection_ratio,
                               "capture_period": self.capture_period
                               }

                    self.json_dump(metrics, METRICS_FILENAME)
                raise TestSuccess()
            else:
                self.log.error(f"Szto? {stats['sr_len']}/{packets_sent}, {self.last_warm_up_id}")

    def json_dump(self, metrics: dict, filename) -> None:
        if os.path.exists(filename):
            # Update JSON in the file
            with open(filename, 'r') as outfile:
                old_metrics = json.load(outfile)
                old_metrics["testcases"].append(metrics)
            with open(filename, 'w') as outfile:
                json.dump(old_metrics, outfile)
        else:
            with open(filename, 'w') as outfile:
                # initialize JSON
                json_file = {"noc_type": "mesh_noc_xy",
                             "date": f"{time.asctime()}"}
                json_file.update(self.config)
                json_file.update({"testcases": []})
                json_file["testcases"].append(metrics)
                json.dump(json_file, outfile)


@cocotb.test(skip=False)
async def smoke(dut, log_lvl=INFO, injection_rate=0.1):
    log = SimLog("smoke")
    log.setLevel(log_lvl)

    tb = NocTB(dut, log_lvl)
    await tb.setup_dut()

    # loop that goes over every reasource !
    if pow(tb.rsc_list.__len__(), 2) > pow(2, tb.config["pckt_data_w"]):
        raise ValueError("Packet Data Width is not big enough to provide unique ID to each packet")
    pid = list(range(pow(2, tb.config["pckt_data_w"])))
    for sending_rsc in tb.rsc_list:
        sources = tb.rsc_list.copy()
        sources.pop(sending_rsc.id)
        for rec_rsc in sources:
            sending_rsc.send_packet_to_xy(pid[0], rec_rsc.config["row_cord"], rec_rsc.config["col_cord"])
            pid.pop(0)
            await ClockCycles(dut.clk_i, 5)
    await ClockCycles(dut.clk_i, 100)
    pid = list(range(pow(2, tb.config["pckt_data_w"])))
    for sending_rsc in tb.rsc_list:
        sources = tb.rsc_list.copy()
        sources.pop(sending_rsc.id)
        for rec_rsc in sources:
            sending_rsc.send_packet_to_xy(pid[0], rec_rsc.config["row_cord"], rec_rsc.config["col_cord"])
            pid.pop(0)
            await ClockCycles(dut.clk_i, 10)
    await tb.compare("smoke", add_to_json=False)


async def uniform_random(dut, log_lvl=INFO, injection_rate=0.1, capture_period=2000, warm_up_period=500):
    log = SimLog("uniform_random")
    log.setLevel(log_lvl)
    tb = NocTB(dut, log_lvl)
    await tb.setup_dut()
    assert (int(len(tb.rsc_list)*injection_rate*capture_period)) < pow(2, tb.config["pckt_data_w"]),\
        "Pckt Data Width is not big enough to provide unique ID to each packet"

    throughput = cocotb.fork(tb.throughput(capture_period, injection_rate))

    pid = list(range(tb.last_warm_up_id, pow(2, tb.config["pckt_data_w"])))
    i = 0
    while i < capture_period:
        for sender in tb.rsc_list:
            if bernouli(injection_rate):
                row = randint(0, tb.config["row_n"] - 1)
                col = randint(0, tb.config["col_m"] - 1)
                while row == sender.config["row_cord"] and col == sender.config["col_cord"]:
                    row = randint(0, tb.config["row_n"] - 1)
                    col = randint(0, tb.config["col_m"] - 1)
                sender.send_packet_to_xy(pid[0], row, col)
                pid.pop(0)

        await RisingEdge(dut.clk_i)
        i += 1

    await throughput
    await tb.compare(f"u_rand_{injection_rate}")


async def bit_permutation(dut, log_lvl=INFO, permutation="complement", injection_rate=0.1, capture_period=2000):
    # Different Types of bit permutation traffic
    log = SimLog("bit_permutation")
    log.setLevel(log_lvl)
    tb = NocTB(dut, log_lvl)
    await tb.setup_dut()

    # Destination node is calculated from the coordinates of the source node
    assert (len(tb.rsc_list)*injection_rate*capture_period + 1000) < pow(2, tb.config["pckt_data_w"]), "Pckt Data Width is not big enough to provide unique ID to each packet"

    throughput = cocotb.fork(tb.throughput(capture_period, injection_rate))
    pid = sample(range(pow(2, tb.config["pckt_data_w"])), int(len(tb.rsc_list)*injection_rate*capture_period + 1000))
    i = 0
    while i < capture_period:
        for sender in tb.rsc_list:
            if bernouli(injection_rate):
                row_cord = BinaryValue(sender.config["row_cord"], ceil(math.log(int(os.environ["ROW_N"]), 2)), bigEndian=False).binstr
                col_cord = BinaryValue(sender.config["col_cord"], ceil(math.log(int(os.environ["COL_M"]), 2)), bigEndian=False).binstr

                if permutation == "complement":
                    dest = bit_p.invert(row_cord + col_cord)
                elif permutation == "shuffle":
                    dest = bit_p.shuffle(row_cord + col_cord)
                elif permutation == "reverse":
                    dest = bit_p.reverse(row_cord + col_cord)
                elif permutation == "rotate":
                    dest = bit_p.rotate(row_cord + col_cord)
                else:
                    raise ValueError(f"ERROR: Incorrect Bit permutation function '{permutation}'")

                row_dest = BinaryValue(dest[0:tb.config["row_addr_w"]], ceil(math.log(int(os.environ["ROW_N"]), 2)),
                                       bigEndian=False).value
                col_dest = BinaryValue(dest[tb.config["row_addr_w"]::], ceil(math.log(int(os.environ["COL_M"]), 2)),
                                       bigEndian=False).value

                if row_dest >= tb.config["row_n"]:
                    row_dest = tb.config["row_n"] - 1
                if col_dest >= tb.config["col_m"]:
                    col_dest = tb.config["col_m"] - 1

                sender.send_packet_to_xy(pid[0], row_dest, col_dest)
                pid.pop(0)
        await RisingEdge(dut.clk_i)
        i += 1
    await throughput
    await tb.compare(f"bp_{permutation[0:3]}_{injection_rate}")


async def digit_permutation(dut, log_lvl=INFO, permutation="neighbour", injection_rate=0.1, capture_period=2000):
    # Different Types of bit permutation traffic
    log = SimLog("digit_permutation")
    log.setLevel(log_lvl)
    tb = NocTB(dut, log_lvl)
    await tb.setup_dut()

    # Destination node is calculated from the coordinates of the source node
    assert (len(tb.rsc_list)*injection_rate*capture_period + 1000) < pow(2, tb.config["pckt_data_w"]),\
            "Pckt Data Width is not big enough to provide unique ID to each packet"

    throughput = cocotb.fork(tb.throughput(capture_period, injection_rate))
    pid = sample(range(pow(2, tb.config["pckt_data_w"])), int(len(tb.rsc_list)*injection_rate*capture_period + 1000))
    i = 0
    while i < capture_period:
        for sender in tb.rsc_list:
            if bernouli(injection_rate):
                row_cord = BinaryValue(sender.config["row_cord"], tb.config["row_addr_w"], bigEndian=False).value
                col_cord = BinaryValue(sender.config["col_cord"], tb.config["col_addr_w"], bigEndian=False).value

                if permutation == "neighbour":
                    row_dest = digit_p.neighbour(row_cord, tb.config["row_n"])
                    col_dest = digit_p.neighbour(col_cord, tb.config["col_m"])
                elif permutation == "tornado":
                    row_dest = digit_p.tornado(row_cord, tb.config["row_n"])
                    col_dest = digit_p.tornado(col_cord, tb.config["col_m"])
                else:
                    raise ValueError(f"ERROR: Incorrect Digit permutation function '{permutation}'")

                sender.send_packet_to_xy(pid[0], row_dest, col_dest)

                pid.pop(0)
        await RisingEdge(dut.clk_i)
        i += 1

    await throughput
    await tb.compare(f"dp_{permutation[0:3]}_{injection_rate}")

if int(os.environ["TESTFACTORY"]) == 1:
    tf = TestFactory(uniform_random)
    tf.add_option("injection_rate", [0.05, 0.075, 0.1, 0.125, 0.15, 0.175, 0.2, 0.225, 0.25, 0.275, 0.3, 0.325, 0.35])
    tf.generate_tests()

    tf = TestFactory(bit_permutation)
    tf.add_option("injection_rate", [0.05, 0.075, 0.1, 0.125, 0.15, 0.175, 0.2, 0.225, 0.25, 0.275, 0.3, 0.325, 0.35])
    tf.add_option("permutation", ["complement"])
    tf.generate_tests()

    # tf = TestFactory(digit_permutation)
    # tf.add_option("injection_rate", [0.05, 0.075, 0.1, 0.125, 0.15, 0.175, 0.2, 0.225, 0.25, 0.275, 0.3, 0.325])
    # tf.add_option("permutation", ["neighbour"])
    # tf.generate_tests()
