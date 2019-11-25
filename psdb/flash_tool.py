#!/usr/bin/env python3
# Copyright (c) 2018-2019 Phase Advanced Sensor Systems, Inc.
import psdb.probes
import psdb.elf

import argparse
import sys


def main(rv):
    # Dump all debuggers if requested.
    if rv.dump_debuggers:
        for p in psdb.probes.PROBES:
            p.show_info()

    # Probe the specified serial number (or find the default if no serial number
    # was specified.
    probe = psdb.probes.find_default(usb_path=rv.usb_path)
    f     = probe.set_tck_freq(rv.probe_freq)
    print('Probing with SWD frequency at %.3f MHz' % (f/1.e6))

    # SRST the target, if requested.  We have to assert this for at least 1 us.
    if rv.srst:
        probe.srst_target()

    # Use the probe to detect a target platform.
    target = probe.probe(verbose=rv.verbose)
    f      = target.set_max_tck_freq()
    print('Set SWD frequency to %.3f MHz' % (f/1.e6))

    # Flash info if verbose.
    if rv.verbose:
        print('       Flash size: %u' % target.flash.flash_size)
        print('Flash sector size: %u' % target.flash.sector_size)

    # Read a backup of flash if requested.
    if rv.read_flash:
        with open(rv.read_flash, 'wb') as f:
            f.write(target.flash.read_all())

    # Erase the flash if requested.
    if rv.erase:
        target.flash.erase_all()
        target.reset_halt()

    # Write a new image to flash if requested.
    if rv.flash:
        target.flash.burn_elf(psdb.elf.ELFBinary(rv.flash))
        target.reset_halt()

    # Resume if halt wasn't requested.
    if not rv.halt:
        target.resume()

    # Dump some memory.
    if rv.mem_dump:
        print('Memory dump:')
        base, length = rv.mem_dump.split(',')
        base         = int(base, 0)
        length       = int(length, 0)
        mem          = target.cpus[0].read_bulk(base, length)
        psdb.hexdump(mem, addr=base)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dump-debuggers', '-d', action='store_true')
    parser.add_argument('--usb-path')
    parser.add_argument('--halt', action='store_true')
    parser.add_argument('--srst', action='store_true')
    parser.add_argument('--read-flash')
    parser.add_argument('--flash')
    parser.add_argument('--erase', action='store_true')
    parser.add_argument('--mem-dump', '-m')
    parser.add_argument('--probe-freq', type=int, default=1000000)
    parser.add_argument('--verbose', '-v', action='store_true')
    rv = parser.parse_args()

    try:
        main(rv)
    except psdb.probes.Exception as e:
        print(e)
        sys.exit(1)
