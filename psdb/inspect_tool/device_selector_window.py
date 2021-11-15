# Copyright (c) 2018-2021 Phase Advanced Sensor Systems, Inc.
import curses
import tgcurses.ui


DEV_TYPE_REGISTER = 0
DEV_TYPE_MEMORY   = 1


class DeviceSelectorWindow:
    def __init__(self, devs, reg_win, mem_win, workspace):
        dev_names    = ['%08X %s' % (d.dev_base, d.path) for d in devs]
        max_dev_name = max(len(dn) for dn in dev_names)

        self.workspace = workspace
        self.devs      = devs
        self.reg_win   = reg_win
        self.mem_win   = mem_win
        self.window    = workspace.make_anchored_window(
            'Devices', w=max_dev_name + 11,
            right_anchor=workspace.canvas.frame.right_anchor(),
            top_anchor=workspace.canvas.frame.top_anchor(),
            bottom_anchor=workspace.canvas.frame.bottom_anchor(dy=-1))
        self.menu      = tgcurses.ui.Menu(self.window, dev_names)

        dt = self.get_dev_type()
        if dt == DEV_TYPE_REGISTER:
            self.reg_win.set_dev(devs[0])
        elif dt == DEV_TYPE_MEMORY:
            self.mem_win.set_mem(devs[0])

    def get_selected_dev(self):
        return self.devs[self.menu.selection]

    def get_dev_type(self):
        dev = self.get_selected_dev()
        if dev.regs:
            return DEV_TYPE_REGISTER
        elif hasattr(dev, 'size'):
            return DEV_TYPE_MEMORY
        raise Exception('Unknown device type!')

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

        dt = self.get_dev_type()
        if dt == DEV_TYPE_REGISTER:
            if updated:
                self.mem_win.hide()
                self.reg_win.set_dev(self.get_selected_dev())
            else:
                self.reg_win.draw()
        elif dt == DEV_TYPE_MEMORY:
            if updated:
                self.reg_win.hide()
                self.mem_win.set_mem(self.get_selected_dev())
            else:
                self.mem_win.draw()
