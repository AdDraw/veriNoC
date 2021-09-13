import numpy as np


def complement(binstr):
  # bitwise not on the address bits
  return ''.join(['1' if i == '0' else '0' for i in binstr])


def reverse(binstr):
  # reverse address bits order reverse 1..N-1 -> N-1..1
  return binstr[::-1]


def shuffle(binstr):
  # move bits by 1 to the left
  new_bin = binstr[1::]
  new_bin += binstr[0]
  return new_bin


def rotate(binstr):
  # move bits by 1 to the right
  new_bin = binstr[-1]
  new_bin += binstr[0:-1]
  return new_bin


def transpose(x_binstr, y_binstr):
  # take each coordinate's binary represenation
  # create a 2 row numpy array with 1 bit per column of the row
  # do np.transpose()
  x = x_binstr
  y = y_binstr
  x_arr = []
  for char in x:
    x_arr.append(char)
  y_arr = []
  for char in y:
    y_arr.append(char)
  arr = np.array([x_arr,y_arr])
  T = arr.transpose()
  addr = ""
  for cord in T:
    x = ""
    for bit in cord:
      x = x + bit
    addr = addr + x
  return addr


assert rotate("1110") == "0111", "Rot Error"
assert shuffle("1110") == "1101", "Shuffle Error"
assert reverse("1000") == "0001", "Reverse Error"
assert complement("1110") == "0001", "Inv Error"
assert transpose("10", "11") == "1101", "Transpose Error"


# print(f"INPUT 0001")
# print(f"      {invert('0001')} - complement bitwise not")
# print(f"      {reverse('0001')} - reverse 1..N-1 -> N-1..1")
# print(f"      {shuffle('0001')} - shuffle move to left by 1")
# print(f"      {rotate('0001')} - rotate move to right by 1")
