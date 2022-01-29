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

    def can_focus(self):
        return True

    def focus_lost(self):
        self.menu.hilite_attr = curses.A_REVERSE
        self.menu.select(self.menu.selection)

    def focus_gained(self):
        self.menu.hilite_attr = curses.color_pair(1)
        self.menu.select(self.menu.selection)

    def focus_draw_cursor(self):
        pass

    def handle_ch(self, c):
        updated = False
        if c in (curses.KEY_DOWN, ord('j')):
            updated = self.menu.select_next()
        elif c in (curses.KEY_UP, ord('k')):
            updated = self.menu.select_prev()

        if updated:
            d = self.get_selected_dev()
            self.inspect_tool.handle_device_selected(d)
