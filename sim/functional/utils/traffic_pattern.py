from random import randint
from utils.address import NodeAddr
from utils.bit_permutation import *
from utils.digit_permutation import *
from cocotb.binary import BinaryValue
from math import ceil, log2, floor
from random import random, sample


class TrafficPattern(object):
  """docstring for TrafficPattern."""

  def __init__(self, dim, addressing="2dxy"):
    super(TrafficPattern, self).__init__()
    self.addressing_scheme = addressing
    self.dim = dim
    self.hotspots = None
    if self.addressing_scheme == "2dxy":
      assert len(dim) == 2, "dim should only hold 2 values"
      self.row_n = dim[0]
      self.col_m = dim[1]
      self.row_n_w = ceil(log2(self.row_n))
      self.col_m_w = ceil(log2(self.col_m))
      self.node_n = self.row_n * self.col_m
    else:
      print("Unsupported addressing scheme!")
      raise ValueError

  def gen_node_from_id(self, id) -> NodeAddr:
    node = NodeAddr([0,0], self.dim)
    node.update(id)
    return node

  def uniform_random(self, input_i):
    if self.addressing_scheme == "2dxy":
      x = randint(0, self.row_n - 1)
      y = randint(0, self.col_m - 1)
      node = NodeAddr([x, y], self.dim)
      while node.id == input_i:
        x = randint(0, self.row_n - 1)
        y = randint(0, self.col_m - 1)
        node = NodeAddr([x, y], [self.row_n, self.col_m])
      return node
    else:
      print("Unsupported addressing scheme!")
      raise ValueError

  def hotspot(self, input_i, hotspot_prob=0.5, hotspot_percentage=0.3, spots = None):
    assert hotspot_prob == 0.5 or hotspot_prob == 0.7, "WRONG hotspot prob value"
    assert 0 < hotspot_percentage <= 1, "GIVEN m is not EVEN!"
    if spots is None:
      if self.hotspots is None:
        # choose hotspots based on N only once !
        hotspot_n = floor(self.node_n * hotspot_percentage)
        if hotspot_n == 0:
          hotspot_n = 1
        self.hotspots = sample(range(self.node_n), hotspot_n)
    else:
      self.hotspots = spots

    if self.addressing_scheme == "2dxy":
      node_src = self.gen_node_from_id(input_i)
      r = random()
      dd = 0
      if r <= hotspot_prob:
        hotspots = self.hotspots.copy()
        if input_i in hotspots:
          hotspots.remove(input_i)
        if len(hotspots) != 0:
          node_out = sample(hotspots, 1)
        else:
          cold_spots = [x for x in range(self.node_n) if x not in self.hotspots]
          node_out = sample(cold_spots, 1)
      else:
        cold_spots = [x for x in range(self.node_n) if x not in self.hotspots]
        if input_i in cold_spots:
          cold_spots.remove(input_i)
        node_out = sample(cold_spots, 1)

      dest_node = self.gen_node_from_id(*node_out)
      assert node_src.id != dest_node.id, "SOMETHING WENT WRONG!"
      return dest_node

    else:
      print("Unsupported addressing scheme!")
      raise ValueError

  def locality(self, input_i):
    assert 0 <= input_i < self.node_n, "wrong INPUT ID"
    if self.addressing_scheme == "2dxy":
      node_addr_src = self.gen_node_from_id(input_i)
      distances = self.node_n * [0]
      P_n = self.node_n * [1]
      unique_dist = []

      for i in range(self.node_n):
        if input_i == i:
          P_n[i] = 0
          distances[i] = 0
        else:
          dest_node = self.gen_node_from_id(i)
          distances[i] = abs(dest_node.row - node_addr_src.row) + abs(dest_node.col - node_addr_src.col)
        if distances[i] not in unique_dist:
          unique_dist.append(distances[i])
          D = max(unique_dist)

      A_D = 0
      for i in range(D):
        A_D += pow(2, -(i+1))
      P_d = len(unique_dist)*[0]

      for dist in range(len(unique_dist)):
        if dist == 0:
          P_d[dist] = 0
        else:
          P_d[dist] = (1/(A_D * pow(2, dist)))

      for dest in range(self.node_n):
        P_n[dest] = P_n[dest] * (1/(A_D * pow(2, distances[dest])))

      # FIRST CHOOSE DISTANCE
      r = random()
      dd = 0
      for i in range(len(P_d)):
        if i > 0:
          low_prob = sum(P_d[ : i])
          high_prob = sum(P_d[: i+1])
          if high_prob - low_prob != 0:
            if low_prob < r <= high_prob :
              dd = i
              break

      # SECOND CHOOSE NODE with 1/N
      uni_nodes = []
      for node in range(self.node_n):
        if dd == distances[node]:
          uni_nodes.append(node)
      node_out = sample(uni_nodes, 1)


      dest_node = self.gen_node_from_id(*node_out)

      assert node_addr_src.id != dest_node.id, "SOMETHING WENT WRONG!"

      return dest_node
    else:
      print("Unsupported addressing scheme!")
      raise ValueError

  def nearest_neighbor(self, input_i, radius=1, nearest_prob=0.7):
    assert radius > 0, "radius 0 would limit possible destinations to src node"
    assert nearest_prob > 0.5, "if it's smaller than it'snot nearest neighbour"
    assert nearest_prob <= 1, "You cannot have probability greater than 100%"

    if self.addressing_scheme == "2dxy":
      node_src = self.gen_node_from_id(input_i)
      distances = self.node_n * [0]
      P_n = self.node_n * [1]
      unique_dist = []
      for i in range(self.node_n):
        if input_i == i:
          P_n[i] = 0
          distances[i] = 0
        else:
          dest_node = self.gen_node_from_id(i)
          distances[i] = abs(dest_node.row - node_src.row) + abs(dest_node.col - node_src.col)
        if distances[i] not in unique_dist:
          unique_dist.append(distances[i])

      for node_id in range(len(distances)):
        if distances[node_id] <= radius:
          P_n[node_id] = P_n[node_id] * nearest_prob
        else:
          P_n[node_id] = P_n[node_id] * (1 - nearest_prob)

      r = random()
      if r <= nearest_prob:
        dd = nearest_prob
      else:
        dd = 1 - nearest_prob

      uni_nodes = []
      for node in range(self.node_n):
        if dd == P_n[node]:
          uni_nodes.append(node)
      node_out = sample(uni_nodes, 1)

      dest_node = self.gen_node_from_id(*node_out)
      assert node_src.id != dest_node.id, "SOMETHING WENT WRONG!"
      return dest_node
    else:
      print("Unsupported addressing scheme!")
      raise ValueError


  def bit_permutation(self, input_i, traffic_pattern: str) -> NodeAddr:
    if self.addressing_scheme == "2dxy":
      node_in = self.gen_node_from_id(input_i)
      x = BinaryValue(node_in.row, self.row_n_w, bigEndian=False)
      y = BinaryValue(node_in.col, self.col_m_w, bigEndian=False)
      binstr = x.binstr + y.binstr

      if traffic_pattern == "complement":
        new_binstr = complement(binstr)
      elif traffic_pattern == "reverse":
        new_binstr = reverse(binstr)
      elif traffic_pattern == "rotate":
        new_binstr = rotate(binstr)
      elif traffic_pattern == "shuffle":
        new_binstr = shuffle(binstr)
      elif traffic_pattern == "transpose":
        new_binstr = transpose(x.binstr, y.binstr)
      else:
        print("This Bit Permutation option is not supported!")
        raise ValueError

      new_x = BinaryValue(new_binstr[:x.n_bits], self.row_n_w, bigEndian=False)
      if new_x.integer > self.row_n - 1:
        new_x.value = self.row_n - 1

      new_y = BinaryValue(new_binstr[ x.n_bits:], self.col_m_w, bigEndian=False)
      if new_y.integer > self.col_m - 1:
        new_y.value = self.col_m - 1

      return NodeAddr([new_x.integer, new_y.integer], self.dim)
    else:
      print("Unsupported addressing scheme!")
      raise ValueError

  def digit_permutation(self, node_in: NodeAddr, traffic_pattern: str) -> NodeAddr:
    if self.addressing_scheme == "2dxy":
      x = node_in.row
      y = node_in.col
      if traffic_pattern == "neighbour":
        new_x = neighbour(x, self.row_n)
        new_y = neighbour(y, self.row_n)
      elif traffic_pattern == "tornado":
        new_x = tornado(x, self.row_n)
        new_y = tornado(y, self.row_n)
      else:
        print("This Digit Permutation option is not supported!")
        raise ValueError
      return NodeAddr([new_x, new_y], self.dim)
    else:
      print("Unsupported addressing scheme!")
      raise ValueError


tp = TrafficPattern([5,5])
