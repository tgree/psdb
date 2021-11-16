#!/usr/bin/env python3
# Copyright (c) 2018-2021 Phase Advanced Sensor Systems, Inc.
import argparse
import sys
import time
import curses

import psdb.probes
import tgcurses
import tgcurses.ui

from .cpu_register_window import CPURegisterWindow
from .device_register_window import DeviceRegisterWindow
from .memory_window import MemoryWindow
from .device_selector_window import DeviceSelectorWindow


STATUS_TIMEOUT = 1

DEV_TYPE_REGISTER = 0
DEV_TYPE_MEMORY   = 1


def get_dev_type(dev):
    if dev.regs:
        return DEV_TYPE_REGISTER
    elif hasattr(dev, 'size'):
        return DEV_TYPE_MEMORY
    raise Exception('Unknown device type!')


class InspectTool:
    def __init__(self, target, workspace):
        self.target      = target
        self.workspace   = workspace
        self.status_time = None

        # Build the device list, including global devices and per-CPU devices
        # and then sort it by address.
        devs = list(target.devs.values())
        for c in target.cpus:
            devs += list(c.devs.values())
        self.devs      = sorted(devs, key=lambda d: d.dev_base)
        self.dev_names = ['%08X %s' % (d.dev_base, d.path) for d in self.devs]

        # Extract name info.
        self.max_reg_name = max(len(r.name) for d in self.devs for r in d.regs)
        self.max_dev_name = max(len(dn) for dn in self.dev_names)

        # Add CPU windows.
        self.cpu_wins = []
        for i, c in enumerate(self.target.cpus):
            if i == 0:
                le = self.workspace.canvas
            else:
                le = self.cpu_wins[-1].window
            self.cpu_wins.append(CPURegisterWindow(self, le, i, c))
            self.cpu_wins[-1].draw()

        # Add a device register window.
        self.reg_win = DeviceRegisterWindow(self, self.cpu_wins[-1].window)

        # Add a memory window.
        self.mem_win = MemoryWindow(self, self.cpu_wins[-1].window)

        # Add a device selector window.
        self.dev_win = DeviceSelectorWindow(self)

        # Focus handling.
        self.focus_list = [self.dev_win,
                           self.reg_win,
                           self.reg_win.decode_win,
                           self.mem_win,
                           ]

    def status(self, s):
        y = self.workspace.canvas.height - 1
        self.workspace.canvas.clrline(y)
        if s:
            self.workspace.canvas.addstr('%s' % s, pos=(y, 1),
                                         attr=curses.A_REVERSE)
            self.status_time = time.time()
        self.workspace.canvas.noutrefresh()

    def handle_device_selected(self, d):
        dt = get_dev_type(d)
        if dt == DEV_TYPE_REGISTER:
            self.mem_win.hide()
            self.reg_win.set_dev(d)
        elif dt == DEV_TYPE_MEMORY:
            self.reg_win.hide()
            self.mem_win.set_mem(d)

    def event_loop(self):
        # Draw the first device.
        self.handle_device_selected(self.dev_win.get_selected_dev())

        # Handle user input.
        tgcurses.ui.curs_set(0)
        self.workspace.canvas.timeout(100)
        self.workspace.canvas.keypad(1)
        self.focus_list[0].focus_gained()
        while True:
            # Clear status text if it has expired.
            if self.status_time is not None:
                if time.time() - self.status_time >= STATUS_TIMEOUT:
                    self.status(None)

            # Draw the current device contents.
            if self.mem_win.is_visible():
                self.mem_win.draw()
            elif self.reg_win.is_visible():
                self.reg_win.draw()

            # Let the focus window draw the cursor.
            self.focus_list[0].focus_draw_cursor()

            # Update the screen.
            tgcurses.ui.doupdate()

            # Get the next command.
            c = self.workspace.canvas.getch()
            if c == ord('q'):
                break
            elif c in (ord('\t'), curses.KEY_BTAB):
                self.focus_list[0].focus_lost()

                while True:
                    if c == ord('\t'):
                        self.focus_list.append(self.focus_list.pop(0))
                    else:
                        self.focus_list.insert(0, self.focus_list.pop())
                    if (self.focus_list[0].is_visible() and
                            self.focus_list[0].can_focus()):
                        break

                self.focus_list[0].focus_gained()
            else:
                self.focus_list[0].handle_ch(c)


def main(screen, args):  # noqa: C901
    # Extract args.
    t = args.target

    # Initialize colors.
    curses.use_default_colors()
    curses.init_pair(1, -1, curses.COLOR_GREEN)

    # Create a workspace.
    ws = tgcurses.ui.Workspace(screen)

    # Create the inspect tool.
    it = InspectTool(t, ws)
    it.event_loop()


def _main():
    # Parse arguments first.
    parser = argparse.ArgumentParser()
    parser.add_argument('--dump-debuggers', '-d', action='store_true')
    parser.add_argument('--usb-path')
    parser.add_argument('--probe-freq', type=int, default=1000000)
    parser.add_argument('--verbose', '-v', action='store_true')
    parser.add_argument('--srst', action='store_true')
    parser.add_argument('--connect-under-reset', action='store_true')
    parser.add_argument('--resume', '-r', action='store_true')
    args = parser.parse_args()

    # Find a debug probe.
    try:
        args.probe = psdb.probes.find_default(usb_path=args.usb_path)
    except psdb.ProbeException as e:
        print(e)
        sys.exit(1)

    # Set the target-probing frequency.
    args.probe.set_tck_freq(args.probe_freq)

    # Reset the target if requested.
    if args.srst:
        args.probe.srst_target()

    # Probe the target platform.
    args.target = args.probe.probe(verbose=args.verbose,
                                   connect_under_reset=args.connect_under_reset)

    # Set the max clock frequency.
    args.target.set_max_tck_freq()

    # Interact with the UI.
    tgcurses.wrapper(main, args)

    # Resume the target.
    if args.resume:
        args.target.resume()


if __name__ == '__main__':
    _main()
