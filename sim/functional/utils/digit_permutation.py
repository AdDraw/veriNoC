def neighbour(val, radix_k):
    return (val + 1) % radix_k


def tornado(val, radix_k):
    return (val - 1) % radix_k


assert neighbour(4, 3) == 2, "neighbour bad val"
assert tornado(4, 3) == 0, "neighbour bad val"
