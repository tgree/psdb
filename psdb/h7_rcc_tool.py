#!/usr/bin/env python3
# Copyright (c) 2020 Phase Advanced Sensor Systems, Inc.
import psdb.probes

import argparse
import sys


def main(rv):
    # Validate DAC values.

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

    # Find the RCC.
    rcc = target.devs['RCC_M7']
    print('      f_csi: %7.3f MHz' % (rcc.f_csi / 1e6))
    print('      f_hsi: %7.3f MHz' % (rcc.f_hsi / 1e6))
    print('   f_pllsrc: %7.3f MHz' % (rcc.f_pllsrc / 1e6))
    print('   f_sysclk: %7.3f MHz' % (rcc.f_sysclk / 1e6))

    # Measure the HSE to the nearest 1 MHz and assign it in the RCC.
    f_hse = target.enable_and_measure_hse()
    print('      f_hse: %7.3f MHz' % (f_hse / 1e6))
    f_hse = ((f_hse + 500000) // 1000000) * 1000000
    rcc.set_f_hse(f_hse)

    # Figure out how to get the PLL to the target MHz using the HSE.
    M, N, P, vos = rcc.get_pll_mnpv(rv.target_mhz, f_hse)
    print('f_pll1_p_ck: %7.3f MHz (M=%u, N=%u, P=%u, VOS%u)' %
          ((f_hse * N / (M * P)) / 1e6, M, N, P, vos))


def _main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dump-debuggers', '-d', action='store_true')
    parser.add_argument('--usb-path')
    parser.add_argument('--halt', action='store_true')
    parser.add_argument('--srst', action='store_true')
    parser.add_argument('--connect-under-reset', action='store_true')
    parser.add_argument('--probe-freq', type=int, default=1000000)
    parser.add_argument('--verbose', '-v', action='store_true')
    parser.add_argument('--target-mhz', '-t', type=int, default=480)
    rv = parser.parse_args()

    try:
        main(rv)
    except psdb.ProbeException as e:
        print(e)
        sys.exit(1)


if __name__ == '__main__':
    _main()
