# Copyright (c) 2018-2021 Phase Advanced Sensor Systems, Inc.
import curses

import tgcurses


class Field:
    def __init__(self, name, width, shift):
        self.name     = name
        self.width    = width
        self.nnibbles = (width + 3) // 4
        self.shift    = shift
        self.mask     = ((1 << width) - 1)

    def extract(self, reg_val):
        return ((reg_val >> self.shift) & self.mask)


class DeviceDecodeWindow:
    def __init__(self, it, reg_win):
        self.inspect_tool   = it
        self.reg_win        = reg_win
        self.fields         = []
        self.named_fields   = []
        self.max_field_len  = None
        self.reg_addr       = None
        self.selected_field = None
        self.pos            = None
        self.hilite_attr    = curses.A_REVERSE

        self.window = it.workspace.make_anchored_window(
            'Decode', w=81, h=24,
            left_anchor=reg_win.window.frame.right_anchor(),
            top_anchor=it.workspace.canvas.frame.top_anchor())

    def is_visible(self):
        return self.window.visible

    def select_register(self, reg):
        self.fields         = []
        self.named_fields   = []
        self.selected_field = 0
        self.pos            = 0

        shift = 0
        for name, width in reg.fields:
            self.fields.append(Field(name, width, shift))
            if name:
                self.named_fields.append(Field(name, width, shift))
            shift += width

        self.fields.reverse()
        self.named_fields.reverse()

        if self.named_fields:
            self.max_field_len = max(len(f.name) for f in self.named_fields)
        else:
            self.max_field_len = None

        self.reg_addr  = self.reg_win.dev.dev_base + reg.offset
        self.reg_nbits = reg.size*8

    def draw_32bit_border(self, lcorner, tick, rcorner, y):
        chars  = [lcorner,
                  curses.ACS_HLINE, tick,
                  curses.ACS_HLINE, tick,
                  curses.ACS_HLINE, tick,
                  curses.ACS_HLINE,
                  rcorner,
                  ord(' '),
                  ]*8
        self.window.content.addchs(chars, pos=(y, 0))

    def draw(self):
        reg_val = self.reg_win.get_decode_val()
        if reg_val is None:
            self.window.hide()
            return

        self.window.show()
        self.window.content.erase()
        self.window.content.addstr(
            'Address: 0x%08X' % self.reg_addr, pos=(0, 0))

        self.draw_32bit_border(curses.ACS_ULCORNER, curses.ACS_TTEE,
                               curses.ACS_URCORNER, 1)

        self.window.content.move(2, 0)
        bit        = self.reg_nbits - 1
        for f in self.fields:
            v = f.extract(reg_val)
            self.window.content.addch(curses.ACS_VLINE)
            for i in reversed(range(f.width)):
                if f.name:
                    self.window.content.addstr('01'[bool(v & (1 << i))])
                    fill = ord(' ')
                else:
                    self.window.content.addch(curses.ACS_BULLET)
                    fill = curses.ACS_BULLET

                if bit == 0:
                    pass
                elif ((bit + 1) % 4) == 1:
                    if i:
                        self.window.content.addch(fill)
                        self.window.content.addch(fill)
                    else:
                        self.window.content.addch(curses.ACS_VLINE)
                        self.window.content.addch(ord(' '))
                    if i:
                        self.window.content.addch(fill)
                elif i:
                    self.window.content.addch(fill)

                bit -= 1
        self.window.content.addch(curses.ACS_VLINE)

        self.draw_32bit_border(curses.ACS_LLCORNER, curses.ACS_BTEE,
                               curses.ACS_LRCORNER, 3)

        for i in range(self.reg_nbits // 4):
            self.window.content.addstr('%X' % ((reg_val >> (28-4*i)) & 0xF),
                                       pos=(4, 4+i*10))

        if self.named_fields:
            if self.reg_win.edit_val is not None:
                hattr = curses.A_UNDERLINE
            else:
                hattr = 0
            for i, f in enumerate(self.named_fields):
                x = 0 if i < 16 else 40
                y = i % 16
                attr = curses.A_BOLD
                if i == self.selected_field:
                    attr |= self.hilite_attr
                self.window.content.addstr(
                    ' %*s:' % (self.max_field_len, f.name), pos=(6+y, x),
                    attr=attr)
                self.window.content.addstr(' ')
                self.window.content.addstr(
                    '%0*X' % (f.nnibbles, f.extract(reg_val)), attr=hattr)

        self.window.content.noutrefresh()

    def can_focus(self):
        return bool(self.named_fields)

    def focus_lost(self):
        self.hilite_attr = curses.A_REVERSE
        self.draw()
        tgcurses.ui.curs_set(0)

    def focus_gained(self):
        self.hilite_attr = curses.color_pair(1)
        self.draw()
        self.focus_draw_cursor()
        tgcurses.ui.doupdate()
        tgcurses.ui.curs_set(1)

    def focus_draw_cursor(self):
        x = 1 if self.selected_field < 16 else 41
        self.window.content.move(6 + (self.selected_field % 16),
                                 x + self.max_field_len + 2 + self.pos)
        self.window.content.noutrefresh()

    def edit_nibble(self, v):
        f        = self.named_fields[self.selected_field]
        shift    = (f.nnibbles - self.pos - 1) * 4
        width    = min(f.width - shift, 4)
        self.pos = min(self.pos + 1, f.nnibbles - 1)
        self.reg_win.edit_field(width, f.shift + shift, v)

    def handle_ch(self, c):
        if c in (curses.KEY_UP, ord('k')):
            if self.selected_field > 0:
                self.selected_field -= 1
                self.pos = min(
                    self.pos,
                    self.named_fields[self.selected_field].nnibbles - 1)
        elif c in (curses.KEY_DOWN, ord('j')):
            if self.selected_field < len(self.named_fields) - 1:
                self.selected_field += 1
                self.pos = min(
                    self.pos,
                    self.named_fields[self.selected_field].nnibbles - 1)
        elif c in (curses.KEY_LEFT, ord('h')):
            self.pos = max(self.pos - 1, 0)
        elif c in (curses.KEY_RIGHT, ord('l')):
            self.pos = min(
                self.pos + 1,
                self.named_fields[self.selected_field].nnibbles - 1)
        elif ord('0') <= c <= ord('9'):
            self.edit_nibble(c - ord('0') + 0x0)
        elif ord('a') <= c <= ord('f'):
            self.edit_nibble(c - ord('a') + 0xA)
        elif ord('A') <= c <= ord('F'):
            self.edit_nibble(c - ord('A') + 0xA)
        elif c == ord('\n'):
            self.reg_win.handle_ch(c)
