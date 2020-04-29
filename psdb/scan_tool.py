#!/usr/bin/env python3
# Copyright (c) 2018-2019 Phase Advanced Sensor Systems, Inc.
import psdb.probes

import sys


def main(rv):
    for p in psdb.probes.PROBES:
        p.show_info()
        p.probe(verbose=True).resume()


if __name__ == '__main__':
    try:
        main(None)
    except psdb.ProbeException as e:
        print(e)
        sys.exit(1)
