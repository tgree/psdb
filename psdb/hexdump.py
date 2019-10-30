# Copyright (c) 2018-2019 Phase Advanced Sensor Systems, Inc.
from builtins import bytes, range


def hexdump(mem, addr=0):
    vals  = ['%02X' % ord(bytes([c])) for c in mem]
    lines = [vals[i:i+16] for i in range(0, len(vals), 16)]
    for i, l in enumerate(lines):
        print('0x%08X: %s' % (addr + i*16, ' '.join(l)))
