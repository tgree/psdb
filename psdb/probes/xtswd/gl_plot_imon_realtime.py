#!/usr/bin/env python3
# Copyright (c) 2022-2024 Phase Advanced Sensor Systems, Inc.
import argparse
import threading
import sys

import numpy as np
import glotlib
import glfw

import psdb.probes


BOXCAR_N = 1


class IMonWindow(glotlib.Window):
    def __init__(self, xtswd, args):
        super().__init__(900, 700, msaa=4, name=xtswd.serial_num)

        self.xtswd      = xtswd
        self.args       = args
        self.i_plot     = self.add_plot(111, limits=(-0.1, 0, 10, args.i_max))
        self.i_steps    = self.i_plot.add_steps(X=[], Y=[])
        self.rst_line   = self.i_plot.add_vline(0, color='#80C080')
        self.pos_label  = self.add_label((0.99, 0.01), '', anchor='SE')
        self.data_lock  = threading.Lock()
        self.new_data_x = np.array([])
        self.new_data_y = np.array([])
        self.paused     = False
        self.thread     = threading.Thread(target=self.workloop)
        self.running    = True
        self.thread.start()

    def stop(self):
        self.running = False
        self.thread.join()

    def handle_mouse_moved(self, x, y):
        self.mark_dirty()

    def handle_key_press(self, key):
        if key == glfw.KEY_S:
            self.paused = not self.paused
            if self.paused:
                print('Paused.')
            else:
                print('Resumed.')

    def update_geometry(self, _t):
        updated = False

        _, _, _, data_x, data_y = self.get_mouse_pos()
        if data_x is not None:
            updated |= self.pos_label.set_text('%.10f  %.10f' %
                                               (data_x, data_y))

        X, Y = None, None
        with self.data_lock:
            if len(self.new_data_x):
                X = self.new_data_x
                Y = self.new_data_y
                self.new_data_x = np.array([])
                self.new_data_y = np.array([])

        if Y is not None:
            updated = True
            self.i_steps.append_x_y_data(X, Y)

        return updated

    def workloop(self):
        # Put the target in reset if requested.
        srst = self.args.srst

        # Enable the INA and start monitoring current.
        self.xtswd.enable_instrumentation_amp()
        # self.xtswd.set_dac_drive(1024)
        imon_settings = self.xtswd.start_current_monitoring(0x4C)
        print('  CALFACT: 0x%08X' % imon_settings.calfact)
        print('Frequency: %.3f Hz' % imon_settings.f)

        last_seq = -1
        t        = 0
        p        = 1 / imon_settings.f
        if srst:
            self.xtswd.assert_srst()
        while self.running:
            if srst and t > 0.5:
                self.xtswd.deassert_srst()
                self.rst_line.set_x_data(t)
                srst = False

            idata, Y = self.xtswd.read_current_monitor_data()

            if idata.seq - last_seq != 1:
                print('**** Missed %u buffers ****' %
                      (idata.seq - last_seq - 1))
            last_seq = idata.seq

            if self.paused:
                continue

            Y = [np.mean(Y[i*BOXCAR_N:(i + 1)*BOXCAR_N])
                 for i in range(len(Y)//BOXCAR_N)]
            X = np.arange(len(Y)) * p * BOXCAR_N + t
            t = X[-1] + p * BOXCAR_N
            with self.data_lock:
                self.new_data_x = np.concatenate((self.new_data_x, X))
                self.new_data_y = np.concatenate((self.new_data_y, Y))
            self.mark_dirty()


def main(args):
    # Dump all debuggers if requested.
    if args.dump_debuggers:
        psdb.probes.dump_probes()

    # Find the target probe.
    xtswd = psdb.probes.xtswd.make_one_ns(args)

    # Make the window.
    iw = IMonWindow(xtswd, args)

    # Interact.
    try:
        glotlib.interact()
    except KeyboardInterrupt:
        print()
    finally:
        iw.stop()


def auto_int(v):
    return int(v, 0)


def _main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dump-debuggers', '-d', action='store_true')
    parser.add_argument('--usb-path')
    parser.add_argument('--serial-num')
    parser.add_argument('--srst', action='store_true')
    parser.add_argument('--calfact', type=auto_int, default='0x4C')
    parser.add_argument('--i-max', type=float, default=45)
    args = parser.parse_args()

    try:
        main(args)
    except psdb.ProbeException as e:
        print(e)
        sys.exit(1)


if __name__ == '__main__':
    _main()
