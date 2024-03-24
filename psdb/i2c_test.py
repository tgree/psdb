#!/usr/bin/env python3
# Copyright (c) 2023 Phase Advanced Sensor Systems, Inc.
import argparse
import time
import sys

import psdb.probes


def main(rv):  # noqa: C901
    # Probe the specified serial number (or find the default if no serial number
    # was specified.
    probe = psdb.probes.make_one_ns(rv)

    # Use the probe to detect a target platform.
    f = probe.set_tck_freq(rv.probe_freq)
    print('Probing with SWD frequency at %.3f MHz' % (f/1.e6))
    target = probe.probe(verbose=rv.verbose, connect_under_reset=True)
    f      = probe.set_max_target_tck_freq()
    print('Set SWD frequency to %.3f MHz' % (f/1.e6))

    # Find the RCC device.
    rcc = target.devs['RCC']

    # Configure PB8 and PB3 as I2C1 devices, with pullups enabled.
    rcc.enable_device('GPIOB')
    gpiob = target.devs['GPIOB']
    gpiob._PUPDR.PUPD3 = 1
    gpiob._PUPDR.PUPD8 = 1
    gpiob._OTYPER.OT3  = 1
    gpiob._OTYPER.OT8  = 1
    gpiob._MODER.MODE3 = 2
    gpiob._MODER.MODE8 = 2
    gpiob._AFRL.AFSEL3 = 4
    gpiob._AFRH.AFSEL8 = 4

    # Configure PB9 as a GPIO, which we will use to control power to the
    # external RTC.  Leave it low for now, so power is disabled.
    gpiob._PUPDR.PUPD9 = 0
    gpiob._OTYPER.OT9  = 0
    gpiob._ODR.OD9     = 0
    gpiob._MODER.MODE9 = 1

    # Enable the I2C kernel clock as SYSCLK
    rcc._CCIPR1.I2C1SEL = 1

    # Enable the I2C peripheral clock.
    rcc.enable_device('I2C1')

    # Configure noise filters before setting PE.
    i2c = target.devs['I2C1']
    i2c._CR1.ANFOFF = 0
    i2c._CR1.DNF = 15

    # Configure timing parameters before setting PE.  These are taken from
    # the manual, only using an I2C fCLK of 4 MHz instead of 8 MHz, so we
    # change PRESC to 0 instead of 1.
    i2c._TIMINGR.PRESC  = 0
    i2c._TIMINGR.SCLDEL = 4
    i2c._TIMINGR.SDADEL = 2
    i2c._TIMINGR.SCLH   = 0xC3
    i2c._TIMINGR.SCLL   = 0xC7

    # Enable the peripheral.
    i2c._CR1.PE = 1

    # Delay briefly before enabling power to the RTC.
    time.sleep(0.1)

    # Enable the RTC and delay briefly before trying to talk to it.
    print('Enabling external RTC...')
    gpiob._ODR.OD9 = 1
    time.sleep(0.005)

    # Read all registers.
    # Loop forever.
    print('Press Ctrl-C to exit.')
    while True:
        data = i2c.i2c_read(0x68, 20)
        print(data)
        time.sleep(1)


def _main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--usb-path')
    parser.add_argument('--serial-num')
    parser.add_argument('--probe-freq', type=int, default=1000000)
    parser.add_argument('--max-tck-freq', type=int)
    parser.add_argument('--verbose', '-v', action='store_true')
    rv = parser.parse_args()

    try:
        main(rv)
    except KeyboardInterrupt:
        print()
    except psdb.ProbeException as e:
        print(e)
        sys.exit(1)


if __name__ == '__main__':
    _main()
