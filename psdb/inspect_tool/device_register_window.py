# Copyright (c) 2018-2021 Phase Advanced Sensor Systems, Inc.
import curses
import tgcurses
from psdb.devices import Reg, RegDiv

from .device_decode_window import DeviceDecodeWindow


class DeviceRegisterWindow:
    def __init__(self, it, left_elem):
        self.inspect_tool = it
        self.selection    = 0
        self.pos          = 0
        self.dev          = None
        self.reg_vals     = []
        self.edit_val     = None

        self.window = it.workspace.make_anchored_window(
            'Registers', w=it.max_reg_name + 14,
            left_anchor=left_elem.frame.right_anchor(),
            top_anchor=it.workspace.canvas.frame.top_anchor(),
            bottom_anchor=it.workspace.canvas.frame.bottom_anchor(dy=-1))

        self.decode_win = DeviceDecodeWindow(it, self)

    def is_visible(self):
        return self.window.visible

    def get_decode_val(self):
        if self.edit_val is not None:
            return self.edit_val
        return self.get_selected_reg_val()

    def get_selected_reg(self):
        return self.dev.regs[self.selection]

    def get_selected_reg_val(self):
        if not self.reg_vals:
            return None
        return self.reg_vals[self.selection]

    def set_dev(self, dev):
        self.dev       = dev
        self.selection = 0
        self.decode_win.select_register(self.get_selected_reg())
        self.window.show()

    def hide(self):
        self.window.hide()
        self.decode_win.window.hide()

    def draw(self):
        self.window.content.erase()

        regs = self.dev.regs[:self.window.content.height]
        self.reg_vals = [None]*len(regs)
        for i, r in enumerate(regs):
            attr  = curses.A_REVERSE if i == self.selection else 0
            hattr = 0
            if isinstance(r, RegDiv):
                rv = '--------'
            elif i == self.selection and self.edit_val is not None:
                v                = self.edit_val
                self.reg_vals[i] = v
                rv               = '%08X' % v
                hattr            = curses.A_UNDERLINE
            elif r.flags & Reg.READABLE:
                v                = r.read(self.dev)
                self.reg_vals[i] = v
                rv               = '%08X' % v
            else:
                rv = '-WrOnly-'
            self.window.content.addstr(
                '%*s:' % (self.window.content.width - 11, r.name), pos=(i, 0),
                attr=curses.A_BOLD | attr)
            self.window.content.addstr(' ')
            self.window.content.addstr('%s' % rv, attr=hattr)
        self.window.content.noutrefresh()

        self.decode_win.draw()

    def can_focus(self):
        return True

    def focus_lost(self):
        tgcurses.ui.curs_set(0)

    def focus_gained(self):
        self.focus_draw_cursor()
        tgcurses.ui.doupdate()
        tgcurses.ui.curs_set(1)

    def focus_draw_cursor(self):
        self.window.content.move(self.selection,
                                 self.window.content.width - 9 + self.pos)
        self.window.content.noutrefresh()

    def edit_field(self, width, shift, v):
        mask = ((1 << width) - 1)
        if (v & ~mask):
            self.inspect_tool.status('Value too large for field')
            return

        if self.edit_val is None:
            r = self.get_selected_reg()
            if not r.flags & Reg.WRITEABLE:
                self.inspect_tool.status('Register not writeable')
                return
            elif r.flags & Reg.READABLE:
                self.edit_val = r.read(self.dev)
            else:
                self.edit_val = 0

        mask         <<= shift
        self.edit_val &= ~mask
        self.edit_val |= ((v << shift) & mask)
        self.draw()

    def edit_nibble(self, v):
        shift    = 28 - self.pos*4
        self.pos = min(self.pos + 1, 7)
        self.edit_field(4, shift, v)

    def abort_write(self):
        if self.edit_val is not None:
            self.edit_val = None
            self.inspect_tool.status('Write aborted')

    def handle_ch(self, c):
        if c == curses.KEY_UP:
            self.abort_write()
            if self.selection > 0:
                self.selection -= 1
                self.decode_win.select_register(self.get_selected_reg())
        elif c == curses.KEY_DOWN:
            self.abort_write()
            if self.selection < len(self.reg_vals) - 1:
                self.selection += 1
                self.decode_win.select_register(self.get_selected_reg())
        elif c == curses.KEY_LEFT:
            self.pos = max(self.pos - 1, 0)
        elif c == curses.KEY_RIGHT:
            self.pos = min(self.pos + 1, 7)
        elif ord('0') <= c <= ord('9'):
            self.edit_nibble(c - ord('0') + 0x0)
        elif ord('a') <= c <= ord('f'):
            self.edit_nibble(c - ord('a') + 0xA)
        elif ord('A') <= c <= ord('F'):
            self.edit_nibble(c - ord('A') + 0xA)
        elif c == ord('\n'):
            if self.edit_val is not None:
                r = self.get_selected_reg()
                r.write(self.dev, self.edit_val)
                self.edit_val = None
