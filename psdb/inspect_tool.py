#!/usr/bin/env python3
# Copyright (c) 2018-2019 Phase Advanced Sensor Systems, Inc.
import argparse
import curses
import curses.ascii
import math
import sys

import psdb.probes
from psdb.targets import Reg
import tgcurses
import tgcurses.ui


def draw_cpu_registers(cpu_win, cpu):
    cpu_win.content.erase()
    regs = cpu.read_core_registers()
    y = 0
    for k, v in regs.items():
        cpu_win.content.addstr('%*s: ' % (cpu_win.content.width - 11, k),
                               pos=(y, 0), attr=curses.A_BOLD)
        cpu_win.content.addstr('%08X' % v)
        y += 1
    cpu_win.content.noutrefresh()


def draw_dev_registers(reg_win, dev):
    regs = dev.regs[:reg_win.content.height]
    if regs:
        reg_win.show()
        reg_win.content.erase()
        max_reg_len = max(len(r.name) for r in regs)
        assert max_reg_len < reg_win.content.width - 11
        y = 0
        for r in regs:
            if r.flags & Reg.READABLE:
                rv = '%08X' % r.read(dev)
            else:
                rv = '-WrOnly-'
            reg_win.content.addstr('%*s: ' % (
                                    reg_win.content.width - 11, r.name),
                                   pos=(y, 0), attr=curses.A_BOLD)
            reg_win.content.addstr('%s' % rv)
            y += 1
        reg_win.content.noutrefresh()
    else:
        reg_win.hide()


def draw_mem_dump(mem_win, dev):
    if not dev.regs and hasattr(dev, 'size'):
        dev._mem_dump_addr = dev.__dict__.get('_mem_dump_addr', dev.dev_base)
        mem_win.show()
        rows = mem_win.content.height
        addr = dev._mem_dump_addr
        size = min(32*rows, dev.size - (addr - dev.dev_base))
        data = dev.read_mem_block(dev._mem_dump_addr, size)
        rows = int(math.ceil(size / 32.))
        for i in range(rows):
            mem_win.content.addstr('%08X: ' % addr, pos=(i, 0),
                                   attr=curses.A_BOLD)
            row_size = min(32, size)
            size    -= row_size
            offset   = addr - dev._mem_dump_addr
            addr    += row_size
            for j in range(row_size):
                mem_win.content.addstr('%02X ' % data[offset + j])
                if j % 8 == 7:
                    mem_win.content.addstr(' ')

            chars = ''
            for j in range(row_size):
                c = chr(data[offset + j])
                chars += c if curses.ascii.isprint(c) else '.'
            mem_win.content.addstr('%s' % chars, pos=(i, 110))
        mem_win.content.noutrefresh()


def draw_device(reg_win, mem_win, dev):
    regs = dev.regs[:reg_win.content.height]
    if regs:
        mem_win.hide()
        draw_dev_registers(reg_win, dev)
    elif hasattr(dev, 'size'):
        reg_win.hide()
        draw_mem_dump(mem_win, dev)
    else:
        mem_win.hide()
        reg_win.hide()


def mem_up(reg_win, mem_win, d, n):
    avail = d._mem_dump_addr - d.dev_base
    d._mem_dump_addr -= min(avail, n)
    draw_device(reg_win, mem_win, d)


def mem_down(reg_win, mem_win, d, n):
    avail = d.dev_base + d.size - d._mem_dump_addr
    d._mem_dump_addr += min(avail, n)
    if d._mem_dump_addr >= d.dev_base + d.size:
        d._mem_dump_addr = d.dev_base + d.size - 32
    d._mem_dump_addr &= ~31
    if d._mem_dump_addr < d.dev_base:
        d._mem_dump_addr = d.dev_base
    draw_device(reg_win, mem_win, d)


def handle_up(reg_win, mem_win, d):
    if hasattr(d, '_mem_dump_addr'):
        mem_up(reg_win, mem_win, d, 64)


