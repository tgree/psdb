#!/usr/bin/env python3
# Copyright (c) 2018-2019 Phase Advanced Sensor Systems, Inc.
import psdb.probes
import psdb.devices
import psdb.elf

import argparse
import struct
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

    # Use the probe to detect a target platform.
    target = probe.probe(verbose=rv.verbose, connect_under_reset=False)
    f      = target.set_max_tck_freq()
    print('Set SWD frequency to %.3f MHz' % (f/1.e6))

    # Generate the core file.
    c = psdb.elf.Core()

    # Iterate over all devices to get memory and peripheral registers.
    for d in target.devs.values():
        if isinstance(d, psdb.devices.MemDevice):
            print('Adding "%s"...' % d.name)
            c.add_mem_map(d.dev_base, d.read_mem_block(d.dev_base, d.size))
        elif rv.peripheral_capture:
            print('Adding "%s"...' % d.name)
            region_data = b''
            for r in d.regs:
                # Skip aliased registers.  For instance, GPT16x1 has CCMR1_I
                # and CCMR1_O both at address 0x18 for use in inspect_tool.
                if r.offset < len(region_data):
                    continue

                assert r.size == 4
                pad          = r.offset - len(region_data)
                region_data += b'\xCA'*pad
                if (r.flags & r.READABLE):
                    region_data += struct.pack('<L', r.read(d))
                else:
                    region_data += struct.pack('<L', 0xCACACACA)

            if region_data:
                c.add_mem_map(d.dev_base, region_data)

    # Iterate over all CPUs to get CPU registers.
    for cpu in target.cpus:
        r    = cpu.read_core_registers()
        regs = [r['r0'], r['r1'], r['r2'], r['r3'], r['r4'], r['r5'], r['r6'],
                r['r7'], r['r8'], r['r9'], r['r10'], r['r11'], r['r12'],
                r['sp'], r['lr'], r['pc'], r['xpsr']]
        c.add_thread(regs)

    # Write it out.
    c.write(rv.output_path)

    # Resume if halt wasn't requested.
    if not rv.halt:
        target.resume()


def _main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dump-debuggers', '-d', action='store_true')
    parser.add_argument('--usb-path')
    parser.add_argument('--halt', action='store_true')
    parser.add_argument('--probe-freq', type=int, default=1000000)
    parser.add_argument('--verbose', '-v', action='store_true')
    parser.add_argument('--output-path', '-o', required=True)
    parser.add_argument('--peripheral-capture', '-p', action='store_true')
    rv = parser.parse_args()

    try:
        main(rv)
    except psdb.ProbeException as e:
        print(e)
        sys.exit(1)


if __name__ == '__main__':
    _main()
