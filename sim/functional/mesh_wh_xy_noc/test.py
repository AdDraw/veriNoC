from logging import INFO, DEBUG
from cocotb.regression import TestFactory
from cocotb.triggers import RisingEdge, FallingEdge, ReadOnly, ClockCycles, Combine
from cocotb.result import TestSuccess
import os
from utils.functions import *
from noc import WHNoCTB
from noc import NoCMetrics
from cocotb import fork
CLK_PERIOD = int(os.environ["CLK_PERIOD"])


# TestCases
async def simple_test(dut, log_lvl=INFO, bp=False):
  tb = WHNoCTB(dut, log_lvl)
  tb.setup_dut(cycle_n=5, bp=bp)
  await ClockCycles(dut.clk_i, 10)

  for i in range(tb.client_n):
    for j in range(tb.client_n):
      dest_addr = tb.id_to_addr(j)
      if j != i:
        packet = tb.packet.gen_packet(dest=dest_addr, lenght=10)
        x = tb.drv.send_packet_from(i, packet)
        tb.packets_to_send.append({"node": j, "packet": x["packet"]})

  await tb.compare()
  raise TestSuccess("Sim finished sucessfully")


async def competetive_test(dut, log_lvl=INFO, bp=False):
  tb = WHNoCTB(dut, log_lvl)
  tb.setup_dut(cycle_n=5, bp=bp)
  await ClockCycles(dut.clk_i, 10)
  for j in range(tb.client_n):
    for i in range(tb.client_n):
      if j != i:
        dest_addr = tb.id_to_addr(j)
        packet = tb.packet.gen_packet(dest=dest_addr, lenght=10)
        x = tb.drv.send_packet_from(i, packet)
        tb.packets_to_send.append({"node": j, "packet": packet})
  await tb.compare()
  raise TestSuccess("Sim finished sucessfully")


async def random_single_input_at_a_time(dut, log_lvl=INFO, packet_n=30, packet_length=4, bp=False):
  tb = WHNoCTB(dut, log_lvl)
  tb.setup_dut(cycle_n=5, bp=bp)
  await ClockCycles(dut.clk_i, 10)

  for i in range(packet_n):
    x = randint(0, tb.config["row_n"]-1)
    y = randint(0, tb.config["col_m"]-1)
    dest = [x, y]
    packet = tb.packet.gen_packet(dest, lenght=packet_length)
    dest_id = tb.addr_to_id(dest)
    tb.packets_to_send.append({"node": dest_id, "packet": packet})

  for packet in tb.packets_to_send:
    driver_id = randint(0, tb.client_n-1)
    x = tb.drv.send_packet_from(driver_id, packet["packet"])
  await tb.compare()
  raise TestSuccess("Sim finished sucessfully")


async def random_multi_input_at_a_time(dut, log_lvl=INFO, packet_n=10, packet_length=4, bp=False):
  tb = WHNoCTB(dut, log_lvl)
  tb.setup_dut(cycle_n=5)
  await ClockCycles(dut.clk_i, 10)
  in_n = tb.client_n
  for i in range(packet_n * in_n):
    x = randint(0, tb.config["row_n"]-1)
    y = randint(0, tb.config["col_m"]-1)
    dest = [x, y]
    packet = tb.packet.gen_packet(dest, lenght=packet_length, tail_with_payload=False)
    dest_id = tb.addr_to_id(dest)
    tb.packets_to_send.append({"node": dest_id, "packet": packet})
  if bp:
    bp = []
    for in_id in range(tb.client_n):
      bp.append(cocotb.fork(tb.backpressure_gen(in_id)))

  for packet_id in range(packet_n):
    for in_id in range(tb.client_n):
      packet_for_input_i = tb.packets_to_send[(packet_id*in_n) + in_id]["packet"]
      x = tb.drv.send_packet_from(in_id, packet_for_input_i)
  await tb.compare()
  raise TestSuccess("Sim finished sucessfully")


async def measure(dut, log_lvl=INFO, warm_up_period=1000, meas_period=8000,
                  injection_rate=0.3, plen=4, traffic_pattern="u_rand"):

  tb = WHNoCTB(dut, log_lvl)
  tb.setup_dut(cycle_n=5, bp=False, reader_en=False)
  await ClockCycles(dut.clk_i, 10)

  packet_injection_rate = injection_rate/plen
  flit_injection_rate = injection_rate
  tb.noc_metrics = NoCMetrics(traffic_pattern, injection_rate, warm_up_period, meas_period, plen=plen)

  # N1 - warmup
  cocotb.log.info("Measurement Phase: Warmup")
  await tb.meas_phase("warmup", warm_up_period, packet_injection_rate, traffic_pattern, plen=plen)

  # N2 - meas phase, count + time(but only timed packets)
  cocotb.log.info("Measurement Phase: Measurements")
  readers = []
  for out_chan in range(tb.client_n):
    readers.append(cocotb.fork(tb.node_out_chan_reader(out_chan, cycle_n=0, time=True)))
  fork(tb.throughput(cycles=meas_period, injection_ratio=flit_injection_rate, plen=plen))
  await tb.meas_phase("measurement", meas_period, packet_injection_rate, traffic_pattern, plen=plen)

  # N3 - wait for all timed packets to arrive
  cocotb.log.info("Measurement Phase: Drain")
  fork(tb.drain())
  await tb.meas_phase("drain", 0, packet_injection_rate, traffic_pattern, plen=plen)

  raise TestSuccess("Sim finished sucessfully")


if int(os.environ["TESTFACTORY"]) == 1:
  tf = TestFactory(simple_test)
  tf.add_option("bp", [False, True])
  tf.generate_tests()

  tf = TestFactory(competetive_test)
  tf.add_option("bp", [False, True])
  tf.generate_tests()

  tf = TestFactory(random_single_input_at_a_time)
  tf.add_option("bp", [False, True])
  tf.add_option("packet_n", [10, 100, 200])
  tf.add_option("packet_length", [2, 8, 16])
  tf.generate_tests()

  tf = TestFactory(random_multi_input_at_a_time)
  tf.add_option("bp", [False, True])
  tf.add_option("packet_n", [10, 100, 200])
  tf.add_option("packet_length", [2, 8, 16])
  tf.generate_tests()
else:
  tf = TestFactory(simple_test)
  # tf.add_option("bp", [False, True])
  # tf.generate_tests()
  tf = TestFactory(measure)
  tf.add_option("traffic_pattern", ["u_rand", "inverse"])
  tf.add_option("injection_rate", [0.05, 0.1, 0.2, 0.3, 0.4, 0.46, 0.5, 0.55, 0.6, 0.65])
  tf.generate_tests()
