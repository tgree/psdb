#!/usr/bin/env python3
# Copyright (c) 2018-2019 Phase Advanced Sensor Systems, Inc.
import psdb.probes

from struct import unpack_from
import argparse
import sys


PATTERN = (b'0123456789ABCDEF'
           b'abcdefghijklmnop'
           b'qrstuvwxyzZYXWVU'
           b'TSRQPONMLKJIHGFE'
           b'DCBAfedcba987654'
           b'3210')


def zap_pattern(rv, rd, pattern):
    rd.write_mem_block(pattern, rd.dev_base)


def write_pattern_bulk(rv, rd, offset, pattern):
    rd.ap.write_bulk(pattern, rd.dev_base + offset)
    assert rd.ap.read_bulk(rd.dev_base + offset, len(pattern)) == pattern


def write_pattern_8(rv, rd, offset, pattern):
    rd.ap.db._bulk_write_8(pattern, rd.dev_base + offset, rd.ap.ap_num)
    assert rd.ap.db._bulk_read_8(rd.dev_base + offset, len(pattern),
                                 rd.ap.ap_num) == pattern
    for i in range(len(pattern)):
        assert rd.ap.read_8(rd.dev_base + offset + i) == pattern[i]


def write_pattern_16(rv, rd, offset, pattern):
    rd.ap.db._bulk_write_16(pattern, rd.dev_base + offset, rd.ap.ap_num)
    assert rd.ap.db._bulk_read_16(rd.dev_base + offset, len(pattern) // 2,
                                  rd.ap.ap_num) == pattern
    for i in range(len(pattern) // 2):
        assert (rd.ap.read_16(rd.dev_base + offset + i*2) ==
                unpack_from('<H', pattern, i*2)[0])


def write_pattern_32(rv, rd, offset, pattern):
    rd.ap.db._bulk_write_32(pattern, rd.dev_base + offset, rd.ap.ap_num)
    assert rd.ap.db._bulk_read_32(rd.dev_base + offset, len(pattern) // 4,
                                  rd.ap.ap_num) == pattern
    for i in range(len(pattern) // 4):
        assert (rd.ap.read_32(rd.dev_base + offset + i*4) ==
                unpack_from('<I', pattern, i*4)[0])


def test_pattern(rv, rd, pattern):
    assert rd.read_mem_block(rd.dev_base, len(pattern)) == pattern


def test_sram(rd, rv):
    # Do many tests.
    print('Testing %s' % rd.name)
    global PATTERN
    for start in range(4):
        for end in range(len(PATTERN) - 3, len(PATTERN) + 1):
            zpattern = b' '*len(PATTERN)
            pattern  = PATTERN[start:end]
            epattern = zpattern[:start] + pattern + zpattern[end:]
            assert len(zpattern) == len(epattern)
            print('Test pattern: %s' % epattern)

            # Do bulk test.
            print('  Doing bulk test...')
            zap_pattern(rv, rd, zpattern)
            test_pattern(rv, rd, zpattern)
            write_pattern_bulk(rv, rd, start, pattern)
            test_pattern(rv, rd, epattern)

            # Do 8-bit test.
            print('  Doing 8-bit test...')
            zap_pattern(rv, rd, zpattern)
            test_pattern(rv, rd, zpattern)
            write_pattern_8(rv, rd, start, pattern)
            test_pattern(rv, rd, epattern)

            # Do 16-bit test.
            if (start % 2) or (len(pattern) % 2):
                continue
            print('  Doing 16-bit test...')
            zap_pattern(rv, rd, zpattern)
            test_pattern(rv, rd, zpattern)
            write_pattern_16(rv, rd, start, pattern)
            test_pattern(rv, rd, epattern)

            # Do 32-bit test.
            if (start % 4) or (len(pattern) % 4):
                continue
            print('  Doing 32-bit test...')
            zap_pattern(rv, rd, zpattern)
            test_pattern(rv, rd, zpattern)
            write_pattern_32(rv, rd, start, pattern)
            test_pattern(rv, rd, epattern)


def main(rv):
    # Dump all debuggers if requested.
    if rv.dump_debuggers:
        psdb.probes.dump_probes()

    # Probe the specified serial number (or find the default if no serial number
    # was specified.
    probe = psdb.probes.find_default(usb_path=rv.usb_path)
    f     = probe.set_tck_freq(rv.probe_freq)
    print('Probing with SWD frequency at %.3f MHz' % (f/1.e6))

    # Use the probe to detect a target platform.
    target = probe.probe(verbose=rv.verbose,
                         connect_under_reset=rv.connect_under_reset)
    f      = target.set_max_tck_freq()
    print('Set SWD frequency to %.3f MHz' % (f/1.e6))

    # Test all SRAMs.
    for rd in target.ram_devs.values():
        test_sram(rd, rv)


def _main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dump-debuggers', '-d', action='store_true')
    parser.add_argument('--usb-path')
    parser.add_argument('--connect-under-reset', action='store_true')
    parser.add_argument('--probe-freq', type=int, default=1000000)
    parser.add_argument('--verbose', '-v', action='store_true')
    rv = parser.parse_args()

    try:
        main(rv)
    except psdb.ProbeException as e:
        print(e)
        sys.exit(1)


if __name__ == '__main__':
    _main()
