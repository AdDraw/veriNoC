class NodeAddr(object):
  """docstring for NodeAddr."""

  def __init__(self, address, dim, addressing_scheme = "2dxy"):
    super(NodeAddr, self).__init__()
    self.dim = dim
    if addressing_scheme == "2dxy":
      assert len(address) == 2, "Address should only have 2 positions!"
      self.row = address[0]
      self.col = address[1]
      self.id = address[0] * dim[1] + address[1]
      self.addr = divmod(self.id, dim[1])
      # self.binstr =
    elif addressing_scheme == "3dxy":
      assert len(address) == 2, "Address should only have 3 positions!"
      self.row = address[0]
      self.col = address[1]
      self.depth = address[2]
      # self.id  = address[0] * self.col_m + address[1]
    else:
      print("Unknown Addressing scheme!")
      raise ValueError

  def update(self, id, addressing_scheme = "2dxy"):
    if addressing_scheme == "2dxy":
      self.id = id
      self.addr = divmod(self.id, self.dim[1])
      self.row = self.addr[0]
      self.col = self.addr[1]
    else:
      print("Unknown Addressing scheme!")
      raise Error
