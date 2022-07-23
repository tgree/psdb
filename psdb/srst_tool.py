#!/usr/bin/env python3
# Copyright (c) 2018-2020 Phase Advanced Sensor Systems, Inc.
import argparse
import sys

import psdb.probes


def main(rv):
    # Dump all debuggers if requested.
    if rv.dump_debuggers:
        psdb.probes.dump_probes()

    # Probe the specified serial number (or find the default if no serial number
    # was specified.
    probe = psdb.probes.make_one_ns(rv)

    # SRST the target.
    if rv.hold:
        probe.assert_srst()
    else:
        probe.srst_target()


def _main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dump-debuggers', '-d', action='store_true')
    parser.add_argument('--usb-path')
    parser.add_argument('--serial-num')
    parser.add_argument('--hold', action='store_true')
    rv = parser.parse_args()

    try:
        main(rv)
    except psdb.ProbeException as e:
        print(e)
        sys.exit(1)


if __name__ == '__main__':
    _main()
