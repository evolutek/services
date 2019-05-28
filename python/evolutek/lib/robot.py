#!/usr/bin/env python3

from functools import wraps
from threading import Event, Thread
from time import sleep
import asyncore
from math import pi

from cellaserv.client import RequestTimeout
from cellaserv.proxy import CellaservProxy
from cellaserv.service import AsynClient
from cellaserv.settings import get_socket

from evolutek.lib.point import Point
from evolutek.lib.settings import ROBOT
from evolutek.lib.watchdog import Watchdog

class Robot:

    # Holds the singleton of Robot
    _instance = None

    @classmethod
    def get_instance(cls, robot=None):
        if cls._instance is None:
            cls._instance = Robot(robot)
        return cls._instance

    # Wrapper
    def wrap_block(self, f):
        @wraps(f)
        def _f(*args, **kwargs):
            self.is_stopped.clear()
            if not self.tm.disabled:
                return

            watchdog = Watchdog(1, self.timeout_handler)
            watchdog.reset()

            f(*args, **kwargs)

            while not self.is_started.is_set() and not self.timeout.is_set():
                sleep(0.1)

            self.timeout.clear()
            if not self.is_started.is_set():
                return

            watchdog.stop()
            self.is_started.clear()

            self.is_stopped.wait()

            has_avoid = self.has_avoid.is_set()
            self.cs('log.robot', is_stopped=self.is_stopped.is_set(),
                        has_avoid=has_avoid)
            self.has_avoid.clear()
            return has_avoid
        return _f

    def __init__(self, robot=None):

        self.cs = CellaservProxy()

        # Current robot
        self.robot = robot if not robot is None else ROBOT
        self.tm = self.cs.trajman[self.robot]

        # Size of the robot and min dist from wall
        self.size_x = float(self.cs.config.get(section=self.robot, option='robot_size_x'))
        self.size_y = float(self.cs.config.get(section=self.robot, option='robot_size_y'))
        self.dist = ((self.size_x ** 2 + self.size_y ** 2) ** (1 / 2.0))

        # Side config
        self.color1 = self.cs.config.get(section='match', option='color1')
        self.side = False
        try:
            self.side = self.cs.match.get_color() != self.color1
        except Exception as e:
            print('[ROBOT] Failed to set color: %s' % (str(e)))

        self.side = False

        # Events
        self.is_stopped = Event()
        self.is_started = Event()
        self.has_avoid = Event()
        self.end_avoid = Event()
        self.timeout = Event()

        # AsynClient
        self.client = AsynClient(get_socket())
        self.client.add_subscribe_cb(self.robot + '_stopped', self.robot_stopped)
        self.client.add_subscribe_cb(self.robot + '_started', self.robot_started)
        self.client.add_subscribe_cb('match_color', self.color_change)
        self.client.add_subscribe_cb(self.robot + '_end_avoid', self.end_avoid_handler)

        # Blocking wrapper
        self.recalibration_block = self.wrap_block(self.tm.recalibration)
        self.goto_xy_block = self.wrap_block(self.tm.goto_xy)
        self.goto_theta_block = self.wrap_block(self.tm.goto_theta)
        self.curve_block = self.wrap_block(self.tm.curve)
        self.move_rot_block = self.wrap_block(self.tm.move_rot)
        self.move_trsl_block = self.wrap_block(self.tm.move_trsl)

        # Start the event listening thread
        self.client_thread = Thread(target=asyncore.loop)
        self.client_thread.daemon = True
        self.client_thread.start()

    ##########
    # Events #
    ##########

    def robot_started(self):
        self.is_started.set()

    def robot_stopped(self, has_avoid=False):
        if has_avoid.decode().split(' ')[1][0] == 't':
            self.has_avoid.set()
        self.is_stopped.set()

    def color_change(self, color):
        self.side = color != self.color1

    def end_avoid_handler(self):
        self.end_avoid.set()

    def timeout_handler(self):
        self.timeout.set()

    #########
    # Moves #
    #########

    def goto(self, x, y):
        return self.goto_xy_block(x, 1500 + (1500 - y) * (-1 if not self.side else 1))

    def goth(self, th):
        return self.goto_theta_block(th * (1 if not self.side else -1))

    def goto_avoid(self, x, y, timeout=0.0):
        while self.goto(x, y):
            self.wait_until(timeout=timeout)

    def goth_avoid(self, th, timeout=0.0):
        while self.goth(th):
            self.wait_until(timeout=timeout)

    # TODO: pgoto with path
    """
    def goto_with_path(self, x, y):
        delta = 5
        end = Point(x, y)
        pos = Point.from_dict(self.tm.get_position())
        path = [pos, end]
        while start.dist(pos) < delta:"""

    # TODO: Manage avoid
    # TODOL remove sleep after recalibration
    def recalibration(self,
                        x=True,
                        y=True,
                        side_x=(False, False),
                        side_y=(False, False),
                        decal_x=0,
                        decal_y=0,
                        init=False):

        speeds = self.tm.get_speeds()
        self.tm.free()
        self.tm.disable_avoid()

        # TODO: check speeds
        self.tm.set_trsl_max_speed(400)
        self.tm.set_trsl_acc(400)
        self.tm.set_trsl_dec(400)

        # init pos if necessary
        if init:
            self.tm.set_theta(0)
            self.tm.set_x(1000)
            self.tm.set_y(1000)

        if x:
            print('[ROBOT] Recalibration X')
            theta = pi if side_x[0] ^ side_x[1] else 0
            self.goth(theta)
            self.recalibration_block(sens=int(side_x[0]), decal=float(decal_x))
            sleep(2)
            pos = self.tm.get_position()
            print('[ROBOT] Robot position is x:%f y:%f theta:%f' %
                (pos['x'], pos['y'], pos['theta']))
            self.move_trsl_block(dest=self.dist - self.size_x, acc=200, dec=200, maxspeed=200, sens=not side_x[0])

        if y:
            print('[ROBOT] Recalibration Y')
            theta = -pi/2 if side_x[0] ^ side_y[0] else pi/2
            self.goth(theta * (-1 if self.side else 1))
            self.recalibration_block(sens=int(side_y[0]), decal=float(decal_y))
            sleep(2)
            pos = self.tm.get_position()
            print('[ROBOT] Robot position is x:%f y:%f theta:%f' %
                (pos['x'], pos['y'], pos['theta']))
            self.move_trsl_block(dest=self.dist - self.size_x, acc=200, dec=200, maxspeed=200, sens=not side_y[0])

        self.tm.set_trsl_max_speed(speeds['trmax'])
        self.tm.set_trsl_acc(speeds['tracc'])
        self.tm.set_trsl_dec(speeds['trdec'])
        self.tm.enable_avoid()

    # TODO : Add other actions

    #########
    # Avoid #
    #########
    def wait_until(self, timeout=0.0):
        watchdog = None

        if timeout > 0.0:
            watchdog = Watchdog(timeout, self.timeout_handler)
            watchdog.reset()

        while not self.end_avoid.is_set() and not self.timeout.is_set():
            sleep(0.1)

        if not watchdog is None:
            watchdog.stop()
            self.timeout.clear()
        self.end_avoid.clear()
