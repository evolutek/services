#!/usr/bin/env python3

from cellaserv.proxy import CellaservProxy
from cellaserv.service import AsynClient
from cellaserv.settings import get_socket

from evolutek.lib.map.point import Point
from evolutek.lib.settings import SIMULATION

if SIMULATION:
    from evolutek.simulation.simulator import read_config

import asyncore
from math import cos, sin, pi
from os import _exit
from threading import Thread
from tkinter import *
from PIL import Image
from PIL import ImageTk

from time import sleep

## TODO: AI status

class MatchInterface:

    def __init__(self):

        self.cs = CellaservProxy()

        match_interface_config = self.cs.config.get_section('match')

        self.interface_refresh = int(match_interface_config['interface_refresh'])
        self.robot_size = float(match_interface_config['robot_size'])
        self.color1 = match_interface_config['color1']
        self.color2 = match_interface_config['color2']

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

        self.robots = {}

        self.init_interface()

        print('[MATCH INTERFACE] Window created')

        self.client = AsynClient(get_socket())
        self.robots['pal'] = {'telemetry' : None, 'size' : float(self.cs.config.get(section='pal', option='robot_size_y')), 'color' : 'orange'}
        self.client.add_subscribe_cb('pal_telemetry', self.telemetry_handler)
        self.robots['pmi'] = {'telemetry' : None, 'size' : float(self.cs.config.get(section='pmi', option='robot_size_y')), 'color' : 'orange'}
        self.client.add_subscribe_cb('pmi_telemetry', self.telemetry_handler)

        if SIMULATION:
            self.init_simulation()

        # Start the event listening thread
        self.client_thread = Thread(target=asyncore.loop)
        self.client_thread.daemon = True
        self.client_thread.start()

        self.moving_robot = None
        self.canvas.bind("<ButtonPress-1>", self.get_moving_robot)
        self.canvas.bind("<ButtonRelease-1>", self.set_moving_robot)

        self.window.after(self.interface_refresh, self.update_interface)
        self.window.mainloop()

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

    def telemetry_handler(self, status, robot, telemetry):

        if status != 'failed':
            self.robots[robot]['telemetry'] = telemetry
        else:
            self.telemetry = None

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

    def close(self):
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

        status = None
        try:
            status= self.cs.match.get_status()
        except Exception as e:
            print('[MATCH INTERFACE] Failed to get match status: %s' % str(e))

        self.canvas.delete('all')
        self.canvas.create_image((3000 * self.interface_ratio) / 2, (2000 * self.interface_ratio) / 2, image=self.map)

        # TODO : display match not connected
        if status is not None:

            # PAL AI STATUS
            # TODO : Update
            text = 'PAL not connected'
            if not status['pal_ai_status'] is None:
                text = status['pal_ai_status']
            elif not status['pal_telemetry'] is None:
                text = 'AI not launched'
            self.pal_ai_status_label.config(text="PAL status: %s" % text)

            # PMI AI STATUS
            # TODO : Update
            text = 'PMI not connected'
            if not status['pmi_ai_status'] is None:
                text = status['pmi_ai_status']
            elif not status['pmi_telemetry'] is None:
                text = 'AI not launched'
            self.pmi_ai_status_label.config(text="PMI status: %s" % text)

            self.color_label.config(text="Color: %s" % status['color'], fg=status['color'])
            self.score_label.config(text="Score: %d" % status['score'])
            self.match_status_label.config(text="Match status: %s" % status['status'])
            self.match_time_label.config(text="Match time: %d" % status['time'])

        # TODO: Update
        """robots = []
        try:
            robots = self.cs.map.get_opponnents()
        except Exception as e:
            print('[MATCH INTERFACE] Failed to get opponents: %s' % str(e))"""

        for robot in self.robots:
            self.print_robot(*self.robots[robot].values())

        # TODO: Manage path
        #self.print_path(self.pal_path, 'yellow', 'violet')
        #self.print_path(self.pmi_path, 'violet', 'yellow')

        self.window.after(self.interface_refresh, self.update_interface)

def main():
    MatchInterface()

if __name__ == "__main__":
    main()
