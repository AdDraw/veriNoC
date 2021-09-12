from random import randint
from utils.address import NodeAddr
from utils.bit_permutation import *
from utils.digit_permutation import *
from cocotb.binary import BinaryValue
from math import ceil, log

class TrafficPattern(object):
  """docstring for TrafficPattern."""

  def __init__(self, dim, addressing="2dxy"):
    super(TrafficPattern, self).__init__()
    self.addressing_scheme = addressing
    self.dim = dim
    if self.addressing_scheme == "2dxy":
      assert len(dim) == 2, "dim should only hold 2 values"
      self.row_n = dim[0]
      self.col_m = dim[1]
      self.row_n_w = ceil(log(self.row_n))
      self.col_m_w = ceil(log(self.col_m))
    else:
      print("Unsupported addressing scheme!")
      raise ValueError

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

  def bit_permutation(self, node_in: NodeAddr, traffic_pattern: str) -> NodeAddr:
    print(traffic_pattern)
    if self.addressing_scheme == "2dxy":
      x = BinaryValue(node_in.row, self.row_n_w, bigEndian=False)
      y = BinaryValue(node_in.col, self.col_m_w, bigEndian=False)
      binstr = x.binstr + y.binstr

      if traffic_pattern == "inverse":
        new_binstr = invert(binstr)
      elif traffic_pattern == "reverse":
        new_binstr = reverse(binstr)
      elif traffic_pattern == "rotate":
        new_binstr = rotate(binstr)
      elif traffic_pattern == "shuffle":
        new_binstr = shuffle(binstr)
      else:
        print("This Bit Permutation option is not supported!")
        raise ValueError

      new_x = BinaryValue(new_binstr[:x.n_bits], self.row_n_w, bigEndian=False)
      if new_x.integer > self.row_n - 1:
        new_x.value = self.row_n - 1
      new_y = BinaryValue(new_binstr[ x.n_bits:], self.row_n_w, bigEndian=False)
      if new_y.integer > self.col_m - 1:
        new_y.value = self.col_m - 1
      # print(f"old {x.binstr}, {y.binstr}, {binstr}")
      # print(f"new {new_x.binstr}, {new_y.binstr}, {new_binstr}")
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


# tp = TrafficPattern([3,3])
# print(tp.u_rand(0))
# node = NodeAddr([0, 1], tp.dim)
# print("INPUT NODE")
# print(f"coords {node.row}, {node.col}")
# print(f"id     {node.id}")
# print("")
#
# new_node = tp.bit_permutation(node, "invert")
# print(f"coords {new_node.row}, {new_node.col}")
# print(f"id     {new_node.id}")
#
# new_node = tp.bit_permutation(node, "reverse")
# print(f"coords {new_node.row}, {new_node.col}")
# print(f"id     {new_node.id}")
#
# new_node = tp.bit_permutation(node, "rotate")
# print(f"coords {new_node.row}, {new_node.col}")
# print(f"id     {new_node.id}")
#
# new_node = tp.bit_permutation(node, "shuffle")
# print(f"coords {new_node.row}, {new_node.col}")
# print(f"id     {new_node.id}")
#
# new_node = tp.digit_permutation(node, "neighbour")
# print(f"coords {new_node.row}, {new_node.col}")
# print(f"id     {new_node.id}")
