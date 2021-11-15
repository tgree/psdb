# Copyright (c) 2018-2021 Phase Advanced Sensor Systems, Inc.
import curses


class CPURegisterWindow:
    def __init__(self, index, cpu, workspace, left_anchor):
        self.index     = index
        self.cpu       = cpu
        self.workspace = workspace
        self.window    = workspace.make_anchored_window(
            'CPU%u (%s)' % (index, cpu.model), w=18,
            left_anchor=left_anchor,
            top_anchor=workspace.canvas.frame.top_anchor(),
            bottom_anchor=workspace.canvas.frame.bottom_anchor(dy=-1))

    def draw(self):
        self.window.content.erase()
        regs = self.cpu.read_core_registers()
        y = 0
        for k, v in regs.items():
            self.window.content.addstr(
                '%*s: ' % (self.window.content.width - 11, k),
                pos=(y, 0), attr=curses.A_BOLD)
            self.window.content.addstr('%08X' % v)
            y += 1
        self.window.content.noutrefresh()
