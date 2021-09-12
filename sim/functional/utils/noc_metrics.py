from logging import INFO, DEBUG
from cocotb.log import SimLog

class NoCMetrics(object):
  """docstring for NoCMetrics."""
  offered_traffic = 0
  # throughput
  accepted_traffic = 0
  min_accepted_traffic = 0
  max_accepted_traffic = 0
  # latency
  avg_packet_latency = 0
  min_packet_latency = pow(2,20)
  max_packet_latency = -1
  # Stats
  warmup_period = 0
  meas_period = 0

  def __init__(self, name, offered_traffic, warmup_period, meas_period, plen=None, log_lvl=INFO):
    super(NoCMetrics, self).__init__()
    self.log = SimLog("noc_metrics")
    self.log.setLevel(log_lvl)
    self.name = name
    if plen is not None:
      self.plen = plen
    self.offered_traffic = offered_traffic
    self.warmup_period = warmup_period
    self.meas_period = meas_period

  def print(self):
    self.log.warning("Metrics")
    self.log.warning(f"- OFFERED TRAFFIC = {self.offered_traffic:.4f}")
    self.log.warning(f"- Packet LEN      = {self.plen}")
    self.log.warning(f"- warm_up_period [cyc] = {self.warmup_period}")
    self.log.warning(f"- meas_period    [cyc] = {self.meas_period}")
    self.log.info("1. Latency:")
    self.log.info(f"   - Avg packet latency [ns] : {self.avg_packet_latency:.2f} ns")
    self.log.info(f"   - Min packet latency [ns] : {self.min_packet_latency:.2f} ns")
    self.log.info(f"   - Max packet latency [ns] : {self.max_packet_latency:.2f} ns")
    self.log.info("2. Throughput:")
    self.log.info(f"   - Avg throughput : {self.accepted_traffic:.4f} | {self.offered_traffic:.4f}")
    self.log.info(f"   - Min throughput : {self.min_accepted_traffic:.4f} | {self.offered_traffic:.4f}")
    self.log.info(f"   - Max throughput : {self.max_accepted_traffic:.4f} | {self.offered_traffic:.4f}")

  def json_gen(self):
    json = {"name": self.name}
    json["offered_traffic"] = self.offered_traffic
    json["packet_lenght"] = self.plen
    json["warmup_period"] = self.warmup_period
    json["measurement_period"] = self.meas_period
    json["avg_packet_latency"] = self.avg_packet_latency
    json["min_packet_latency"] = self.min_packet_latency
    json["max_packet_latency"] = self.max_packet_latency
    json["accepted_traffic"] = self.accepted_traffic
    json["min_accepted_traffic"] = self.min_accepted_traffic
    json["max_accepted_traffic"] = self.max_accepted_traffic
    return json
