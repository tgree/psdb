#!/usr/bin/env python3
# Copyright (c) 2018-2019 Phase Advanced Sensor Systems, Inc.
import psdb.probes

import sys


def main():
    for p in psdb.probes.get_probes():
        p.show_info()
        p.probe(verbose=True).resume()


def _main():
    try:
        main()
    except psdb.ProbeException as e:
        print(e)
        sys.exit(1)


if __name__ == '__main__':
    _main()
