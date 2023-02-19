#!/usr/bin/env python3
# Copyright (c) 2018-2019 Phase Advanced Sensor Systems, Inc.
import argparse
import time
import math
import sys

import psdb.probes


def main(rv):  # noqa: C901
    # Probe the specified serial number (or find the default if no serial number
    # was specified.
    probe = psdb.probes.make_one_ns(rv)
    f     = probe.set_tck_freq(rv.probe_freq)
    print('Probing with SWD frequency at %.3f MHz' % (f/1.e6))

    # Use the probe to detect a target platform.
    target = probe.probe(verbose=rv.verbose, connect_under_reset=True)
    f      = probe.set_max_target_tck_freq()
    print('Set SWD frequency to %.3f MHz' % (f/1.e6))

    # Enable the CORDIC unit.
    rcc    = target.devs['RCC']
    cordic = target.devs['CORDIC']
    rcc.enable_device('CORDIC')
    cordic._CSR = 0x00000061
    theta_fixed = 0
    while True:
        theta         = theta_fixed * 2 * math.pi / 2**32
        cordic._WDATA = theta_fixed
        sin_math      = math.sin(theta)
        sin_q1_31     = cordic._RDATA.read()
        if sin_q1_31 <= 0x7FFFFFFF:
            sin_cordic = sin_q1_31 / 0x7FFFFFFF
        else:
            sin_cordic = -(2**32 - sin_q1_31) / 0x7FFFFFFF
        print('theta_fixed 0x%08X theta %f sin_math %f sin_cordic %f' %
              (theta_fixed, theta, sin_math, sin_cordic))

        theta_fixed += 0x01000000
        time.sleep(1)


def _main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--usb-path')
    parser.add_argument('--serial-num')
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
