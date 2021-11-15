#!/usr/bin/env python3
# Copyright (c) 2018-2021 Phase Advanced Sensor Systems, Inc.
import argparse
import sys

import psdb.probes
import tgcurses
import tgcurses.ui

from .cpu_register_window import CPURegisterWindow
from .device_register_window import DeviceRegisterWindow
from .memory_window import MemoryWindow
from .device_selector_window import DeviceSelectorWindow


def main(screen, args):  # noqa: C901
    # Extract args.
    t = args.target

    # Get the device list.
    devs = list(t.devs.values())
    for c in t.cpus:
        devs += list(c.devs.values())

    # Parse it.
    devs = sorted(devs, key=lambda d: d.dev_base)

    # Create a workspace.
    ws = tgcurses.ui.Workspace(screen)

    # Add CPU windows.
    cpu_wins = []
    for i, c in enumerate(t.cpus):
        if i == 0:
            la = ws.canvas.frame.left_anchor()
        else:
            la = cpu_wins[-1].frame.right_anchor()
        cpu_wins.append(CPURegisterWindow(i, c, ws, la))
        cpu_wins[-1].draw()

    # Add a device register window.
    reg_win = DeviceRegisterWindow(devs, ws,
                                   cpu_wins[-1].window.frame.right_anchor())

    # Add a memory window.
    mem_win = MemoryWindow(ws, cpu_wins[-1].window.frame.right_anchor())

    # Add a device selector window.
    dev_win = DeviceSelectorWindow(devs, reg_win, mem_win, ws)

    # Handle user input.
    focus_list = [dev_win, reg_win, mem_win]
    tgcurses.ui.curs_set(0)
    ws.canvas.timeout(100)
    ws.canvas.keypad(1)
    while True:
        tgcurses.ui.doupdate()
        c = ws.canvas.getch()
        if c == ord('q'):
            break
        elif c == ord('\t'):
            f = focus_list.pop(0)
            f.focus_lost()
            focus_list.append(f)

            while not focus_list[0].is_visible():
                focus_list.append(focus_list.pop(0))

            focus_list[0].focus_gained()
        else:
            focus_list[0].handle_ch(c)


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
