# Copyright (c) 2018-2021 Phase Advanced Sensor Systems, Inc.
import curses
from psdb.devices import Reg, RegDiv

from .device_decode_window import DeviceDecodeWindow


class DeviceRegisterWindow:
    def __init__(self, it, left_elem):
        self.inspect_tool = it
        self.selection    = 0
        self.dev          = None
        self.reg_vals     = []

        self.window = it.workspace.make_anchored_window(
            'Registers', w=it.max_reg_name + 14,
            left_anchor=left_elem.frame.right_anchor(),
            top_anchor=it.workspace.canvas.frame.top_anchor(),
            bottom_anchor=it.workspace.canvas.frame.bottom_anchor(dy=-1))

        self.decode_win = DeviceDecodeWindow(it, self.window)

    def is_visible(self):
        return self.window.visible

    def get_selected_reg(self):
        return self.dev.regs[self.selection]

    def get_selected_reg_val(self):
        if not self.reg_vals:
            return None
        return self.reg_vals[self.selection]

    def set_dev(self, dev):
        self.dev       = dev
        self.selection = 0
        self.window.show()

    def hide(self):
        self.window.hide()
        self.decode_win.window.hide()

    def draw(self):
        self.window.content.erase()

        regs = self.dev.regs[:self.window.content.height]
        self.reg_vals = [None]*len(regs)
        for i, r in enumerate(regs):
            attr = curses.A_REVERSE if i == self.selection else 0
            if isinstance(r, RegDiv):
                rv = '--------'
            elif r.flags & Reg.READABLE:
                v                = r.read(self.dev)
                self.reg_vals[i] = v
                rv               = '%08X' % v
            else:
                rv = '-WrOnly-'
            self.window.content.addstr(
                '%*s: ' % (self.window.content.width - 11, r.name), pos=(i, 0),
                attr=curses.A_BOLD | attr)
            self.window.content.addstr('%s' % rv, attr=attr)
        self.window.content.noutrefresh()

        self.decode_win.draw(self.dev, self.dev.regs[self.selection],
                             self.reg_vals[self.selection])

    def focus_lost(self):
        pass

    def focus_gained(self):
        pass

    def handle_ch(self, c):
        if c == curses.KEY_UP:
            if self.selection > 0:
                self.selection -= 1
        elif c == curses.KEY_DOWN:
            if self.selection < len(self.reg_vals) - 1:
                self.selection += 1
