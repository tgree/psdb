#!/usr/bin/env python3
# Copyright (c) 2018-2022 Phase Advanced Sensor Systems, Inc.
import psdb.probes
import usb.core

import argparse
import threading
import time
import sys

from struct import unpack_from


def process_synchronization_data(data):
    for i, v in enumerate(data):
        if v:
            assert i >= 5
            return data[i:]

    return data


def process_source_data(data):
    size = data[0] & 3
    if size == 3:
        size = 4
    if len(data) < size + 1:
        return data

    addr               = (data[0] >> 3) & 0x1F
    is_instrumentation = ((data[0] & 4) == 0)
    if size == 1:
        payload = unpack_from('<B', data, 1)[0]
    elif size == 2:
        payload = unpack_from('<H', data, 1)[0]
    elif size == 4:
        payload = unpack_from('<I', data, 1)[0]

    if is_instrumentation:
        prefix = 'INST'
    else:
        prefix = 'HARD'
    if size == 1:
        print('%s[%u]: 0x%02X' % (prefix, addr, payload))
    elif size == 2:
        print('%s[%u]: 0x%04X' % (prefix, addr, payload))
    elif size == 4:
        print('%s[%u]: 0x%08X' % (prefix, addr, payload))

    return data[size + 1:]


def process_protocol_data(data):
    pass


def process_trace_data(data):
    while data:
        rem = len(data)

        if data[0] == 0x00:
            data = process_synchronization_data(data)
        elif data[0] & 3:
            data = process_source_data(data)
        else:
            data = process_protocol_data(data)

        if len(data) == rem:
            break

    return data


POLL_ACTIVE = True
def poll_thread(probe):
    data = b''
    while POLL_ACTIVE:
        try:
            new_data = probe.trace_read(timeout=100)
            if new_data:
                data = process_trace_data(data + new_data)
            else:
                time.sleep(0.01)
        except usb.core.USBTimeoutError:
            pass


def main(rv):  # noqa: C901
    global POLL_ACTIVE

    # Dump all debuggers if requested.
    if rv.dump_debuggers:
        psdb.probes.dump_probes()

    # Sanity on the prescaler.
    prescaler   = round(rv.traceclkin_freq / rv.swo_freq)
    output_freq = rv.traceclkin_freq / prescaler
    deviation   = abs(output_freq - rv.swo_freq) / rv.swo_freq
    print('Prescaler of %u has a deviation of %.1f%%.' %
          (prescaler, 100*deviation))
    if deviation > 0.03:
        raise Exception('Frequency deviation too large!')

    # Probe the specified serial number (or find the default if no serial number
    # was specified.
    probe = psdb.probes.find_default(usb_path=rv.usb_path)
    assert rv.swo_freq <= probe.max_swo_freq
    f     = probe.set_tck_freq(rv.probe_freq)
    print('Resetting and probing with SWD frequency at %.3f MHz...' % (f/1.e6))

    # Use the probe to detect a target platform.
    target = probe.probe(verbose=rv.verbose, connect_under_reset=True)
    f      = target.set_max_tck_freq()
    print('Set SWD frequency to %.3f MHz.' % (f/1.e6))

    # Flush trace before we start the MCU.
    probe.trace_flush(rv.swo_freq)

    # As a consequence of pre-probing, we have enabled the DBGMCU debug clocks,
    # which will allow us to later configure trace even if the MCU is asleep.
    # Start it up.
    print('Starting MCU...')
    target.resume()

    # Delay until we are ready to start recording trace.
    input('Press Enter to begin tracing once MCU is ready. ')
    probe.trace_enable(rv.swo_freq)
    print('Starting SWO with a prescaler of %u.' % prescaler)
    target.start_swo_trace(prescaler)
    target.disable_debug_clocks()

    # Read and dump trace.
    POLL_ACTIVE = True
    t = threading.Thread(target=poll_thread, args=(probe,))
    t.start()
    try:
        while True:
            time.sleep(1)
    finally:
        POLL_ACTIVE = False
        t.join()
        probe.trace_disable()


def _main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dump-debuggers', '-d', action='store_true')
    parser.add_argument('--usb-path')
    parser.add_argument('--probe-freq', type=int, default=1000000)
    parser.add_argument('--swo-freq', type=int, default=2000000,
                        help='frequency at which to run the debug probe UART')
    parser.add_argument('--traceclkin-freq', type=int, required=True,
                        help=('frequency of the clock driving the TPIU '
                              '(typically the CPU frequency)'))
    parser.add_argument('--verbose', '-v', action='store_true')
    rv = parser.parse_args()

    try:
        main(rv)
    except psdb.ProbeException as e:
        print(e)
        sys.exit(1)


if __name__ == '__main__':
    _main()
