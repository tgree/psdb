#!/usr/bin/env python3
# Copyright (c) 2020 Phase Advanced Sensor Systems, Inc.
import psdb.probes

import argparse
import sys


def main(rv):
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

    # Find the necessary devices.
    rcc   = target.devs['RCC_M7']
    pe    = target.devs['GPIOE']
    tim15 = target.devs['TIM15']

    # Switch to HSE.
    rcc.enable_hse()
    rcc.set_sysclock_source(2)

    # Enable PE5 as TIM15_CH1.
    rcc.enable_device('GPIOE')
    pe._AFRL.AFSEL5     = 4
    pe._MODER.MODE5     = 2
    pe._OTYPER.OT5      = 0
    pe._OSPEEDR.OSPEED5 = 3
    pe._PUPDR.PUPD5     = 0

    # Configure TIM15 to toggle at 1/1000th the CPU frequency.
    rcc.enable_device('TIM15')
    tim15._SMCR  = 0
    tim15._CCER  = 0
    tim15._CR1   = 0
    ccmr         = tim15._CCMR1.read()
    ccmr        &= ~0x00010070
    ccmr        |= 0x00000030
    tim15._CCMR1 = ccmr
    tim15._CCR1  = 0
    tim15._CCER  = 0x00000001
    tim15._CR1   = 0
    tim15._PSC   = 0
    tim15._ARR   = (1000 // 2) - 1
    tim15._CNT   = 0
    tim15._BDTR  = 0x00008000
    tim15._CR1   = 0x00000001


def _main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dump-debuggers', '-d', action='store_true')
    parser.add_argument('--usb-path')
    parser.add_argument('--halt', action='store_true')
    parser.add_argument('--srst', action='store_true')
    parser.add_argument('--connect-under-reset', action='store_true')
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
