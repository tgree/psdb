#!/usr/bin/env python3
# Copyright (c) 2022 Phase Advanced Sensor Systems, Inc.
import argparse
import sys

import psdb.probes


def main(rv):
    # Dump all debuggers if requested.
    if rv.dump_debuggers:
        psdb.probes.dump_probes()

    # Find the target probe and dump the stats.
    probe = psdb.probes.make_one_ns(rv)
    stats = probe.get_stats()
    stats.dump()


def _main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dump-debuggers', '-d', action='store_true')
    parser.add_argument('--usb-path')
    parser.add_argument('--serial-num')
    rv = parser.parse_args()

    try:
        main(rv)
    except psdb.ProbeException as e:
        print(e)
        sys.exit(1)


if __name__ == '__main__':
    _main()
