#!/usr/bin/env python3

import curses
import sys

from cellaserv.proxy import CellaservProxy

class AX:

    def __init__(self, ax, win):
        self.ax = ax
        self.win = win

        self.position = 0
        self.voltage = 0
        self.temperature = 0
        self.load = 0

        self.draw_base()
        self.update_state()

    def draw_base(self):
        self.win.border(0)
        self.win.addstr(1, 1, "AX:          {: <5}".format(self.ax.identification))
        self.win.addstr(2, 1, "Position:    ")
        self.win.addstr(3, 1, "Voltage:     ")
        self.win.addstr(4, 1, "Temperature: ")
        self.win.addstr(5, 1, "Load:      ")

    def update_state(self):
        new_pos = self.ax.get_present_position()
        self.position = new_pos or self.position

        new_voltage = self.ax.get_present_voltage()
        self.voltage = new_voltage or self.voltage

        new_temperature = self.ax.get_present_temperature()
        self.temperature = new_temperature or self.temperature

        new_load = self.ax.get_present_load() # usually 0
        self.load = new_load & ((1<<10) - 1)
        self.load_sign = "+" if new_load & (1<<10) else "-"

    def refresh(self):
        # TODO: do not redraw everything
        self.win.addstr(2, 14, "{: <5}".format(self.position))
        self.win.addstr(3, 14, "{: <5}".format(self.voltage))
        self.win.addstr(4, 14, "{: <5}".format(self.temperature))
        self.win.addstr(5, 12, "{} {: <5}".format(self.load_sign, self.load))

        self.win.refresh()

def app(stdscr):
    curses.curs_set(0) # invisible cursor
    stdscr.timeout(20) # 20 ms max delay

    cs = CellaservProxy()
    axs = [cs.ax[ax_id] for ax_id in sys.argv[1:]]

    ax_windows = [AX(ax, stdscr.derwin(7, 20, i*7, 0)) for i, ax in enumerate(axs)]

    while stdscr.getch() != 27: # 27 == ESC
        for win in ax_windows:
            win.update_state()
            win.refresh()

def main():
    if len(sys.argv) < 2:
        print("Error: expect ax ids as argument", file=sys.stderr)
        sys.exit(1)

    curses.wrapper(app)

if __name__ == '__main__':
    main()
