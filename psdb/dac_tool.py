#!/usr/bin/env python3
# Copyright (c) 2020 Phase Advanced Sensor Systems, Inc.
import psdb.probes

import argparse
import sys


def autoint(v):
    return int(v, 0)


def main(rv):
    # Validate DAC values.
    if rv.singen < 0 or rv.singen > 0x0FFF:
        raise Exception('--singen out of range')
    if rv.bias < 0 or rv.bias > 0x0FFF:
        raise Exception('--bias out of range')

    # Dump all debuggers if requested.
    if rv.dump_debuggers:
        psdb.probes.dump_probes()

    # Probe the specified serial number (or find the default if no serial number
    # was specified.
    probe = psdb.probes.find_default(usb_path=rv.usb_path)
    f     = probe.set_tck_freq(rv.probe_freq)
    print('Probing with SWD frequency at %.3f MHz' % (f/1.e6))

    # SRST the target, if requested.  We have to assert this for at least 1 us.
    if rv.srst:
        probe.srst_target()

    # Use the probe to detect a target platform.
    target = probe.probe(verbose=rv.verbose,
                         connect_under_reset=rv.connect_under_reset)
    f      = target.set_max_tck_freq()
    print('Set SWD frequency to %.3f MHz' % (f/1.e6))

    # Find the RCC and DAC devices.
    rcc = target.devs['RCC_M7']
    dac = target.devs['DAC1']

    # Enable both DAC channels.
    rcc.enable_device('DAC1')
    dac._CR      = 0x00000000
    dac._MCR     = 0x00020002
    dac._CR      = 0x00010001
    dac._DHR12RD = (rv.singen << 16) | (rv.bias << 0)


def _main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dump-debuggers', '-d', action='store_true')
    parser.add_argument('--usb-path')
    parser.add_argument('--halt', action='store_true')
    parser.add_argument('--srst', action='store_true')
    parser.add_argument('--connect-under-reset', action='store_true')
    parser.add_argument('--probe-freq', type=int, default=1000000)
    parser.add_argument('--verbose', '-v', action='store_true')
    parser.add_argument('--singen', '-s', type=autoint, default=0x0800)
    parser.add_argument('--bias', '-b', type=autoint, default=0x0800)
    rv = parser.parse_args()

    try:
        main(rv)
    except psdb.ProbeException as e:
        print(e)
        sys.exit(1)


if __name__ == '__main__':
    _main()
