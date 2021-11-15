# Copyright (c) 2018-2021 Phase Advanced Sensor Systems, Inc.
import curses
import tgcurses.ui


DEV_TYPE_REGISTER = 0
DEV_TYPE_MEMORY   = 1


def get_dev_type(dev):
    if dev.regs:
        return DEV_TYPE_REGISTER
    elif hasattr(dev, 'size'):
        return DEV_TYPE_MEMORY
    raise Exception('Unknown device type!')


class DeviceSelectorWindow:
    def __init__(self, it):
        self.inspect_tool = it

        self.window = it.workspace.make_anchored_window(
            'Devices', w=it.max_dev_name + 11,
            right_anchor=it.workspace.canvas.frame.right_anchor(),
            top_anchor=it.workspace.canvas.frame.top_anchor(),
            bottom_anchor=it.workspace.canvas.frame.bottom_anchor(dy=-1))

        self.menu = tgcurses.ui.Menu(self.window, self.inspect_tool.dev_names)

        d  = self.get_selected_dev()
        dt = get_dev_type(d)
        if dt == DEV_TYPE_REGISTER:
            self.inspect_tool.reg_win.set_dev(d)
        elif dt == DEV_TYPE_MEMORY:
            self.inspect_tool.mem_win.set_mem(d)

    def get_selected_dev(self):
        return self.inspect_tool.devs[self.menu.selection]

    def is_visible(self):
        return self.window.visible

    def focus_lost(self):
        pass

    def focus_gained(self):
        pass

    def handle_ch(self, c):
        updated = False
        if c == curses.KEY_DOWN:
            updated = self.menu.select_next()
        elif c == curses.KEY_UP:
            updated = self.menu.select_prev()

        d  = self.get_selected_dev()
        dt = get_dev_type(d)
        if dt == DEV_TYPE_REGISTER:
            if updated:
                self.inspect_tool.mem_win.hide()
                self.inspect_tool.reg_win.set_dev(d)
            else:
                self.inspect_tool.reg_win.draw()
        elif dt == DEV_TYPE_MEMORY:
            if updated:
                self.inspect_tool.reg_win.hide()
                self.inspect_tool.mem_win.set_mem(d)
            else:
                self.inspect_tool.mem_win.draw()
