#!/usr/bin/env python3
# Copyright (c) 2018-2019 Phase Advanced Sensor Systems, Inc.
import psdb.probes

import sys


def main():
    for e in psdb.probes.enumerate_probes():
        try:
            p = e.make_probe()
        except Exception as ex:
            e.show_info()
            print('Exception making probe: %s' % ex)
            continue

        p.show_detailed_info()
        try:
            p.probe(verbose=True).resume()
        except Exception as ex:
            print('Exception probing target: %s' % ex)


def _main():
    try:
        main()
    except psdb.ProbeException as e:
        print(e)
        sys.exit(1)


if __name__ == '__main__':
    _main()
