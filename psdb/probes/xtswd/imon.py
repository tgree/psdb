#!/usr/bin/env python3
# Copyright (c) 2022 Phase Advanced Sensor Systems, Inc.
import argparse
import time
import sys

import btype
import psdb.probes


HDR      = None
LAST_SEQ = -1


class Header(btype.Struct):
    sig             = btype.uint32_t(0x4e4f4d49)
    freq_num        = btype.uint32_t()
    freq_denom      = btype.uint32_t()
    oversample_log2 = btype.uint8_t()
    rsrv            = btype.Array(btype.uint8_t(), 3)
    _EXPECTED_SIZE  = 16


def read_data(f, probe, timeout=None):
    global HDR
    global LAST_SEQ

    if timeout is None:
        timeout = 100000000000000

    t0 = time.time()
    while time.time() - t0 < timeout:
        idata, data = probe.read_current_monitor_data()
        if HDR is None:
            HDR = Header(freq_num=idata.freq_num,
                         freq_denom=idata.freq_denom,
                         oversample_log2=idata.oversample_log2)
            f.write(HDR.pack())
        f.write(data)

        if idata.seq - LAST_SEQ != 1:
            print('**** Missed %u buffers ****' % (idata.seq - LAST_SEQ - 1))
        LAST_SEQ = idata.seq

        freq = idata.freq_num / idata.freq_denom
        print('IMon %u: %ux oversample, %s Hz, %u bytes' %
              (idata.seq, 1 << idata.oversample_log2, freq, len(data)))


def main(rv):
    # Dump all debuggers if requested.
    if rv.dump_debuggers:
        psdb.probes.dump_probes()

    # If no dump file was specified, we are done.
    if not rv.dump_file:
        return

    # Find the target probe.
    probe = psdb.probes.xtswd.make_one_ns(rv)

    with open(rv.dump_file, 'wb') as f:
        # Put the target in reset if requested.
        if rv.srst:
            probe.assert_srst()
            time.sleep(0.001)

        # Enable the INA and give it time to self-cal and warm up.
        probe.enable_instrumentation_amp()
        time.sleep(0.5)

        # Start current monitoring while in reset.
        probe.start_current_monitoring()
        read_data(f, probe, timeout=1)

        # Release the target from reset if requested.
        if rv.srst:
            probe.deassert_srst()

        # Monitor indefinitely.
        read_data(f, probe)


def _main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dump-debuggers', '-d', action='store_true')
    parser.add_argument('--usb-path')
    parser.add_argument('--serial-num')
    parser.add_argument('--srst', action='store_true')
    parser.add_argument('--dump-file')
    rv = parser.parse_args()

    try:
        main(rv)
    except psdb.ProbeException as e:
        print(e)
        sys.exit(1)


if __name__ == '__main__':
    _main()
