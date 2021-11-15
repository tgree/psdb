# Copyright (c) 2018-2021 Phase Advanced Sensor Systems, Inc.
import curses


class DeviceDecodeWindow:
    def __init__(self, it, left_elem):
        self.inspect_tool = it

        self.window = it.workspace.make_anchored_window(
            'Decode', w=81, h=23,
            left_anchor=left_elem.frame.right_anchor(),
            top_anchor=it.workspace.canvas.frame.top_anchor())

    def draw(self, dev, reg, reg_val):  # noqa: C901
        if reg_val is None:
            self.window.hide()
            return

        self.window.show()
        self.window.content.erase()
        self.window.content.addstr(
            'Address: 0x%08X' % (dev.dev_base + reg.offset), pos=(0, 0))

        chars  = [curses.ACS_ULCORNER,
                  curses.ACS_HLINE, curses.ACS_TTEE,
                  curses.ACS_HLINE, curses.ACS_TTEE,
                  curses.ACS_HLINE, curses.ACS_TTEE,
                  curses.ACS_HLINE,
                  curses.ACS_URCORNER,
                  ord(' '),
                  ]*8
        self.window.content.addchs(chars, pos=(1, 0))

        self.window.content.move(2, 0)
        bit        = reg.size*8 - 1
        field_vals = []
        for f in reversed(reg.fields):
            self.window.content.addch(curses.ACS_VLINE)
            if f[0]:
                fv = 0
                for i in reversed(range(f[1])):
                    fv <<= 1
                    if reg_val & (1 << bit):
                        self.window.content.addstr('1')
                        fv |= 1
                    else:
                        self.window.content.addstr('0')

                    if bit == 0:
                        pass
                    elif ((bit + 1) % 4) == 1:
                        if i:
                            self.window.content.addch(ord(' '))
                        else:
                            self.window.content.addch(curses.ACS_VLINE)
                        self.window.content.addch(ord(' '))
                        if i:
                            self.window.content.addch(ord(' '))
                    elif i:
                        self.window.content.addstr(' ')
                    bit -= 1
                field_vals.append((f[0], fv))
            else:
                for i in reversed(range(f[1])):
                    self.window.content.addch(curses.ACS_BULLET)
                    if bit == 0:
                        pass
                    elif ((bit + 1) % 4) == 1:
                        if i:
                            self.window.content.addch(curses.ACS_BULLET)
                            self.window.content.addch(curses.ACS_BULLET)
                        else:
                            self.window.content.addch(curses.ACS_VLINE)
                            self.window.content.addch(ord(' '))
                        if i:
                            self.window.content.addch(curses.ACS_BULLET)
                    elif i:
                        self.window.content.addch(curses.ACS_BULLET)
                    bit -= 1
        self.window.content.addch(curses.ACS_VLINE)

        chars  = [curses.ACS_LLCORNER,
                  curses.ACS_HLINE, curses.ACS_BTEE,
                  curses.ACS_HLINE, curses.ACS_BTEE,
                  curses.ACS_HLINE, curses.ACS_BTEE,
                  curses.ACS_HLINE,
                  curses.ACS_LRCORNER,
                  ord(' '),
                  ]*8
        self.window.content.addchs(chars, pos=(3, 0))

        for i in range(reg.size*2):
            self.window.content.addstr('%X' % ((reg_val >> (28-4*i)) & 0xF),
                                       pos=(4, 4+i*10))

        if len(field_vals) > 0:
            w = max(len(fv[0]) for fv in field_vals[:16])
            for i, fv in enumerate(field_vals[:16]):
                self.window.content.addstr('%*s: ' % (w, fv[0]), pos=(5+i, 1),
                                           attr=curses.A_BOLD)
                self.window.content.addstr('0x%X' % fv[1])

        if len(field_vals) > 16:
            w = max(len(fv[0]) for fv in field_vals[16:])
            for i, fv in enumerate(field_vals[16:]):
                self.window.content.addstr('%*s: ' % (w, fv[0]), pos=(5+i, 41),
                                           attr=curses.A_BOLD)
                self.window.content.addstr('0x%X' % fv[1])

        self.window.content.noutrefresh()
