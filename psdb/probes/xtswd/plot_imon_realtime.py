#!/usr/bin/env python3
# Copyright (c) 2022 Phase Advanced Sensor Systems, Inc.
import argparse
import threading
import bisect
import time
import sys

import btype

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

import psdb.probes


matplotlib.rcParams['lines.linewidth'] = 1
matplotlib.rcParams['lines.markersize'] = 1


# Approximate ADC-to-mA ratio for prototype board.
MA_RATIO = 11.047

F_MUL    = None

MA_PLOT  = None
MA_LOCK  = threading.Lock()
MA_Y     = []
MA_GEN   = 0
MA_DISP  = 0
RUNNING  = True
ANI      = None


class Header(btype.Struct):
    sig             = btype.uint32_t(0x4e4f4d49)
    freq_num        = btype.uint32_t()
    freq_denom      = btype.uint32_t()
    oversample_log2 = btype.uint8_t()
    rsrv            = btype.Array(btype.uint8_t(), 3)
    _EXPECTED_SIZE  = 16


def make_plot(i_max):
    global MA_PLOT

    fig = plt.figure(figsize=(12.5, 7))
    fig.suptitle('Current Consumption')

    ax = fig.add_subplot(111)
    ax.set_xlim(-15, 5)
    ax.set_ylim(0, i_max)
    ax.set_ylabel('mA')
    ax.set_xlabel('Time')
    ax.format_coord = lambda x, y: 'T=%.10f, mA=%.10f' % (x, y)

    MA_PLOT = ax.plot([], [])[0]

    return fig


def update_plot(_frame):
    global MA_DISP

    with MA_LOCK:
        if MA_GEN == MA_DISP:
            return

        ma_y    = MA_Y[:]
        MA_DISP = MA_GEN

    ts    = [i * F_MUL for i in range(1 - len(ma_y), 1)]
    index = bisect.bisect_left(ts, -10)
    ma_y  = ma_y[index:]
    ts    = ts[index:]
    MA_PLOT.set_data(ts, ma_y)


def read_thread(rv, probe):
    global MA_GEN
    global MA_Y
    global F_MUL

    # Put the target in reset if requested.
    if rv.srst:
        probe.assert_srst()
        time.sleep(0.001)

    # Enable the INA and give it time to self-cal and warm up.
    probe.enable_instrumentation_amp()
    time.sleep(0.5)

    # Start current monitoring while in reset.
    probe.start_current_monitoring()

    # TODO: Should do some monitoring here before releasing SRST.

    # Release the target from reset if requested.
    if rv.srst:
        probe.deassert_srst()

    last_seq = -1
    while RUNNING:
        idata, data = probe.read_current_monitor_data()

        if idata.seq - last_seq != 1:
            print('**** Missed %u buffers ****' % (idata.seq - last_seq - 1))
        last_seq = idata.seq

        F_MUL = idata.freq_denom / idata.freq_num
        freq = idata.freq_num / idata.freq_denom
        print('IMon %u: %ux oversample, %s Hz, %u bytes' %
              (idata.seq, 1 << idata.oversample_log2, freq, len(data)))

        ovr  = (1 << idata.oversample_log2)
        vals = [v / ovr for v in idata.samples]
        vals = [v / MA_RATIO for v in vals]
        with MA_LOCK:
            MA_GEN += 1
            MA_Y   += vals


def main(rv):
    global RUNNING
    global ANI

    # Dump all debuggers if requested.
    if rv.dump_debuggers:
        psdb.probes.dump_probes()

    # Find the target probe.
    probe = psdb.probes.xtswd.make_one_ns(rv)

    # Make the plot.
    fig = make_plot(rv.i_max)

    # Start the read thread.
    t = threading.Thread(target=read_thread, args=(rv, probe))
    t.start()

    # Display the graph.
    ANI = FuncAnimation(fig, update_plot, frames=range(1), blit=False,
                        interval=1000)
    plt.show()

    RUNNING = False
    t.join()


def _main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dump-debuggers', '-d', action='store_true')
    parser.add_argument('--usb-path')
    parser.add_argument('--serial-num')
    parser.add_argument('--srst', action='store_true')
    parser.add_argument('--i-max', type=float, default=100)
    rv = parser.parse_args()

    try:
        main(rv)
    except psdb.ProbeException as e:
        print(e)
        sys.exit(1)


if __name__ == '__main__':
    _main()
