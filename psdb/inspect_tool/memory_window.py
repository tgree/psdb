# Copyright (c) 2018-2021 Phase Advanced Sensor Systems, Inc.
import math
import curses


class MemoryWindow:
    def __init__(self, it, left_elem):
        self.inspect_tool = it
        self.dump_addrs   = {}
        self.dump_addr    = None
        self.dev          = None

        self.window = it.workspace.make_anchored_window(
            'Memory', w=145,
            left_anchor=left_elem.frame.right_anchor(),
            top_anchor=it.workspace.canvas.frame.top_anchor(),
            bottom_anchor=it.workspace.canvas.frame.bottom_anchor(dy=-1))

    def is_visible(self):
        return self.window.visible

    def set_mem(self, dev):
        if self.dev:
            self.dump_addrs[self.dev] = self.dump_addr

        self.dev       = dev
        self.dump_addr = self.dump_addrs.get(dev, dev.dev_base)
        self.draw()

    def set_addr(self, addr):
        addr = min(self.dev.dev_base + self.dev.size - 32, addr)
        addr = max(self.dev.dev_base, addr)
        self.dump_addr = addr
        self.draw()

    def hide(self):
        self.window.hide()

    def draw(self):
        self.window.show()
        self.window.content.erase()

        rows = self.window.content.height
        addr = self.dump_addr
        size = min(32*rows, self.dev.size - (addr - self.dev.dev_base))
        data = self.dev.read_mem_block(self.dump_addr, size)
        rows = int(math.ceil(size / 32.))
        for i in range(rows):
            self.window.content.addstr('%08X: ' % addr, pos=(i, 0),
                                       attr=curses.A_BOLD)
            row_size = min(32, size)
            size    -= row_size
            offset   = addr - self.dump_addr
            addr    += row_size
            for j in range(row_size):
                self.window.content.addstr('%02X ' % data[offset + j])
                if j % 8 == 7:
                    self.window.content.addstr(' ')

            chars = ''
            for j in range(row_size):
                c = chr(data[offset + j])
                chars += c if curses.ascii.isprint(c) else '.'
            self.window.content.addstr('%s' % chars, pos=(i, 110))
        self.window.content.noutrefresh()

    def focus_lost(self):
        pass

    def focus_gained(self):
        pass

    def handle_ch(self, c):
        if c == curses.KEY_DOWN:
            self.set_addr(self.dump_addr + 32)
        elif c == curses.KEY_UP:
            self.set_addr(self.dump_addr - 32)
        elif c == curses.KEY_NPAGE:
            nrows = self.window.content.height
            self.set_addr(self.dump_addr + nrows*32 - 32)
        elif c == curses.KEY_PPAGE:
            nrows = self.window.content.height
            self.set_addr(self.dump_addr - nrows*32 + 32)
        self.draw()
