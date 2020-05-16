#!/usr/bin/env python3

from evolutek.lib.interface import Interface
from evolutek.lib.map.point import Point
from evolutek.lib.map.tim import DebugMode
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

        self.map_enabled = False
        self.tim_enabled = False
        self.tim_debug = 0
        self.tim_scans = []
        self.tim_merge = []
        self.tim_detected_robots = []

        super().__init__('Match', 3)

        try:
            self.tim_debug = self.cs.map.get_debug_mode()
        except Exception as e:
            print('[MATCH INTERFACE] Failed to get debug mode: %s' % str(e))
        self.client.add_subscribe_cb('tim_debug_mode', self.tim_debug_mode_handler)
        self.client.add_subscribe_cb('tim_scans', self.tim_scans_handler)
        self.client.add_subscribe_cb('tim_merge', self.tim_merge_handler)
        self.client.add_subscribe_cb('tim_detected_robots', self.tim_detected_robots_handler)
        self.tim_watchdog = Watchdog(1, self.reset_tim) # TODO : Use tims refresh

        self.init_robot('pal')
        self.init_robot('pmi')

        self.obstacles = []
        try:
            self.obstacles = self.cs.map.get_obstacles()
        except Exception as e:
            print('[MATCH INTERFACE] Failed to get obstacles: %s' % str(e))
        self.client.add_subscribe_cb('obstacles', self.map_obstacles_handler)

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

    def tim_debug_mode_handler(self, mode):
        self.tim_debug = int(mode)

    def tim_scans_handler(self, scans):
        self.tim_watchdog.reset()
        self.tim_scans = scans

    def tim_merge_handler(self, merge):
        self.tim_watchdog.reset()
        self.tim_merge = merge

    def tim_detected_robots_handler(self, robots):
        self.tim_watchdog.reset()
        self.tim_robots = robots

    def reset_tim(self):
        self.tim_scans = []
        self.tim_merge = []
        self.tim_detected_robots = []

    def map_obstacles_handler(self, obstacles):
        self.obstacles = []

    def match_status_handler(self, status):
        self.match_status_watchdog.reset()
        self.match_status = status

    def reset_match(self):
        try:
            self.cs.match.reset_match()
        except Exception as e:
            print('[MATCH INTERFACE] Failed to reset match : %s' % str(e))

    def enable_map(self):
        self.map_enabled = not self.map_enabled

    def enable_tim(self):
        self.tim_enabled = not self.tim_enabled

    def change_debug_tim(self):
        if not self.tim_enabled:
            return

        tim_debug = (self.tim_debug + 1) % len(list(DebugMode))
        try:
            self.cs.map.set_debug_mode(tim_debug)
        except Exception as e:
            print("[MATCH INTERFACE] Failed to set TIMs debug mode: %s" % str(e))

    def print_polygon(self, points, color):

        for i in range(1, len(points)):
            p1 = Point(dict=points[i - 1])
            p2 = Point(dict=points[i])

            self.canvas.create_line(p1.y * self.interface_ratio, p1.x * self.interface_ratio,
                p2.y * self.interface_ratio, p2.x * self.interface_ratio, width=5, fill=color)

        for p in points:
            point = Point(dict=p)
            x1 = (point.y - 10) * self.interface_ratio
            x2 = (point.y + 10) * self.interface_ratio
            y1 = (point.x - 10) * self.interface_ratio
            y2 = (point.x + 10) * self.interface_ratio
            self.canvas.create_rectangle(x1, y1, x2, y2, fill='violet')

    def print_tims(self, tims):
        pass

    def print_merge(self, merge):
        pass

    # Init match interface
    def init_interface(self):

        # Close button
        close_button = Button(self.window, text='Close', command=self.close)
        close_button.grid(row=1, column=1)

        # Reset Button
        reset_button = Button(self.window, text='Reset Match', command=self.reset_match)
        reset_button.grid(row=1, column=3)

        # Map Button
        self.map_button = Button(self.window, text='Display Map', command=self.enable_map, bg='green' if self.map_enabled else 'red')
        self.map_button.grid(row=1, column=4)

        # TIM enable Button
        self.tim_enable_button = Button(self.window, text='Display TIM', command=self.enable_tim, bg='green' if self.tim_enabled else 'red')
        self.tim_enable_button.grid(row=2, column=4)

        # TIM debug Button
        self.tim_debug_button = Button(self.window, text='Change TIM Debug level: %s' % list(DebugMode)[self.tim_debug].name, command=self.change_debug_tim, bg='green' if self.tim_enabled else 'red')
        self.tim_debug_button.grid(row=3, column=4)

        # Map
        self.canvas = Canvas(self.window, width=3000 * self.interface_ratio, height= 2000 * self.interface_ratio)
        self.canvas.grid(row=4, column=1, columnspan=4)

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
            if robot in ['pal', 'pmi']:
                self.print_robot_image(robot, self.robots[robot]['telemetry'])
            else:
                if not self.tim_enabled:
                    self.print_robot(*self.robots[robot].values())

        if self.tim_enabled:
            if DebugMode(self.tim_debug) == DebugMode.normal:
                for robot in self.tim_robots:
                    self.print_robot(robot, self.robot_size, 'red')
            if DebugMode(self.tim_debug) == DebugMode.debug_tims:
                self.print_tims(self.tim_scans)
            elif DebugMode(self.tim_debug) == DebugMode.debug_merge:
                self.print_merge(self.tim_merge)

        self.print_path(self.paths['pal'], 'yellow', 'violet')
        self.print_path(self.paths['pmi'], 'violet', 'yellow')

        self.map_button.config(bg='green' if self.map_enabled else 'red')
        self.tim_enable_button.config(bg='green' if self.tim_enabled else 'red')
        self.tim_debug_button.config(text='Change TIM Debug level: %s' % list(DebugMode)[self.tim_debug].name, bg='green' if self.tim_enabled else 'red')

        if self.map_enabled:
            for poly in self.obstacles:
                self.print_polygon(poly, 'grey')

        self.window.after(self.interface_refresh, self.update_interface)

def main():
    MatchInterface()

if __name__ == "__main__":
    main()
