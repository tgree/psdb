#!/usr/bin/env python3
# Copyright (c) 2018-2019 Phase Advanced Sensor Systems, Inc.
import argparse
import curses
import curses.ascii
import math
import sys

import psdb.probes
from psdb.devices import Reg, RegDiv
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
        reg_win.reg_vals = [None]*len(regs)
        for i, r in enumerate(regs):
            attr = curses.A_REVERSE if i == reg_win.selection else 0
            if isinstance(r, RegDiv):
                rv = '--------'
            elif r.flags & Reg.READABLE:
                v                   = r.read(dev)
                reg_win.reg_vals[i] = v
                rv                  = '%08X' % v
            else:
                rv = '-WrOnly-'
            reg_win.content.addstr('%*s: ' % (
                                    reg_win.content.width - 11, r.name),
                                   pos=(i, 0), attr=curses.A_BOLD | attr)
            reg_win.content.addstr('%s' % rv, attr=attr)
        reg_win.content.noutrefresh()
    else:
        reg_win.hide()


def draw_decode(reg_win, decode_win, dev):  # noqa: C901
    if not dev.regs:
        decode_win.hide()
        return

    r = dev.regs[reg_win.selection]
    if not (r.flags & Reg.READABLE):
        decode_win.hide()
        return
    rv = reg_win.reg_vals[reg_win.selection]

    decode_win.show()
    decode_win.content.erase()
    chars  = [curses.ACS_ULCORNER,
              curses.ACS_HLINE, curses.ACS_TTEE,
              curses.ACS_HLINE, curses.ACS_TTEE,
              curses.ACS_HLINE, curses.ACS_TTEE,
              curses.ACS_HLINE,
              curses.ACS_URCORNER,
              ord(' '),
              ]*8
    decode_win.content.addchs(chars, pos=(0, 0))

    decode_win.content.move(1, 0)
    bit = r.size*8 - 1
    field_vals = []
    for f in reversed(r.fields):
        decode_win.content.addch(curses.ACS_VLINE)
        if f[0]:
            fv = 0
            for i in reversed(range(f[1])):
                fv <<= 1
                if rv & (1 << bit):
                    decode_win.content.addstr('1')
                    fv |= 1
                else:
                    decode_win.content.addstr('0')

                if bit == 0:
                    pass
                elif ((bit + 1) % 4) == 1:
                    if i:
                        decode_win.content.addch(ord(' '))
                    else:
                        decode_win.content.addch(curses.ACS_VLINE)
                    decode_win.content.addch(ord(' '))
                    if i:
                        decode_win.content.addch(ord(' '))
                elif i:
                    decode_win.content.addstr(' ')
                bit -= 1
            field_vals.append((f[0], fv))
        else:
            for i in reversed(range(f[1])):
                decode_win.content.addch(curses.ACS_BULLET)
                if bit == 0:
                    pass
                elif ((bit + 1) % 4) == 1:
                    if i:
                        decode_win.content.addch(curses.ACS_BULLET)
                        decode_win.content.addch(curses.ACS_BULLET)
                    else:
                        decode_win.content.addch(curses.ACS_VLINE)
                        decode_win.content.addch(ord(' '))
                    if i:
                        decode_win.content.addch(curses.ACS_BULLET)
                elif i:
                    decode_win.content.addch(curses.ACS_BULLET)
                bit -= 1
    decode_win.content.addch(curses.ACS_VLINE)

    chars  = [curses.ACS_LLCORNER,
              curses.ACS_HLINE, curses.ACS_BTEE,
              curses.ACS_HLINE, curses.ACS_BTEE,
              curses.ACS_HLINE, curses.ACS_BTEE,
              curses.ACS_HLINE,
              curses.ACS_LRCORNER,
              ord(' '),
              ]*8
    decode_win.content.addchs(chars, pos=(2, 0))

    for i in range(r.size*2):
        decode_win.content.addstr('%X' % ((rv >> (28-4*i)) & 0xF),
                                  pos=(3, 4+i*10))

    if len(field_vals) > 0:
        w = max(len(fv[0]) for fv in field_vals[:16])
        for i, fv in enumerate(field_vals[:16]):
            decode_win.content.addstr('%*s: ' % (w, fv[0]), pos=(4+i, 1),
                                      attr=curses.A_BOLD)
            decode_win.content.addstr('0x%X' % fv[1])

    if len(field_vals) > 16:
        w = max(len(fv[0]) for fv in field_vals[16:])
        for i, fv in enumerate(field_vals[16:]):
            decode_win.content.addstr('%*s: ' % (w, fv[0]), pos=(4+i, 41),
                                      attr=curses.A_BOLD)
            decode_win.content.addstr('0x%X' % fv[1])

    decode_win.content.noutrefresh()


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


def draw_device(reg_win, mem_win, decode_win, dev):
    regs = dev.regs[:reg_win.content.height]
    if regs:
        mem_win.hide()
        draw_dev_registers(reg_win, dev)
        draw_decode(reg_win, decode_win, dev)
    elif hasattr(dev, 'size'):
        reg_win.hide()
        decode_win.hide()
        draw_mem_dump(mem_win, dev)
    else:
        mem_win.hide()
        reg_win.hide()
        decode_win.hide()


def mem_up(reg_win, mem_win, decode_win, d, n):
    avail = d._mem_dump_addr - d.dev_base
    d._mem_dump_addr -= min(avail, n)
    draw_device(reg_win, mem_win, decode_win, d)


