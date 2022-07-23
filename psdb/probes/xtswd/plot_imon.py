#!/usr/bin/env python3
# Copyright (c) 2021-2022 by Phase Advanced Sensor Systems, Inc.
# All rights reserved.
import argparse
import struct

import matplotlib
import matplotlib.pyplot as plt

from .imon import Header


matplotlib.rcParams['lines.linewidth'] = 1
matplotlib.rcParams['lines.markersize'] = 1


class Point:
    def __init__(self, t, v):
        self.t = t
        self.v = v


# Approximate ADC-to-mA ratio for prototype board.
# TODO: Get this from calibration flash.
MA_RATIO = 11.047


def interpolate_color(begin, end, p):
    return (p*end[0] + (1-p)*begin[0],
            p*end[1] + (1-p)*begin[1],
            p*end[2] + (1-p)*begin[2])


def plot_imon_data(plots, labels, i_max, t_max):
    # Make the plot
    fig = plt.figure(figsize=(12.5, 7))
    fig.suptitle('Current Consumption')

    # Do the time plot.
    ax = fig.add_subplot(111)
    ax.set_xlim(0, t_max)
    ax.set_ylim(0, i_max)
    ax.set_ylabel('mA')
    ax.set_xlabel('Time')
    ax.format_coord = lambda x, y: 'T=%.10f, mA=%.10f' % (x, y)

    # Add data points from each file.
    white_color   = (1., 1., 1.)
    newest_color  = (0, 0.25, 0.5)
    for i, points in enumerate(plots):
        color = interpolate_color(white_color, newest_color, (i + 1)/len(plots))
        ts   = [p.t for p in points]
        vals = [p.v for p in points]
        ax.plot(ts, vals, label=labels[i], color=color)
    ax.legend()

    # Display the plot.
    plt.show()


def main(rv):
    plots = []
    t_max = 0
    for fname in rv.imon_files:
        fname, _, tdelta = fname.partition(':')
        if tdelta:
            tdelta = float(tdelta)
        else:
            tdelta = 0
        with open(fname, 'rb') as f:
            data = f.read()
        hdr  = Header.unpack(data[:Header._STRUCT.size])
        data = data[Header._STRUCT.size:]
        f    = hdr.freq_num / hdr.freq_denom
        ovr  = (1 << hdr.oversample_log2)

        vals = struct.unpack('<%uH' % (len(data) // 2), data)
        vals = [v / ovr for v in vals]
        print('%s: Iavg ADC = %s' % (fname, sum(vals) / len(vals)))
        vals = [v / MA_RATIO for v in vals]
        ts   = [i * hdr.freq_denom / hdr.freq_num for i in range(len(vals))]
        t_max = max(t_max, ts[-1])

        points = [Point(t + tdelta, v) for t, v in zip(ts, vals)]
        plots.append(points)

    plot_imon_data(plots, rv.imon_files, rv.i_max, t_max)


def _main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--i-max', type=float, default=100)
    parser.add_argument('imon_files', nargs='+')
    rv = parser.parse_args()

    try:
        main(rv)
    except KeyboardInterrupt:
        print()


if __name__ == '__main__':
    _main()
