class NodeAddr(object):
  """docstring for NodeAddr."""

  def __init__(self, addr, dim, addr_scheme = "2dxy"):
    super(NodeAddr, self).__init__()
    self.dim = dim
    if addr_scheme == "2dxy":
      assert len(addr) == 2, "addr should only have 2 positions!"
      self.row = addr[0]
      self.col = addr[1]
      self.id = addr[0] * dim[1] + addr[1]
      self.addr = divmod(self.id, dim[1])
      # self.binstr =
    elif addr_scheme == "3dxy":
      assert len(addr) == 2, "addr should only have 3 positions!"
      self.row = addr[0]
      self.col = addr[1]
      self.depth = addr[2]
      # self.id  = addr[0] * self.col_m + addr[1]
    else:
      print("Unknown Addressing scheme!")
      raise ValueError

  def update(self, id, addr_scheme = "2dxy"):
    if addr_scheme == "2dxy":
      self.id = id
      self.addr = divmod(self.id, self.dim[1])
      self.row = self.addr[0]
      self.col = self.addr[1]
    else:
      print("Unknown Addressing scheme!")
      raise ValueError