def handle_down(reg_win, mem_win, d):
    if hasattr(d, '_mem_dump_addr'):
        mem_down(reg_win, mem_win, d, 64)


def handle_pageup(reg_win, mem_win, d):
    if hasattr(d, '_mem_dump_addr'):
        nrows = mem_win.content.height
        mem_up(reg_win, mem_win, d, nrows*32)


def handle_pagedown(reg_win, mem_win, d):
    if hasattr(d, '_mem_dump_addr'):
        nrows = mem_win.content.height
        mem_down(reg_win, mem_win, d, nrows*32)


def main(screen, args):
    # Extract args.
    t = args.target

    # Get the device list.
    devs         = sorted(t.devs.values(), key=lambda d: d.dev_base)
    dev_names    = ['%08X %s' % (d.dev_base, d.name) for d in devs]
    max_dev_name = max(len(dn) for dn in dev_names)
    max_reg_name = max(len(r.name) for d in devs for r in d.regs)

    # Create a workspace.
    ws = tgcurses.ui.Workspace(screen)

    # Add a device selector window.
    dev_win  = ws.make_edge_window('Devices', w=-(max_dev_name + 11))
    dev_menu = tgcurses.ui.Menu(dev_win, dev_names)
    dev_win.content.timeout(100)
    dev_win.content.keypad(1)

    # Add a CPU window.
    cpu_win = ws.make_edge_window('CPU', w=17)
    draw_cpu_registers(cpu_win, t.cpus[0])

    # Add a register window.
    reg_win = ws.make_anchored_window(
            'Registers',
            left_anchor=cpu_win.frame.right_anchor(),
            top_anchor=ws.canvas.frame.top_anchor(),
            bottom_anchor=ws.canvas.frame.bottom_anchor(),
            width=max_reg_name + 14)

    # Add a memory window.
    mem_win = ws.make_anchored_window(
            'Memory',
            left_anchor=cpu_win.frame.right_anchor(),
            top_anchor=ws.canvas.frame.top_anchor(),
            bottom_anchor=ws.canvas.frame.bottom_anchor(),
            width=145)

    # Draw the first device.
    draw_device(reg_win, mem_win, devs[dev_menu.selection])

    # Handle user input.
    tgcurses.ui.curs_set(0)
    while True:
        tgcurses.ui.doupdate()
        c = dev_win.content.getch()
        if c == -1:
            draw_device(reg_win, mem_win, devs[dev_menu.selection])
            continue

        if c == ord('q'):
            break
        elif c == curses.KEY_DOWN:
            dev_menu.select_next()
            draw_device(reg_win, mem_win, devs[dev_menu.selection])
        elif c == curses.KEY_UP:
            dev_menu.select_prev()
            draw_device(reg_win, mem_win, devs[dev_menu.selection])
        elif c == curses.KEY_LEFT:
            handle_up(reg_win, mem_win, devs[dev_menu.selection])
        elif c == curses.KEY_RIGHT:
            handle_down(reg_win, mem_win, devs[dev_menu.selection])
        elif c == ord('-'):
            handle_pageup(reg_win, mem_win, devs[dev_menu.selection])
        elif c == ord(' '):
            handle_pagedown(reg_win, mem_win, devs[dev_menu.selection])


if __name__ == '__main__':
    # Parse arguments first.
    parser = argparse.ArgumentParser()
    parser.add_argument('--dump-debuggers', '-d', action='store_true')
    parser.add_argument('--usb-path')
    parser.add_argument('--verbose', '-v', action='store_true')
    args = parser.parse_args()

    # Find a debug probe.
    try:
        args.probe = psdb.probes.find_default(usb_path=args.usb_path)
    except psdb.probes.Exception as e:
        print(e)
        sys.exit(1)

    # Set the max clock frequency.
    args.probe.set_tck_freq_max()

    # Probe the target platform.
    args.target = args.probe.probe(verbose=args.verbose)

    # Interact with the UI.
    tgcurses.wrapper(main, args)

    # Resume the target.
    args.target.resume()
