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

    # wrapper
    # TODO: update watchod timer
    def wrap_block(self, f):
        @wraps(f)
        def _f(*args, **kwargs):
            self.is_stopped.clear()
            if not self.tm.disabled:
                return
            f(*args, **kwargs)
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
        self.dist = ((self.robot_size_x() ** 2 + self.robot_size_y() ** 2) ** (1 / 2.0)) + 50

        # Side config
        self.color1 = self.cs.config.get(section='match', option='color1')
        self.side = False
        try:
            self.side = self.cs.match.get_color() != self.color1
        except Exception as e:
            print('[ROBOT] Failed to set color: %s' % (str(e)))

        # Events
        self.is_stopped = Event()
        self.has_avoid = Event()
        self.end_avoid = Event()
        self.timeout = Event()

        # AsynClient
        self.client = AsynClient(get_socket())
        self.client.add_subscribe_cb(self.robot + '_stopped', self.robot_stopped)
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
        return self.goto_xy_block(x, 1500 + (1500 - y) * -1 if not self.side else 1)

    def goth(self, th):
        return self.goto_theta_block(th * 1 if not self.side else -1)

    def goto_avoid(self, x, y, timeout=0.0):
        while self.goto(x, y):
            self.wait_until(timeout=timeout)

    def goth_avoid(self, th, timeout=0.0):
        while self.goth(th):
            self.wait_until(timeout=timeout)

    def update_path(self, path):
        updated = False
        try:
            tmp_path = self.cs.map.get_path(path[0].to_dict(), path[-1].to_dict())
            if len(tmp_path) >= 2 and Point.from_dict(tmp_path[1]) != path[1]):
                print('[ROBOT] Update Path')
                updated = True
                path.clear()
                for point in tmp_path:
                    path.append(Point.from_dict(point))
        except Exception as e:
            print('[ROBOT] Failed to update path: %s' % str(e))
            return False
        return updated

    # TODO: goto with path
    def goto_with_path(self, x, y):
        print('[ROBOT] Destination x: %d y: %d' % (x, y))
        delta = 5
        end = Point(x, y)
        pos = Point.from_dict(self.tm.get_position())
        path = [pos, end]
        while len(path) >= 2:
            print('[ROBOT] Current pos is x: %d y: %d' % (pos.x, pos.y))
            if pos.dist(path[1]) < delta:
                path.pop(0)
            self.update_path(path)
            self.is_stopped.clear()
            if not self.tm.disabled:
                return
            print('[ROBOT] Going to %s' % str(path[1]))
            self.tm.goto_xy(x=path[1].x, y=path[1].y)
            while not self.is_stopped.is_set():
                if self.update_path(path):
                    break;
                sleep(0.2)
            if self.has_avoid.is_set():
                print('[ROBOT] Robot has avoid')
                self.wait_until(timeout=3)
                if not self.end_avoid.is_set():
                    print('[ROBOT] Is going back')
                    if self.move_trsl_block(acc=200, dec=200, dest=150,
                        sens=int(self.tm.avoid_status['front'])):
                        print('[ROBOT] Going back again')
                        self.move_trsl_block(acc=200, dec=200, dest=50,
                            sens=int(self.tm.avoid_status['front']))
            pos = Point.from_dict(self.tm.get_position())
        print('[ROBOT] Robot reach destination')


    # TODO: Manage avoid
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
        self.tm.set_trsl_max_speed(200)
        self.tm.set_trsl_acc(200)
        self.tm.set_trsl_dec(200)

        # init pos if necessary
        if init:
            self.tm.set_theta(0)
            self.tm.set_x(1000)
            self.tm.set_y(1000)

        if x:
            print('[ROBOT] Recalibration X')
            self.goth(pi if side_x(0) ^ side_x(1) else 0)
            pos = self.recalibration_block(sens=int(side_x(0)), decal=float(decal_x))
            print('[ROBOT] Robot position is x: %f y: %f theta: %f' %
                (pos['recal_xpos'], pos['recal_ypos'], pos['recal_theta']))
            self.goto(
                x = pos['recal_xpos'] + dist * -1 if abs(pos['recal_theta'] - pi) < 0.1 else 1,
                y = pos['recal_ypos']))pos['recal_xpos']

        if y:
            print('[ROBOT] Recalibration y
            theta = pi/2 if side_x(0) ^ side_y(0) else -pi/2
            self.goth(theta * -1 if self.side else 1)
            pos = self.recalibration_block(sens=int(side_x(0)), decal=float(decal_x))
            print('[ROBOT] Robot position is x: %f y: %f theta: %f' %
                (pos['recal_xpos'], pos['recal_ypos'], pos['recal_theta']))
            self.goto(
                x = pos['recal_xpos'],
                y = pos['recal_ypos'] + dist * -1 if abs(pos['recal_theta'] + pi/2) < 0.1 else 1
            )

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

        while not end_avoid.is_set() and not self.timeout.is_set():
            sleep(0.1)

        if not watchdog is None:
            watchdog.stop()
            self.timeout.clear()
        self.end_avoid.clear()
