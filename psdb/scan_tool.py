#!/usr/bin/env python3
# Copyright (c) 2018-2019 Phase Advanced Sensor Systems, Inc.
import argparse
import sys

import psdb.probes


def main(args):
    for e in psdb.probes.find():
        try:
            p = e.make_probe()
        except Exception as ex:
            e.show_info()
            print('Exception making probe: %s' % ex)
            continue

        p.show_detailed_info()
        if args.probe_targets:
            try:
                p.probe(verbose=True).resume()
            except Exception as ex:
                print('Exception probing target: %s' % ex)


def _main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--probe-targets', action='store_true')
    args = parser.parse_args()

    try:
        main(args)
    except psdb.ProbeException as e:
        print(e)
        sys.exit(1)


if __name__ == '__main__':
    _main()
