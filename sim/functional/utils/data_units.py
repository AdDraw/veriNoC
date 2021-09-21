from cocotb.binary import BinaryValue
from random import getrandbits, randint
from math import ceil, log2
from utils.functions import *


class Flit(object):
  """docstring for Flit."""

  _flit_id = {
    "head": "10",
    "body": "01",
    "tail": "11"
  }

  def __init__(self, flit_id_w, flit_data_w, row_addr_w, col_addr_w):
    super(Flit, self).__init__()
    self.flit_id_w = flit_id_w
    self.flit_data_w = flit_data_w
    self.row_addr_w = row_addr_w
    self.col_addr_w = col_addr_w

  def gen_header(self, row_id, col_id):
    row_addr = BinaryValue(row_id, self.row_addr_w, bigEndian=False).binstr
    col_addr = BinaryValue(col_id, self.col_addr_w, bigEndian=False).binstr
    network_info = row_addr + col_addr
    null = ""
    header = self._flit_id["head"] + network_info + null_string(self.flit_data_w - len(network_info))
    return BinaryValue(header, len(header), bigEndian=False).integer

  def gen_payload_flit(self, data=None, randomize=True):
    if randomize is True:
      data = rand_string(self.flit_data_w)
    else:
      data = value_2_string(data, self.flit_data_w)
    body = self._flit_id["body"] + data
    return BinaryValue(body, len(body), bigEndian=False).integer

  def gen_tail(self, payload = False, value = None):
    if payload is True:
      if value is None:
        data = rand_string(self.flit_data_w)
      else:
        data = value_2_string(value, self.flit_data_w)
    else:
      data = null_string(self.flit_data_w)
    tail = self._flit_id["tail"] + data
    return BinaryValue(tail, len(tail), bigEndian=False).integer


class Packet(object):
  """docstring for Packet."""

  def __init__(self, row_n, col_m, max_lenght, channel_w, flit_id_w, routing_alg="xy"):
    super(Packet, self).__init__()
    assert channel_w > flit_id_w, "Channel has to be wider than flit id"
    self.max_lenght = max_lenght
    self.channel_w = channel_w
    self.flit_id_w = flit_id_w
    self.flit_data_w = channel_w - flit_id_w
    self.row_n = row_n
    self.col_m = col_m
    self.row_addr_w = ceil(log2(row_n))
    self.col_addr_w = ceil(log2(col_m))
    assert self.flit_data_w >= (self.row_addr_w + self.col_addr_w), "Data section of the FLIT is not wide enough to contain DEST"
    self.routing_alg = routing_alg
    self.flit = Flit(self.flit_id_w, self.flit_data_w,
                     self.row_addr_w, self.col_addr_w)

  def gen_packet(self, dest, lenght, rand_data=True, tail_with_payload=True):
    assert self.routing_alg == "xy", "Bad ALG"
    row_id = 0
    col_id = 0
    if self.routing_alg == "xy":
      row_id = dest[0]
      col_id = dest[1]
    packet = [self.flit.gen_header(row_id, col_id)]
    if tail_with_payload:
      body_len = lenght - 2
    else:
      body_len = lenght - 1
    for i in range(body_len):
        packet.append(self.flit.gen_payload_flit(randomize=rand_data))
    packet.append(self.flit.gen_tail(payload=tail_with_payload))

    return packet
