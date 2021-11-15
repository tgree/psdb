# Copyright (c) 2018-2021 Phase Advanced Sensor Systems, Inc.
import curses
import tgcurses.ui


class DeviceSelectorWindow:
    def __init__(self, it):
        self.inspect_tool = it

        self.window = it.workspace.make_anchored_window(
            'Devices', w=it.max_dev_name + 11,
            right_anchor=it.workspace.canvas.frame.right_anchor(),
            top_anchor=it.workspace.canvas.frame.top_anchor(),
            bottom_anchor=it.workspace.canvas.frame.bottom_anchor(dy=-1))

        self.menu = tgcurses.ui.Menu(self.window, self.inspect_tool.dev_names)

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

        if updated:
            d = self.get_selected_dev()
            self.inspect_tool.handle_device_selected(d)
