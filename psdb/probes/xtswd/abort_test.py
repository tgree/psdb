#!/usr/bin/env python3
# Copyright (c) 2022 Phase Advanced Sensor Systems, Inc.
import argparse
import time
import sys

import psdb
from psdb.probes.xtswd.xtswd import (Command, Response, Status, Opcode,
                                     XTSWDCommandException)


def main(rv):
    # Find the target probe.
    probe  = psdb.probes.xtswd.make_one_ns(rv)
    target = probe.probe(connect_under_reset=rv.connect_under_reset,
                         verbose=rv.verbose)

    # Find an SRAM to use.
    ram = next(iter(target.ram_devs.values()))
    print('Using %s...' % ram.name)

    # Start a bulk read to the first SRAM.
    tag = probe._alloc_tag()
    cmd = Command(
            opcode=Opcode.BULK_READ, tag=tag,
            params=[ram.ap.ap_num, ram.dev_base, 256 // 4, 4, 0, 0, 0])
    data = cmd.pack()
    size = probe.usb_dev.write(probe.CMD_EP, data)
    assert size == 32

    # Abort the bulk read.  The write is posted immediately, but if we don't
    # insert a delay then the subsequent read will also be posted immediately
    # and we will race; the read will successfully get at least one extra
    # packet before the abort makes it out.
    probe.usb_dev.write(probe.CMD_EP, b'')
    time.sleep(1)

    # We should have 2 packets posted already to the FIFO, but then it should
    # terminate with an ABORTED response instead of continuing.
    data = probe.usb_dev.read(probe.RSP_EP, 1024)
    print('Got response len %u' % len(data))
    print(bytes(data).hex())
    rsp = Response.unpack(data[-32:])
    rsp.status = Status(rsp.status)
    print(rsp)
    assert len(data)  == 128 + 32
    assert rsp.tag    == tag
    assert rsp.opcode == Opcode.BULK_READ
    assert rsp.status == Status.ABORTED

    # Ensure a read times out.
    try:
        data = probe.usb_dev.read(probe.RSP_EP, 1024)
        got_ex = False
    except Exception as e:
        print('Got expected exception: %s' % e)
        got_ex = True
    assert got_ex

    # Send a bad opcode and ensure we get it back immediately.
    try:
        probe._exec_command(Opcode.BAD_OPCODE)
        got_ex = False
    except XTSWDCommandException as e:
        assert e.rsp.status == Status.BAD_OPCODE
        got_ex = True
    assert got_ex

    # Ensure a read times out.
    try:
        data = probe.usb_dev.read(probe.RSP_EP, 1024)
        got_ex = False
    except Exception as e:
        print('Got expected exception: %s' % e)
        got_ex = True
    assert got_ex

    # Start a bulk write to the first SRAM.
    tag  = probe._alloc_tag()
    cmd  = Command(
             opcode=Opcode.BULK_WRITE, tag=tag,
             params=[ram.ap.ap_num, ram.dev_base, 256 // 4, 4, 0, 0, 0])
    data = cmd.pack() + bytearray(32)
    size = probe.usb_dev.write(probe.CMD_EP, data)
    assert size == 64

    # Abort the bulk write.
    probe.usb_dev.write(probe.CMD_EP, b'')
    time.sleep(1)

    # Read the response.
    data = probe.usb_dev.read(probe.RSP_EP, 64)
    assert len(data) == 32
    rsp = Response.unpack(data)
    rsp.status = Status(rsp.status)
    print(rsp)
    assert rsp.tag    == tag
    assert rsp.opcode == Opcode.BULK_WRITE
    assert rsp.status == Status.ABORTED

    # Ensure a read times out.
    try:
        data = probe.usb_dev.read(probe.RSP_EP, 1024)
        got_ex = False
    except Exception as e:
        print('Got expected exception: %s' % e)
        got_ex = True
    assert got_ex

    # Send a bad opcode and ensure we get it back immediately.
    try:
        probe._exec_command(Opcode.BAD_OPCODE)
        got_ex = False
    except XTSWDCommandException as e:
        assert e.rsp.status == Status.BAD_OPCODE
        got_ex = True
    assert got_ex

    # Ensure a read times out.
    try:
        data = probe.usb_dev.read(probe.RSP_EP, 1024)
        got_ex = False
    except Exception as e:
        print('Got expected exception: %s' % e)
        got_ex = True
    assert got_ex

    print('Abort test successful.')


def _main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--usb-path')
    parser.add_argument('--serial-num')
    parser.add_argument('--connect-under-reset', action='store_true')
    parser.add_argument('--verbose', '-v', action='store_true')
    rv = parser.parse_args()

    try:
        main(rv)
    except psdb.ProbeException as e:
        print(e)
        sys.exit(1)


if __name__ == '__main__':
    _main()
