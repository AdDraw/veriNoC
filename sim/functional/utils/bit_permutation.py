def invert(binstr):
    return ''.join(['1' if i == '0' else '0' for i in binstr])


def reverse(binstr):
    return binstr[::-1]


def shuffle(binstr):
    # you move by 1 in the left position
    new_bin = binstr[1::]
    new_bin += binstr[0]
    return new_bin


def rotate(binstr):
    # move by 1 in right position
    new_bin = binstr[-1]
    new_bin += binstr[0:-1]
    return new_bin


assert rotate("1110") == "0111", "Rot Error"
assert shuffle("1110") == "1101", "Shuffle Error"
assert reverse("1000") == "0001", "Reverse Error"
assert invert("1110") == "0001", "Inv Error"
