# Copyright (c) 2018-2021 Phase Advanced Sensor Systems, Inc.
import curses


class Field:
    def __init__(self, name, width, shift):
        self.name  = name
        self.width = width
        self.shift = shift
        self.mask  = ((1 << width) - 1)

    def extract(self, reg_val):
        return ((reg_val >> self.shift) & self.mask)


class DeviceDecodeWindow:
    def __init__(self, it, reg_win):
        self.inspect_tool  = it
        self.reg_win       = reg_win
        self.fields        = []
        self.named_fields  = []
        self.max_field_len = None
        self.reg_addr      = None

        self.window = it.workspace.make_anchored_window(
            'Decode', w=81, h=23,
            left_anchor=reg_win.window.frame.right_anchor(),
            top_anchor=it.workspace.canvas.frame.top_anchor())

    def select_register(self, reg):
        shift             = 0
        self.fields       = []
        self.named_fields = []
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
            for i, f in enumerate(self.named_fields):
                x = 1 if i < 16 else 41
                y = i % 16
                self.window.content.addstr(
                    '%*s: ' % (self.max_field_len, f.name), pos=(5+y, x),
                    attr=curses.A_BOLD)
                self.window.content.addstr('0x%X' % f.extract(reg_val))

        self.window.content.noutrefresh()