def mem_down(reg_win, mem_win, decode_win, d, n):
    avail = d.dev_base + d.size - d._mem_dump_addr
    d._mem_dump_addr += min(avail, n)
    if d._mem_dump_addr >= d.dev_base + d.size:
        d._mem_dump_addr = d.dev_base + d.size - 32
    d._mem_dump_addr &= ~31
    if d._mem_dump_addr < d.dev_base:
        d._mem_dump_addr = d.dev_base
    draw_device(reg_win, mem_win, decode_win, d)


def handle_up(reg_win, mem_win, decode_win, d):
    if hasattr(d, '_mem_dump_addr'):
        mem_up(reg_win, mem_win, decode_win, d, 64)


def handle_down(reg_win, mem_win, decode_win, d):
    if hasattr(d, '_mem_dump_addr'):
        mem_down(reg_win, mem_win, decode_win, d, 64)


def handle_pageup(reg_win, mem_win, decode_win, d):
    if hasattr(d, '_mem_dump_addr'):
        nrows = mem_win.content.height
        mem_up(reg_win, mem_win, decode_win, d, nrows*32)


def handle_pagedown(reg_win, mem_win, decode_win, d):
    if hasattr(d, '_mem_dump_addr'):
        nrows = mem_win.content.height
        mem_down(reg_win, mem_win, decode_win, d, nrows*32)


def main(screen, args):  # noqa: C901
    # Extract args.
    t = args.target

    # Get the device list.
    devs = list(t.devs.values())
    for c in t.cpus:
        devs += list(c.devs.values())

    # Parse it.
    devs         = sorted(devs, key=lambda d: d.dev_base)
    dev_names    = ['%08X %s' % (d.dev_base, d.path) for d in devs]
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
    cpu_wins = []
    for i, c in enumerate(t.cpus):
        if i == 0:
            cpu_wins.append(ws.make_edge_window('CPU%u (%s)' % (i, c.model),
                                                w=18))
        else:
            cpu_wins.append(ws.make_anchored_window(
                'CPU%u (%s)' % (i, c.model), w=18,
                left_anchor=cpu_wins[-1].frame.right_anchor(),
                top_anchor=ws.canvas.frame.top_anchor(),
                bottom_anchor=ws.canvas.frame.bottom_anchor(),
                ))
        draw_cpu_registers(cpu_wins[-1], c)

    # Add a register window.
    reg_win = ws.make_anchored_window(
            'Registers',
            left_anchor=cpu_wins[-1].frame.right_anchor(),
            top_anchor=ws.canvas.frame.top_anchor(),
            bottom_anchor=ws.canvas.frame.bottom_anchor(),
            w=max_reg_name + 14)
    reg_win.selection = 0

    # Add a decode window.
    decode_win = ws.make_anchored_window(
            'Decode',
            left_anchor=reg_win.frame.right_anchor(),
            top_anchor=ws.canvas.frame.top_anchor(),
            w=81, h=22)

    # Add a memory window.
    mem_win = ws.make_anchored_window(
            'Memory',
            left_anchor=cpu_wins[-1].frame.right_anchor(),
            top_anchor=ws.canvas.frame.top_anchor(),
            bottom_anchor=ws.canvas.frame.bottom_anchor(),
            w=145)

    # Draw the first device.
    draw_device(reg_win, mem_win, decode_win, devs[dev_menu.selection])

    # Handle user input.
    tgcurses.ui.curs_set(0)
    focus = dev_win
    while True:
        tgcurses.ui.doupdate()
        c = dev_win.content.getch()
        if c == -1:
            draw_device(reg_win, mem_win, decode_win, devs[dev_menu.selection])
            continue

        if c == ord('q'):
            break
        elif focus == dev_win:
            if c == ord('\t'):
                if reg_win.visible:
                    focus = reg_win
            elif c == curses.KEY_DOWN:
                if dev_menu.select_next():
                    reg_win.selection = 0
                draw_device(reg_win, mem_win, decode_win,
                            devs[dev_menu.selection])
            elif c == curses.KEY_UP:
                if dev_menu.select_prev():
                    reg_win.selection = 0
                draw_device(reg_win, mem_win, decode_win,
                            devs[dev_menu.selection])
            elif c == curses.KEY_LEFT:
                handle_up(reg_win, mem_win, decode_win,
                          devs[dev_menu.selection])
            elif c == curses.KEY_RIGHT:
                handle_down(reg_win, mem_win, decode_win,
                            devs[dev_menu.selection])
            elif c == ord('-'):
                handle_pageup(reg_win, mem_win, decode_win,
                              devs[dev_menu.selection])
            elif c == ord(' '):
                handle_pagedown(reg_win, mem_win, decode_win,
                                devs[dev_menu.selection])
        elif focus == reg_win:
            if c == ord('\t'):
                focus = dev_win
            elif c == curses.KEY_UP:
                if reg_win.selection > 0:
                    reg_win.selection -= 1
                    draw_device(reg_win, mem_win, decode_win,
                                devs[dev_menu.selection])
            elif c == curses.KEY_DOWN:
                if reg_win.selection < len(devs[dev_menu.selection].regs) - 1:
                    reg_win.selection += 1
                    draw_device(reg_win, mem_win, decode_win,
                                devs[dev_menu.selection])


def _main():
    # Parse arguments first.
    parser = argparse.ArgumentParser()
    parser.add_argument('--dump-debuggers', '-d', action='store_true')
    parser.add_argument('--usb-path')
    parser.add_argument('--probe-freq', type=int, default=1000000)
    parser.add_argument('--verbose', '-v', action='store_true')
    parser.add_argument('--srst', action='store_true')
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
    args.target = args.probe.probe(verbose=args.verbose)

    # Set the max clock frequency.
    args.target.set_max_tck_freq()

    # Interact with the UI.
    tgcurses.wrapper(main, args)

    # Resume the target.
    if args.resume:
        args.target.resume()


if __name__ == '__main__':
    _main()
