#!/usr/bin/env python3
# Copyright (c) 2018-2019 Phase Advanced Sensor Systems, Inc.
import argparse
import sys

import psdb.probes
import psdb.devices


def main(rv):
    # Dump all debuggers if requested.
    if rv.dump_debuggers:
        psdb.probes.dump_probes()

    # Probe the specified serial number (or find the default if no serial number
    # was specified.
    probe = psdb.probes.make_one_ns(rv)
    f     = probe.set_tck_freq(rv.probe_freq)
    print('Probing with SWD frequency at %.3f MHz' % (f/1.e6))

    # Use the probe to detect a target platform.
    target = probe.probe(verbose=rv.verbose, connect_under_reset=False)
    f      = probe.set_max_target_tck_freq()
    print('Set SWD frequency to %.3f MHz' % (f/1.e6))

    # Iterate over all devices to get peripheral registers.
    print('Dumping device registers to %s...' % rv.output_path)
    with open(rv.output_path, 'w', encoding='utf8') as f:
        block = 0
        for d in target.devs.values():
            if isinstance(d, psdb.devices.MemDevice):
                continue

            block += 1
            if block > 1:
                f.write('\n')
            f.write('%s\n' % d.path)
            for r in d.regs:
                addr = d.dev_base + r.offset
                f.write('0x%08X: ' % addr)
                if not r.flags & r.READABLE:
                    f.write('--Wr Onl--')
                elif r.flags & r.SIDE_EFFECTS:
                    f.write('--SideFx--')
                else:
                    v    = r.read(d)
                    if r.size == 1:
                        f.write('0x%02X' % v)
                    elif r.size == 2:
                        f.write('0x%04X' % v)
                    elif r.size == 4:
                        f.write('0x%08X' % v)
                    else:
                        f.write('0x%X' % v)
                f.write(' %s\n' % r.name)

    # Resume if halt wasn't requested.
    if not rv.halt:
        target.resume()


def _main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dump-debuggers', '-d', action='store_true')
    parser.add_argument('--usb-path')
    parser.add_argument('--serial-num')
    parser.add_argument('--halt', action='store_true')
    parser.add_argument('--probe-freq', type=int, default=1000000)
    parser.add_argument('--verbose', '-v', action='store_true')
    parser.add_argument('--output-path', '-o', required=True)
    rv = parser.parse_args()

    try:
        main(rv)
    except psdb.ProbeException as e:
        print(e)
        sys.exit(1)


if __name__ == '__main__':
    _main()
