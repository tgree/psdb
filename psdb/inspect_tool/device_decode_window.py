# Copyright (c) 2018-2021 Phase Advanced Sensor Systems, Inc.
import curses


class DeviceDecodeWindow:
    def __init__(self, it, reg_win):
        self.inspect_tool = it
        self.reg_win      = reg_win

        self.window = it.workspace.make_anchored_window(
            'Decode', w=81, h=23,
            left_anchor=reg_win.window.frame.right_anchor(),
            top_anchor=it.workspace.canvas.frame.top_anchor())

    def decode(self):
        reg, reg_val = self.reg_win.get_decode_info()
        if reg_val is None:
            return reg, None, [], []

        shift        = 0
        fields       = []
        named_fields = []
        for name, width in reg.fields:
            mask = ((1 << width) - 1)
            v    = ((reg_val >> shift) & mask)
            fields.append((name, width, shift, v))
            if name:
                named_fields.append((name, width, shift, v))
            shift += width

        return reg, reg_val, fields, named_fields

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
        reg, reg_val, fields, named_fields = self.decode()
        if reg_val is None:
            self.window.hide()
            return
        dev = self.reg_win.dev

        self.window.show()
        self.window.content.erase()
        self.window.content.addstr(
            'Address: 0x%08X' % (dev.dev_base + reg.offset), pos=(0, 0))

        self.draw_32bit_border(curses.ACS_ULCORNER, curses.ACS_TTEE,
                               curses.ACS_URCORNER, 1)

        self.window.content.move(2, 0)
        bit        = reg.size*8 - 1
        for name, width, _, v in reversed(fields):
            self.window.content.addch(curses.ACS_VLINE)
            for i in reversed(range(width)):
                if name:
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

        for i in range(reg.size*2):
            self.window.content.addstr('%X' % ((reg_val >> (28-4*i)) & 0xF),
                                       pos=(4, 4+i*10))

        if named_fields:
            w   = max(len(name) for name, _, _, _ in named_fields)
            for i, (name, _, _, v) in enumerate(reversed(named_fields)):
                x = 1 if i < 16 else 41
                y = i % 16
                self.window.content.addstr('%*s: ' % (w, name), pos=(5+y, x),
                                           attr=curses.A_BOLD)
                self.window.content.addstr('0x%X' % v)

        self.window.content.noutrefresh()
