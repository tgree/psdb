#!/usr/bin/env python3
# Copyright (c) 2020 Phase Advanced Sensor Systems, Inc.
import argparse
import struct
import math
import sys

import psdb.probes


USE_HSE = True


def autoint(v):
    return int(v, 0)


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
    target = probe.probe(verbose=rv.verbose, connect_under_reset=True)
    f      = target.set_max_tck_freq()
    print('Set SWD frequency to %.3f MHz' % (f/1.e6))

    # Find the various devices we need.
    rcc = target.devs['RCC_M7']
    pwr = target.devs['PWR']

    # Set the PWR mode.
    pwr.set_mode_ldo()

    # Configure the RCC dividers.  Out of reset, the clocks will be as follows:
    #   SYSCLK     - 64 MHz
    #   CPU1CLK    - 64 MHz
    #   CPU2CLK    - 32 MHz
    #   AHB clocks - 32 MHz
    #   APB clocks - 16 MHz
    rcc.set_d1cpre(1)       # CPU1           - 64 MHz
    rcc.set_hpre(2)         # AHB, AXI, CPU2 - 32 MHz
    rcc.set_d1ppre(2)       # APB3           - 16 MHz
    rcc.set_d2ppre1(2)      # APB1           - 16 MHz
    rcc.set_d2ppre2(2)      # APB2           - 16 MHz
    rcc.set_d3ppre(2)       # APB4           - 16 MHz

    # Measure HSE.
    f_hse = target.enable_and_measure_hse()
    f_hse = ((f_hse + 500000) // 1000000) * 1000000
    rcc.set_f_hse(f_hse)

    # Configure for 480 MHz operation.
    print('          f_hse: %7.3f MHz' % (rcc.f_hse / 1e6))
    print('       f_sysclk: %7.3f MHz' % (rcc.f_sysclk / 1e6))
    print('f_sys_d1cpre_ck: %7.3f MHz' % (rcc.f_sys_d1cpre_ck / 1e6))
    print('         f_hclk: %7.3f MHz' % (rcc.f_hclk / 1e6))
    print('        f_pclk1: %7.3f MHz' % (rcc.f_pclk1 / 1e6))
    print('        f_pclk2: %7.3f MHz' % (rcc.f_pclk2 / 1e6))
    print('        f_pclk3: %7.3f MHz' % (rcc.f_pclk3 / 1e6))
    print('        f_pclk4: %7.3f MHz' % (rcc.f_pclk4 / 1e6))
    print('  f_timx_ker_ck: %7.3f MHz' % (rcc.f_timx_ker_ck / 1e6))
    print('  f_timy_ker_ck: %7.3f MHz' % (rcc.f_timy_ker_ck / 1e6))


def _main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dump-debuggers', '-d', action='store_true')
    parser.add_argument('--usb-path')
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
