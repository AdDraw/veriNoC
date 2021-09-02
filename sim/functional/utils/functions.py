from random import random
import cocotb
from cocotb.result import TestSuccess, TestFailure
from cocotb.triggers import ClockCycles, RisingEdge, ReadOnly, Combine, FallingEdge
from cocotb.binary import BinaryValue
from random import getrandbits, randint


def bernouli(r):
    if random() < r:
        return True
    else:
        return False

def gen_packet(tb, row, col, packet_length=4):
    packet = [gen_header_flit(tb,
                              tb.config["row_addr_w"],
                              tb.config["col_addr_w"],
                              tb.config["hop_cnt_w"],
                              row=row, col=col, random=False)]
    for j in range(packet_length - 1):
        packet.append(gen_body_flit(tb, tb.config["flit_data_w"]))  # body / payload
    packet.append(gen_body_flit(tb, tb.config["flit_data_w"], flit_id="11"))  # tail

    out_chan = xy_route(tb, row, col)

    tb.packets_to_send.append({"out_chan": out_chan, "packet": packet})
    return packet


def xy_route(tb, row, col, RESOURCE=0, LEFT=1, UP=2, RIGHT=3, DOWN=4):
    row_cord = tb.config["row_cord"]
    col_cord = tb.config["col_cord"]
    assert tb.config["out_m"] == 5, "Wrong number of outputs"
    if col == col_cord:
        if row == row_cord:
            return RESOURCE
        elif row < row_cord:
            return UP
        else:
            return DOWN
    else:
        if col > col_cord:
            return RIGHT
        else:
            return LEFT


def xy_deroute(tb, output_id, RESOURCE=0, LEFT=1, UP=2, RIGHT=3, DOWN=4):
    row_cord = tb.config["row_cord"]
    col_cord = tb.config["col_cord"]
    assert tb.config["out_m"] == 5, "Wrong number of outputs"
    if output_id == RESOURCE:
        return [row_cord, col_cord]
    if output_id == LEFT:
        return [row_cord, col_cord - 1]
    if output_id == RIGHT:
        return [row_cord, col_cord + 1]
    if output_id == UP:
        return [row_cord - 1, col_cord]
    if output_id == DOWN:
        return [row_cord + 1, col_cord]


async def test_input(tb, input_id, output_id, packet_lenght=4):
    cocotb.log.debug(f"START: packet I:{input_id}->O:{output_id}")
    row = xy_deroute(tb, output_id)[0]
    col = xy_deroute(tb, output_id)[1]
    packet = gen_packet(tb, row, col, packet_lenght)
    await tb.drv.send_packet(packet, input_id=input_id)
    cocotb.log.debug(f"END  : packet I:{input_id} -> O:{output_id}")

def populate_packets_to_send(tb, packet_n=10, packet_length=4):
    for i in range(packet_n):

        header = gen_header_flit(tb,
                                 tb.config["row_addr_w"],
                                 tb.config["col_addr_w"],
                                 tb.config["hop_cnt_w"])
        packet = [header[0]]
        out_chan = xy_route(tb, row=header[1], col=header[2])

        for j in range(packet_length-1):
            packet.append(gen_body_flit(tb, tb.config["flit_data_w"]))  # body / payload
        packet.append(gen_body_flit(tb, tb.config["flit_data_w"], flit_id="11"))  # tail

        tb.packets_to_send.append({"out_chan": out_chan, "packet": packet})

def gen_header_flit(tb, row_addr_w, col_addr_w, hop_cnt_w, row=0, col=0, hop_cnt=0, header_id="10", random=True):
    assert (row_addr_w + col_addr_w + hop_cnt_w + len(header_id)) == tb.config["flit_w"], f"Total lenght of Header Flit != FLIT_W"

    if random:
        row_addr = BinaryValue(getrandbits(row_addr_w), row_addr_w, bigEndian=False).binstr
        col_addr = BinaryValue(getrandbits(col_addr_w), col_addr_w, bigEndian=False).binstr
        hop_cnt = BinaryValue(getrandbits(hop_cnt_w), hop_cnt_w, bigEndian=False).binstr
    else:
        assert 0 > row or row <= 2**tb.config["row_addr_w"]-1, "Row Destination Address is too big for the Width provided"
        row_addr = BinaryValue(row, row_addr_w, bigEndian=False).binstr
        assert 0 > col or col <= 2 ** tb.config["col_addr_w"] - 1, "Col Destination Address is too big for the Width provided"
        col_addr = BinaryValue(col, col_addr_w, bigEndian=False).binstr
        assert 0 > hop_cnt or hop_cnt <= 2 ** tb.config["hop_cnt_w"] - 1, "HopCount is too big for the Width provided"
        hop_cnt = BinaryValue(hop_cnt, hop_cnt_w, bigEndian=False).binstr

    header_flit = header_id + row_addr + col_addr + hop_cnt
    if random:
        return [BinaryValue(header_flit, len(header_flit), bigEndian=False).integer,
                BinaryValue(row_addr, len(row_addr), bigEndian=False).integer,
                BinaryValue(col_addr, len(col_addr), bigEndian=False).integer]
    else:
        return BinaryValue(header_flit, len(header_flit), bigEndian=False).integer

def gen_body_flit(tb, data_w, flit_id="01", data=0, random=True):
    assert (data_w + len(flit_id)) == tb.config["flit_w"], "Total lenght of Header Flit != FLIT_W"
    if random:
        data = BinaryValue(getrandbits(data_w), data_w, bigEndian=False).binstr
    else:
        assert 0 > data or data <= 2 ** tb.config["flit_data_w"] - 1, "Data is too big for the Width provided"
        data = BinaryValue(data, data_w, bigEndian=False).binstr
    flit = flit_id + data
    return BinaryValue(flit, len(flit), bigEndian=False).integer
