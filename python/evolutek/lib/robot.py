#!/usr/bin/env python3

## TODO: goto_with path

from enum import Enum
from functools import wraps
from threading import Event, Thread
from time import sleep
import asyncore
from math import pi

from cellaserv.client import RequestTimeout
from cellaserv.proxy import CellaservProxy
from cellaserv.service import AsynClient
from cellaserv.settings import get_socket

from evolutek.lib.map.point import Point
from evolutek.lib.map.utils import convert_path_to_point
from evolutek.lib.settings import ROBOT
from evolutek.lib.watchdog import Watchdog

DELTA_POS = 5
DELTA_THETA = 0.1
TIMEOUT_PATH = 5

class Status(Enum):
    reached = 0
    unreached = 1
    has_avoid = 2
    unreachable = 3

# TODO: manage collision

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

        # Events
        self.is_stopped = Event()
        self.is_started = Event()
        self.has_avoid = Event()
        self.end_avoid = Event()
        self.timeout = Event()
        self.telemetry = None

        # AsynClient
        self.client = AsynClient(get_socket())
        self.client.add_subscribe_cb(self.robot + '_stopped', self.robot_stopped)
        self.client.add_subscribe_cb(self.robot + '_started', self.robot_started)
        self.client.add_subscribe_cb('match_color', self.color_change)
        self.client.add_subscribe_cb(self.robot + '_end_avoid', self.end_avoid_handler)
        self.client.add_subscribe_cb(self.robot + '_telemetry', self.telemetry_handler)

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
        if has_avoid:
            self.has_avoid.set()
        self.is_stopped.set()

    def color_change(self, color):
        self.side = color != self.color1

    def end_avoid_handler(self):
        self.end_avoid.set()

    def timeout_handler(self):
        self.timeout.set()

    def telemetry_handler(self, status, robot, telemetry):
        if status != 'failed':
            self.telemetry = telemetry
        else:
            self.telemetry = None

    ########
    # Sets #
    ########

    def set_x(self, x):
        self.tm.set_x(x)

    def set_y(self, y):
        self.tm.set_y(1500 + (1500 - y) * (-1 if not self.side else 1))

    def set_theta(self, theta):
        self.tm.set_theta(theta * (1 if not self.side else -1))

    def set_pos(self, x, y, theta=None):
        self.set_x(x)
        self.set_y(y)
        if not theta is None:
            self.set_theta(theta)

    #########
    # Moves #
    #########

    def goto(self, x, y):
        if self.goto_xy_block(x, 1500 + (1500 - y) * (-1 if not self.side else 1)):
            return Status.has_avoid

        if self.telemetry is None:
            pos = self.tm.get_position()
        else:
            pos = self.telemetry

        print(pos)

        if Point(x=x, y=y).dist(Point(dict=pos)) < DELTA_POS:
            return Status.unreached
        return Status.reached

    def goth(self, th):
        if self.goto_theta_block(th * (1 if not self.side else -1)):
            return Status.has_avoid

        if self.telemetry is None:
            pos = self.tm.get_position()
        else:
            pos = self.telemetry

        if abs(th - float(pos['theta'])) < DELTA_THETA:
            return Status.unreached
        return Status.reached

    def goto_avoid(self, x, y, timeout=0.0, nb_try=None):
        tried = 1
        status = self.goto(x, y)
        while (not nb_try is None and tried < nb_try) and status == Status.has_avoid:
            tried += 1
            self.wait_until(timeout=timeout)
            status = self.goto(x, y)

        return status

    def goth_avoid(self, th, timeout=0.0, nb_try=None):
        tried = 1
        status = self.goth(th)
        while (not nb_try is None and tried < nb_try) and status == Status.has_avoid:
            tried += 1
            self.wait_until(timeout=timeout)
            status = self.goth(th)

        return status

    def move_trsl_avoid(self, dest, acc, dec, maxspeed, sens, timeout=0.0, nb_try=None):
        tried = 1
        status = self.move_trsl_block(dest, acc, dec, maxspeed, sens)
        while (not nb_try is None and tried < nb_try) and status == Status.has_avoid:
            tried += 1
            self.wait_until(timeout=timeout)
            status = self.move_trsl_block(dest, acc, dec, maxspeed, sens)

        return status

    def update_path(self, path):
        new = []

        try:
            computed = 0
            while computed < TIMEOUT_PATH and len(new) < 2:
                # Ask Map for path between current pos and end point

                if self.telemetry is None:
                    pos = self.tm.get_position()
                else:
                    pos = self.telemetry

                new = self.cs.map.get_path(pos, path[-1].to_dict())

                if len(path) < 2:
                    continue

                new = convert_path_to_point(new)

                if new[1].dist(new[0]) < DELTA_POS:
                    new.pop(0)

        except Exception as e:
            print('[ROBOT] Failed to update path: %s' % str(e))

        return new


    # TODO: debug move back
    # TODO: Manage Avoid
    def goto_with_path(self, x, y):
        print('[ROBOT] Destination x: %d y: %d' % (x, y))

        #if self.telemetry is None:
        pos = self.tm.get_position()
        #else:
        #    pos = self.telemetry

        path = [Point(dict=pos), Point(x=x, y=y)]

        while len(path) > 1:

            # Try to update path
            path = self.update_path(path)

            if len(path) < 2:
                print('[ROBOT] Destination unreachable')
                return Status.unreachable

            print('[ROBOT] Current pos is x: %d y: %d' % (path[0].x, path[0].y))

            for p in path:
                print(p)

            self.is_stopped.clear()
            if not self.tm.disabled:
                # Can't move, Trajman is disabled
                return

            print('[ROBOT] Going to %s' % str(path[1]))
            self.tm.goto_xy(x=path[1].x, y=path[1].y)

            # While the robot is not stopped
            while not self.is_stopped.is_set():
                stopped = False

                tmp_path = self.update_path(path)

                if len(tmp_path) < 2:
                    self.tm.stop_asap(1000, 20)
                    print('[ROBOT] Destination unreachable')
                    return Status.unreachable

                if tmp_path[1::] != path[1::]:
                    # Next point changed, need to stop
                    self.tm.stop_asap(1000, 20)
                    stopped = True

                path = tmp_path

                if stopped:
                    # If we stopped the robot, we wait for it
                    self.is_stopped.wait()

            # TODO: Avoid management
            """if self.has_avoid.is_set():
                print('[ROBOT] Robot has avoid')
                self.wait_until(timeout=3)
                if not self.end_avoid.is_set():
                    print('[ROBOT] Is going back')
                    side = self.tm.avoid_status()['back']
                    if self.move_trsl_block(acc=200, dec=200, dest=150, maxspeed=400, sens=int(side)):
                        print('[ROBOT] Going back again')
                        self.move_trsl_block(acc=200, dec=200, dest=50, maxspeed=400, sens=int(not side))"""

            # We are supposed to be stopped
            #if self.telemetry is None:
            pos = self.tm.get_position()
            #else:
            #    pos = self.telemetry

            if Point(dict=pos).dist(path[1]) < DELTA_POS:
                # We reached next point (path[1])
                path.pop(0)
                path[0] = pos

        print('[ROBOT] Robot near destination')
        return Status.reached

    # TODO remove sleep after recalibration
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
            self.tm.disable_avoid()
            self.recalibration_block(sens=int(side_x[0]), decal=float(decal_x))
            sleep(0.5)

            if self.telemetry is None:
                pos = self.tm.get_position()
            else:
                pos = self.telemetry

            print('[ROBOT] Robot position is x:%f y:%f theta:%f' %
                (pos['x'], pos['y'], pos['theta']))
            self.tm.enable_avoid()
            self.move_trsl_block(dest=self.dist - self.size_x, acc=200, dec=200, maxspeed=200, sens=not side_x[0])

        if y:
            print('[ROBOT] Recalibration Y')
            theta = -pi/2 if side_x[0] ^ side_y[0] else pi/2
            self.goth(theta * (-1 if self.side else 1))
            self.tm.disable_avoid()
            self.recalibration_block(sens=int(side_y[0]), decal=float(decal_y))
            sleep(0.5)

            if self.telemetry is None:
                pos = self.tm.get_position()
            else:
                pos = self.telemetry

            print('[ROBOT] Robot position is x:%f y:%f theta:%f' %
                (pos['x'], pos['y'], pos['theta']))
            self.tm.enable_avoid()
            self.move_trsl_block(dest=self.dist - self.size_x, acc=200, dec=200, maxspeed=200, sens=not side_y[0])

        self.tm.set_trsl_max_speed(speeds['trmax'])
        self.tm.set_trsl_acc(speeds['tracc'])
        self.tm.set_trsl_dec(speeds['trdec'])

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
