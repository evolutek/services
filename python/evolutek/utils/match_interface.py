#!/usr/bin/env python3

from cellaserv.proxy import CellaservProxy
from cellaserv.service import AsynClient
from cellaserv.settings import get_socket

from evolutek.lib.map.point import Point
from evolutek.lib.settings import SIMULATION
from evolutek.lib.watchdog import Watchdog

if SIMULATION:
    from evolutek.simulation.simulator import read_config

import asyncore
from math import cos, sin, pi
from os import _exit
from signal import signal, SIGINT
from threading import Thread
from tkinter import *
from PIL import Image
from PIL import ImageTk

from time import sleep

## TODO: Robots paths
## TODO: Map obstacles
## TODO: Tims
## TODO: Detected oppenents

class MatchInterface:

    def __init__(self):

        self.cs = CellaservProxy()

        match_config = self.cs.config.get_section('match')

        self.interface_refresh = int(match_config['interface_refresh'])
        self.robot_size = float(match_config['robot_size'])
        self.color1 = match_config['color1']
        self.color2 = match_config['color2']
        self.timeout_robot = float(match_config['timeout_robot'])

        self.window = Tk()
        self.window.attributes('-fullscreen', True)
        self.window.bind('<Escape>',lambda e: self.close())
        self.window.title('Match Interface')
        ratio_width = self.window.winfo_screenwidth() / 3000
        ratio_height = (self.window.winfo_screenheight() - 75) / 2000
        self.interface_ratio = min(ratio_width, ratio_height)

        img = Image.open('/etc/conf.d/map.png')
        img = img.resize((int(3000 * self.interface_ratio), int(2000 * self.interface_ratio)), Image.ANTIALIAS)
        self.map = ImageTk.PhotoImage(img)

        self.init_interface()

        print('[MATCH INTERFACE] Window created')

        self.client = AsynClient(get_socket())

        self.robots = {}
        self.ai_status = {}
        self.paths = {}
        self.init_robot('pal')
        self.init_robot('pmi')

        self.match_status = None
        self.client.add_subscribe_cb('match_status', self.match_status_handler)
        self.match_status_watchdog = Watchdog(float(match_config['refresh']) * 2, self.reset_match_status)

        if SIMULATION:
            self.init_simulation()

        # Start the event listening thread
        self.client_thread = Thread(target=asyncore.loop)
        self.client_thread.daemon = True
        self.client_thread.start()

        self.moving_robot = None
        self.canvas.bind("<ButtonPress-1>", self.get_moving_robot)
        self.canvas.bind("<ButtonRelease-1>", self.set_moving_robot)

        signal(SIGINT, self.close)

        self.window.after(self.interface_refresh, self.update_interface)
        self.window.mainloop()

    def init_robot(self, robot):
        self.robots[robot] = {'telemetry' : None, 'size' : float(self.cs.config.get(section=robot, option='robot_size_y')), 'color' : 'orange'}
        self.client.add_subscribe_cb('%s_telemetry' % robot, self.telemetry_handler)

        self.ai_status[robot] = None
        self.client.add_subscribe_cb('%s_ai_status' % robot, self.ai_status_handler)

        self.paths[robot] = []
        self.client.add_subscribe_cb('%s_path' % robot, self.path_handler)

        setattr(self, '%s_watchdog' % robot, Watchdog(self.timeout_robot, self.reset_robot, [robot]))

    def reset_robot(self, robot):
        self.robots[robot]['telemetry'] = None
        self.ai_status[robot] = None

    def reset_match_status(self):
        self.match_status = None

    def init_simulation(self):
        enemies = read_config('enemies')

        if enemies is None:
            return

        for enemy, config in enemies['robots'].items():
            self.robots[enemy] = {'telemetry' : None, 'size' : config['config']['robot_size_y'], 'color' : 'red'}
            self.client.add_subscribe_cb(enemy + '_telemetry', self.telemetry_handler)

    def get_moving_robot(self, event):

        x, y = event.y / self.interface_ratio, event.x / self.interface_ratio

        robot = None
        previous_dist = None
        for enemy, config in self.robots.items():
            if config['telemetry'] is None:
                continue
            dist = Point.dist_dict(config['telemetry'], {'x': x, 'y': y})
            if dist <= config['size'] and (robot is None or dist < previous_dist):
                robot = enemy
                previous_dist = dist

        self.moving_robot = robot

        print('[MATCH INTERFACE] Get moving robot %s' % robot)

    def set_moving_robot(self, event):
        if self.moving_robot is None:
            return

        x, y = event.y / self.interface_ratio, event.x / self.interface_ratio

        self.cs.trajman[self.moving_robot].goto_xy(x=x, y=y)

        print('[MATCH INTERFACE] Moving robot %s to %f %f' % (self.moving_robot, x, y))

        self.moving_robot = None

    """ EVENT HANDLERS """

    def match_status_handler(self, status):
        self.match_status_watchdog.reset()
        self.match_status = status

    def telemetry_handler(self, status, robot, telemetry):
        if status != 'failed':
            self.robots[robot]['telemetry'] = telemetry
        else:
            self.telemetry = None

        if robot in ['pal', 'pmi']:
            getattr(self, '%s_watchdog' % robot).reset()

    def ai_status_handler(self, robot, status):
        getattr(self, '%s_watchdog' % robot).reset()
        if robot in self.ai_status:
            self.ai_status[robot] = status

    def path_handler(self, robot, path):
        self.paths[robot] = path

    """ PRINT UTILITIES """

    def print_robot(self, robot, size, color):

        if robot is None:
            return

        if 'theta' in robot:
            x = robot['y'] * self.interface_ratio
            y = robot['x'] * self.interface_ratio
            size *= self.interface_ratio

            points = []
            points.append((x - size, y - size))
            points.append((x + size, y - size))
            points.append((x + size, y + size))
            points.append((x - size, y + size))

            cos_val = cos(pi/2 - robot['theta'])
            sin_val = sin(pi/2 - robot['theta'])

            new_points = []
            for point in points:
                new_points.append((
                    (point[0] - x) * cos_val - (point[1] - y) * sin_val + x,
                    (point[0] - x) * sin_val + (point[1] - y) * cos_val + y
                ))

            self.canvas.create_polygon(new_points, fill=color)
            return

        self.canvas.create_rectangle(
            (robot['y'] - size) * self.interface_ratio,
            (robot['x'] - size) * self.interface_ratio,
            (robot['y'] + size) * self.interface_ratio,
            (robot['x'] + size) * self.interface_ratio,
            width=2, fill=color)

    def print_path(self, path, color_path, color_point):
        size = 10 * self.interface_ratio
        for i in range(1, len(path)):
            p1 = path[i - 1]
            p2 = path[i]

            self.canvas.create_line(p1['y'] * self.interface_ratio, p1['x'] * self.interface_ratio,
                p2['y'] * self.interface_ratio, p2['x'] * self.interface_ratio, width=size, fill=color_path)

        for p in path:
            x1 = (p['y'] - size) * self.interface_ratio
            x2 = (p['y'] + size) * self.interface_ratio
            y1 = (p['x'] - size) * self.interface_ratio
            y2 = (p['x'] + size) * self.interface_ratio
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=color_point)

    """ INTERFACE UTILITIES """

    def close(self, signal_received=None, frame=None):
        print('[MATCH_INTERFACE] Killing interface')
        self.window.destroy()
        _exit(0)

    # Update
    def set_color(self, color):
        pass
        self.match.set_color(color)

    # Update
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

        # PAL AI STATUS
        text = 'PAL not connected'
        if not self.ai_status['pal'] is None:
            text = self.ai_status['pal']
        elif not self.robots['pal']['telemetry'] is None:
            text = 'AI not launched'
        self.pal_ai_status_label.config(text="PAL status: %s" % text)

        # PMI AI STATUS
        text = 'PMI not connected'
        if not self.ai_status['pmi'] is None:
            text = self.ai_status['pmi']
        elif not self.robots['pmi']['telemetry'] is None:
            text = 'AI not launched'
        self.pmi_ai_status_label.config(text="PMI status: %s" % text)

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
