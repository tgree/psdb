#!/usr/bin/env python3
# Copyright (c) 2018-2019 Phase Advanced Sensor Systems, Inc.
import argparse
import random
import time
import math
import sys

import psdb.probes


SEED = None
EXCLUDE_SRAMS = ['Backup SRAM']


class LCG:
    def __init__(self, A, C, M, x=0):
        self.A = A
        self.C = C
        self.M = M
        self.x = x

    def get_next(self):
        self.x = (self.A*self.x + self.C) % self.M
        return self.x

    @staticmethod
    def make_std(seed):
        return LCG(48271, 0, 0x7FFFFFFF, seed)


def test_sram(t, rd, _rv, lcg, timeout=10):
    print('Testing %s with seed %u' % (rd.name, lcg.x))
    ap         = rd.ap
    ap_num     = ap.ap_num
    db         = ap.db
    ram_buf    = bytearray(rd.size)
    mv         = memoryview(ram_buf)
    ap.write_bulk(ram_buf, rd.dev_base)
    data = ap.read_bulk(rd.dev_base, rd.size)
    assert data == ram_buf

    t0 = time.time()
    while time.time() - t0 < timeout:
        offset0    = (lcg.get_next() % rd.size)
        offset1    = (lcg.get_next() % (rd.size + 1))
        offset     = min(offset0, offset1)
        addr       = rd.dev_base + offset
        count      = max(offset0, offset1) - offset
        if count == 0:
            continue

        pg_offset0 = (lcg.get_next() % 0x400)
        pg_offset1 = (lcg.get_next() % 0x401)
        pg_offset  = (offset0 & 0xFFFFFC00) + min(pg_offset0, pg_offset1)
        pg_addr    = rd.dev_base + pg_offset
        pg_count   = max(pg_offset0, pg_offset1) - min(pg_offset0, pg_offset1)
        if pg_count == 0:
            continue

        choice = (lcg.get_next() % 9)
        if choice == 0:
            # Bulk write test.
            data = random.randbytes(count)
            print('WB  0x%08X:0x%08X %u' % (addr, offset, count))
            mv[offset:offset + count] = data
            ap.write_bulk(data, addr)
        elif choice == 1:
            # Bulk read test.
            print('RB  0x%08X:0x%08X %u' % (addr, offset, count))
            data = ap.read_bulk(addr, count)
            assert data == mv[offset:offset + count]
        elif choice == 2:
            # 8-bit write test.
            data = random.randbytes(pg_count)
            print('W8  0x%08X:0x%08X %u' % (pg_addr, pg_offset, pg_count))
            mv[pg_offset:pg_offset + pg_count] = data
            db._bulk_write_8(data, pg_addr, ap_num=ap_num)
        elif choice == 3:
            # 8-bit read test.
            print('R8  0x%08X:0x%08X %u' % (pg_addr, pg_offset, pg_count))
            data = db._bulk_read_8(pg_addr, pg_count, ap_num=ap_num)
            assert data == mv[pg_offset:pg_offset + pg_count]
        elif choice == 4:
            # 16-bit write test.
            pg_addr   = (pg_addr & 0xFFFFFFFE)
            pg_offset = (pg_offset & 0xFFFFFFFE)
            pg_count  = math.ceil(pg_count / 2)
            data      = random.randbytes(pg_count * 2)
            print('W16 0x%08X:0x%08X %u' % (pg_addr, pg_offset, pg_count * 2))
            mv[pg_offset:pg_offset + pg_count * 2] = data
            db._bulk_write_16(data, pg_addr, ap_num=ap_num)
        elif choice == 5:
            # 16-bit read test.
            pg_addr   = (pg_addr & 0xFFFFFFFE)
            pg_offset = (pg_offset & 0xFFFFFFFE)
            pg_count  = math.ceil(pg_count / 2)
            print('R16 0x%08X:0x%08X %u' % (pg_addr, pg_offset, pg_count * 2))
            data      = db._bulk_read_16(pg_addr, pg_count, ap_num=ap_num)
            assert data == mv[pg_offset:pg_offset + pg_count * 2]
        elif choice == 6:
            # 32-bit write test.
            pg_addr   = (pg_addr & 0xFFFFFFFC)
            pg_offset = (pg_offset & 0xFFFFFFFC)
            pg_count  = math.ceil(pg_count / 4)
            data      = random.randbytes(pg_count * 4)
            print('W32 0x%08X:0x%08X %u' % (pg_addr, pg_offset, pg_count * 4))
            mv[pg_offset:pg_offset + pg_count * 4] = data
            db._bulk_write_32(data, pg_addr, ap_num=ap_num)
        elif choice == 7:
            # 32-bit read test.
            pg_addr   = (pg_addr & 0xFFFFFFFC)
            pg_offset = (pg_offset & 0xFFFFFFFC)
            pg_count  = math.ceil(pg_count / 4)
            print('R32 0x%08X:0x%08X %u' % (pg_addr, pg_offset, pg_count * 4))
            data      = db._bulk_read_32(pg_addr, pg_count, ap_num=ap_num)
            assert data == mv[pg_offset:pg_offset + pg_count * 4]
        elif choice == 8:
            # Read fault test.
            addr = t.get_fault_addr()
            print('RFL 0x%08X' % addr)
            try:
                ap.read_32(addr)
                got_exception = False
            except Exception:
                got_exception = True
            assert got_exception

    data = ap.read_bulk(rd.dev_base, rd.size)
    assert data == ram_buf


def main(rv):
    global SEED

    # Dump all debuggers if requested.
    if rv.dump_debuggers:
        psdb.probes.dump_probes()

    # Probe the specified serial number (or find the default if no serial number
    # was specified.
    probe = psdb.probes.make_one_ns(rv)
    f     = probe.set_tck_freq(rv.probe_freq)
    print('Probing with SWD frequency at %.3f MHz' % (f/1.e6))

    # Use the probe to detect a target platform.
    target = probe.probe(verbose=rv.verbose,
                         connect_under_reset=rv.connect_under_reset)
    f      = probe.set_max_target_tck_freq()
    print('Set SWD frequency to %.3f MHz' % (f/1.e6))

    # Test all SRAMs.
    if rv.seed is not None:
        seed = rv.seed
    else:
        seed = random.randint(0, 0x7FFFFFFE)
    SEED     = seed
    lcg      = LCG.make_std(seed)
    mem_name = rv.mem_name
    if mem_name:
        assert mem_name not in EXCLUDE_SRAMS
    while True:
        for rd in target.ram_devs.values():
            if mem_name is not None and mem_name != rd.name:
                continue
            if rd.name in EXCLUDE_SRAMS:
                continue

            test_sram(target, rd, rv, lcg)
            mem_name = None


def _main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dump-debuggers', '-d', action='store_true')
    parser.add_argument('--usb-path')
    parser.add_argument('--serial-num')
    parser.add_argument('--connect-under-reset', action='store_true')
    parser.add_argument('--probe-freq', type=int, default=1000000)
    parser.add_argument('--verbose', '-v', action='store_true')
    parser.add_argument('--enable-fault-write-test', action='store_true')
    parser.add_argument('--seed', type=int)
    parser.add_argument('--mem-name')
    rv = parser.parse_args()

    try:
        main(rv)
    except psdb.ProbeException as e:
        print(e)
        sys.exit(1)
    except KeyboardInterrupt:
        print()
    finally:
        if SEED is not None:
            print('Initial seed was: %u' % SEED)


if __name__ == '__main__':
    _main()
