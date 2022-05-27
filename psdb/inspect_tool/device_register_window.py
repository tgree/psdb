# Copyright (c) 2018-2021 Phase Advanced Sensor Systems, Inc.
import curses
import _curses
import tgcurses
from psdb.devices import Reg, RegDiv

from .device_decode_window import DeviceDecodeWindow


class DeviceRegisterWindow:
    def __init__(self, it, left_elem):
        self.inspect_tool = it
        self.top          = 0
        self.selection    = 0
        self.pos          = 0
        self.dev          = None
        self.reg_vals     = None
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

    def read_selected_reg(self):
        v = self.dev.regs[self.selection].read(self.dev)
        self.reg_vals[self.selection] = v

    def set_dev(self, dev):
        self.dev         = dev
        self.reg_vals    = [None] * len(self.dev.regs)
        self.top         = 0
        self.selection   = 0
        self.pos         = 0
        self.hilite_attr = curses.A_REVERSE
        self.decode_win.select_register(self.get_selected_reg())
        self.window.show()

    def hide(self):
        self.window.hide()
        self.decode_win.window.hide()

    def update_reg_vals(self):
        cmd_list = []
        for i, r in enumerate(self.dev.regs):
            if i == self.selection and self.edit_val is not None:
                continue
            elif (r.flags & Reg.READABLE) and not (r.flags & Reg.SIDE_EFFECTS):
                cmd_list.append(r.read_cmd(self.dev))
            else:
                continue

        read_vals = self.dev.ap.db.exec_cmd_list(cmd_list)

        for i, r in enumerate(self.dev.regs):
            if i == self.selection and self.edit_val is not None:
                self.reg_vals[i] = self.edit_val
            elif (r.flags & Reg.READABLE) and not (r.flags & Reg.SIDE_EFFECTS):
                self.reg_vals[i] = read_vals.pop(0)

    def draw_item(self, i):
        rows = self.window.content.height
        if i < self.top or i >= self.top + rows:
            return

        r = self.dev.regs[i]
        if isinstance(r, RegDiv):
            rv = '--------'
        elif self.reg_vals[i] is not None:
            rv = '%08X' % self.reg_vals[i]
        elif not (r.flags & Reg.READABLE):
            rv = '-WrOnly-'
        else:
            rv = '-SideFx-'

        row = i - self.top
        if self.top > 0 and row == 0:
            tag = '\u2191'.encode('utf-8')
        elif self.top + rows < len(self.dev.regs) and row == rows - 1:
            tag = '\u2193'.encode('utf-8')
        else:
            tag = ' '

        attr  = self.hilite_attr if i == self.selection else 0
        hattr = (curses.A_UNDERLINE
                 if i == self.selection and self.edit_val is not None else 0)
        self.window.content.addstr(
            '%*s:' % (self.window.content.width - 11, r.name), pos=(row, 0),
            attr=curses.A_BOLD | attr)
        self.window.content.addstr(' ')
        self.window.content.addstr('%s' % rv, attr=hattr)
        try:
            self.window.content.addstr(tag)
        except _curses.error:
            pass

        self.window.content.noutrefresh()

    def draw(self):
        self.window.content.erase()

        self.update_reg_vals()
        for i in range(len(self.reg_vals)):
            self.draw_item(i)

        self.decode_win.draw()

    def can_focus(self):
        return True

    def focus_lost(self):
        self.hilite_attr = curses.A_REVERSE
        self.draw_item(self.selection)
        tgcurses.ui.curs_set(0)

    def focus_gained(self):
        self.hilite_attr = curses.color_pair(1)
        self.draw_item(self.selection)
        self.focus_draw_cursor()
        tgcurses.ui.doupdate()
        tgcurses.ui.curs_set(1)

    def focus_draw_cursor(self):
        self.window.content.move(self.selection - self.top,
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
            elif (r.flags & Reg.READABLE) and not (r.flags & Reg.SIDE_EFFECTS):
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

    def select(self, index):
        rows           = self.window.content.height
        self.top       = min(self.top, index)
        self.top       = max(self.top, index - rows + 1)
        self.selection = index
        self.decode_win.select_register(self.get_selected_reg())

    def handle_ch(self, c):
        if c in (curses.KEY_UP, ord('k')):
            self.abort_write()
            if self.selection > 0:
                self.select(self.selection - 1)
        elif c in (curses.KEY_DOWN, ord('j')):
            self.abort_write()
            if self.selection < len(self.reg_vals) - 1:
                self.select(self.selection + 1)
        elif c in (curses.KEY_LEFT, ord('h')):
            self.pos = max(self.pos - 1, 0)
        elif c in (curses.KEY_RIGHT, ord('l')):
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
        elif c == ord(' '):
            if self.edit_val is None:
                self.read_selected_reg()
                self.draw_item(self.selection)
