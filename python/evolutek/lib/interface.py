from cellaserv.proxy import CellaservProxy
from cellaserv.service import AsynClient
from cellaserv.settings import get_socket

from evolutek.lib.map.point import Point
from evolutek.lib.watchdog import Watchdog

import asyncore
from math import cos, sin, pi, degrees
from os import _exit
from signal import signal, SIGINT
from threading import Thread
from tkinter import *
from PIL import Image
from PIL import ImageTk

class Interface:

    def __init__(self, title, nb_lines=1):

        self.cs = CellaservProxy()
        self.client = AsynClient(get_socket())


        match_config = self.cs.config.get_section('match')
        self.interface_refresh = int(match_config['interface_refresh'])
        self.robot_size = float(match_config['robot_size'])
        self.color1 = match_config['color1']
        self.color2 = match_config['color2']
        self.timeout_robot = float(match_config['timeout_robot'])

        self.window = Tk()
        self.window.attributes('-fullscreen', True)
        self.window.bind('<Escape>',lambda e: self.close())
        self.window.title('%s Interface' % title)

        ratio_width = self.window.winfo_screenwidth() / 3000
        ratio_height = (self.window.winfo_screenheight() - (25 * nb_lines)) / 2000
        self.interface_ratio = min(ratio_width, ratio_height)

        img = Image.open('/etc/conf.d/map.png')
        img = img.resize((int(3000 * self.interface_ratio), int(2000 * self.interface_ratio)), Image.ANTIALIAS)
        self.map = ImageTk.PhotoImage(img)

        self.init_interface()
        print('[NTERFACE] Window created')

        self.ai_status = {}
        self.paths = {}
        self.robots = {}
        self.tmp = []

        self.moving_robot = None
        self.canvas.bind("<ButtonPress-1>", self.get_moving_robot)
        self.canvas.bind("<ButtonRelease-1>", self.set_moving_robot)

        # Start the event listening thread
        self.client_thread = Thread(target=asyncore.loop)
        self.client_thread.daemon = True
        self.client_thread.start()

        signal(SIGINT, self.close)


    """" ROBOT UTILITIES """

    def init_robot(self, robot):
        self.robots[robot] = {'telemetry' : None, 'size' : float(self.cs.config.get(section=robot, option='robot_size_y')), 'color' : 'orange'}
        self.client.add_subscribe_cb('%s_telemetry' % robot, self.telemetry_handler)

        self.ai_status[robot] = None
        self.client.add_subscribe_cb('%s_ai_status' % robot, self.ai_status_handler)

        self.paths[robot] = []
        self.client.add_subscribe_cb('%s_path' % robot, self.path_handler)

        setattr(self, '%s_watchdog' % robot, Watchdog(self.timeout_robot, self.reset_robot, [robot]))

        img = Image.open('/etc/conf.d/%s.png' % robot)
        new_size = int((self.robots[robot]['size'] + 35) * 2 * self.interface_ratio)
        img = img.resize((new_size, new_size), Image.ANTIALIAS)

        setattr(self, '%s_image' % robot, img)

    def reset_robot(self, robot):
        self.robots[robot]['telemetry'] = None
        self.ai_status[robot] = None

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

        print('[INTERFACE] Get moving robot %s' % robot)

    def set_moving_robot(self, event):
        if self.moving_robot is None:
            return

        x, y = event.y / self.interface_ratio, event.x / self.interface_ratio

        self.cs.trajman[self.moving_robot].goto_xy(x=x, y=y)

        print('[INTERFACE] Moving robot %s to %f %f' % (self.moving_robot, x, y))

        self.moving_robot = None

    def ai_status_handler(self, robot, status):
        getattr(self, '%s_watchdog' % robot).reset()
        if robot in self.ai_status:
            self.ai_status[robot] = status

    def path_handler(self, robot, path):
        self.paths[robot] = path

    def telemetry_handler(self, status, robot, telemetry):
        if status != 'failed':
            self.robots[robot]['telemetry'] = telemetry
        else:
            self.telemetry = None

        if robot in ['pal', 'pmi']:
            getattr(self, '%s_watchdog' % robot).reset()

    def get_robot_status(self, robot):
        text = '%s not connected' % robot
        if not self.ai_status[robot] is None:
            text = self.ai_status[robot]
        elif not self.robots[robot]['telemetry'] is None:
            text = 'AI not launched'

        return text


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

    def print_robot_image(self, robot, coords):

        if coords is None:
            return

        x = coords['y'] * self.interface_ratio
        y = coords['x'] * self.interface_ratio
        img = getattr(self, '%s_image' % robot)
        img = img.rotate(degrees(coords['theta']) - 90)
        self.tmp.append(ImageTk.PhotoImage(img))
        self.canvas.create_image(x, y, image=self.tmp[-1])

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
        print('[INTERFACE] Killing interface')
        self.window.destroy()
        _exit(0)

    def set_color(self, color):
        self.cs.match.set_color(color)
