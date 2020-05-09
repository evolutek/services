#!/usr/bin/env python3

from evolutek.lib.interface import Interface
from evolutek.lib.settings import SIMULATION
from evolutek.lib.watchdog import Watchdog

if SIMULATION:
    from evolutek.simulation.simulator import read_config

from tkinter import Button, Canvas, Label

## TODO: Map obstacles
## TODO: Tims
## TODO: Detected opponents

class MatchInterface(Interface):

    def __init__(self):

        super().__init__('Match', 3)

        self.init_robot('pal')
        self.init_robot('pmi')

        self.match_status = None
        self.client.add_subscribe_cb('match_status', self.match_status_handler)
        self.match_status_watchdog = Watchdog(1, self.reset_match_status)#float(match_config['refresh']) * 2, self.reset_match_status)

        if SIMULATION:
            self.init_simulation()

        self.window.after(self.interface_refresh, self.update_interface)
        print('[MATCH NTERFACE] Window looping')
        self.window.mainloop()

    def reset_match_status(self):
        self.match_status = None

    def init_simulation(self):
        enemies = read_config('enemies')

        if enemies is None:
            return

        for enemy, config in enemies['robots'].items():
            self.robots[enemy] = {'telemetry' : None, 'size' : config['config']['robot_size_y'], 'color' : 'red'}
            self.client.add_subscribe_cb(enemy + '_telemetry', self.telemetry_handler)

    def match_status_handler(self, status):
        self.match_status_watchdog.reset()
        self.match_status = status

    def reset_match(self):
        try:
            self.cs.match.reset_match()
        except:
            print('[MATCH INTERFACE] Failed to reset match : %s' % str(e))

    # Init match interface
    def init_interface(self):

        # Close button
        close_button = Button(self.window, text='Close', command=self.close)
        close_button.grid(row=1, column=1)

        # Reset Button
        reset_button = Button(self.window, text='Reset Match', command=self.reset_match)
        reset_button.grid(row=1, column=3)

        # Map
        self.canvas = Canvas(self.window, width=3000 * self.interface_ratio, height= 2000 * self.interface_ratio)
        self.canvas.grid(row=4, column=1, columnspan=3)

        # PAL status
        self.pal_ai_status_label = Label(self.window)
        self.pal_ai_status_label.grid(row=2, column=1)

        # PMI
        self.pmi_ai_status_label = Label(self.window)
        self.pmi_ai_status_label.grid(row=3, column=1)

        # Color
        self.color_label = Label(self.window)
        self.color_label.grid(row=2, column=3)

        # Score
        self.score_label = Label(self.window)
        self.score_label.grid(row=3, column=3)

        # Match status
        self.match_status_label = Label(self.window)
        self.match_status_label.grid(row=2, column=2)

        # Match time
        self.match_time_label = Label(self.window)
        self.match_time_label.grid(row=3, column=2)

        self.canvas.create_image(1500 * self.interface_ratio, 1000 * self.interface_ratio, image=self.map)

    def update_interface(self):

        self.canvas.delete('all')
        self.canvas.create_image((3000 * self.interface_ratio) / 2, (2000 * self.interface_ratio) / 2, image=self.map)

        self.pal_ai_status_label.config(text="PAL status: %s" % self.get_robot_status('pal'))
        self.pmi_ai_status_label.config(text="PMI status: %s" % self.get_robot_status('pmi'))

        if self.match_status is not None:
            self.color_label.config(text="Color: %s" % self.match_status['color'], fg=self.match_status['color'])
            self.score_label.config(text="Score: %d" % self.match_status['score'])
            self.match_status_label.config(text="Match status: %s" % self.match_status['status'])
            self.match_time_label.config(text="Match time: %d" % self.match_status['time'])
        else:
            self.color_label.config(text="Color: %s" % 'Match not connected')
            self.score_label.config(text="Score: %s" % 'Match not connected')
            self.match_status_label.config(text="Match status: %s" % 'Match not connected')
            self.match_time_label.config(text="Match time: %s" % 'Match not connected')

        for robot in self.robots:
            self.print_robot(*self.robots[robot].values())

        self.print_path(self.paths['pal'], 'yellow', 'violet')
        self.print_path(self.paths['pmi'], 'violet', 'yellow')

        self.window.after(self.interface_refresh, self.update_interface)

def main():
    MatchInterface()

if __name__ == "__main__":
    main()
