#!/usr/bin/env python3

from enum import Enum
from functools import wraps
from threading import Event, Thread
from time import sleep
import asyncore
from math import pi
from time import sleep 

#from cellaserv.client import RequestTimeout
from cellaserv.proxy import CellaservProxy
from cellaserv.service import AsynClient
from cellaserv.settings import get_socket

from evolutek.lib.map.point import Point
from evolutek.lib.map.utils import convert_path_to_point, convert_path_to_dict
from evolutek.lib.settings import ROBOT
from evolutek.lib.watchdog import Watchdog

DELTA_POS = 15
DELTA_THETA = 0.1
TIMEOUT_PATH = 5
MOVE_BACK = 250

class Status(Enum):
    reached = 0
    unreached = 1
    has_avoid = 2
    unreachable = 3


class Robot:

    # Holds the singleton of Robot
    _instance = None

    @classmethod
    def get_instance(cls, robot=None):
        if cls._instance is None:
            cls._instance = Robot(robot)
        return cls._instance

    # Wrapper for moves
    # TODO: update watchod timer
    def wrap_block(self, f):
        @wraps(f)
        def _f(*args, **kwargs):
            self.is_stopped.clear()
            if not self.tm.disabled:
                return

            watchdog = Watchdog(1, self.timeout_handler)
            watchdog.reset()
            self.has_avoid.clear()

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


    def __init__(self, robot=None, match_end_cb=None):

        self.cs = CellaservProxy()

        # Current robot
        self.robot = robot if not robot is None else ROBOT
        self.tm = self.cs.trajman[self.robot]

        self.match_end_cb = match_end_cb

        # Size of the robot and min dist from wall
        self.size_x = float(self.cs.config.get(section=self.robot, option='robot_size_x'))
        self.size_y = float(self.cs.config.get(section=self.robot, option='robot_size_y'))
        self.dist = ((self.size_x ** 2 + self.size_y ** 2) ** (1 / 2.0))

        # Side config
        self.color1 = self.cs.config.get(section='match', option='color1')
        self.color = self.color1
        self.side = False
        try:
            self.color_change(self.cs.match.get_color())
        except Exception as e:
            print('[ROBOT] Failed to set color: %s' % (str(e)))

        # Events
        self.is_stopped = Event()
        self.is_started = Event()
        self.has_avoid = Event()
        self.end_avoid = Event()
        self.reset = Event()
        self._recalibration = Event()
        self.match_start = Event()
        self.match_end = Event()
        self.timeout = Event()
        self.telemetry = None

        # AsynClient
        self.client = AsynClient(get_socket())
        self.client.add_subscribe_cb(self.robot + '_stopped', self.robot_stopped)
        self.client.add_subscribe_cb(self.robot + '_started', self.robot_started)
        self.client.add_subscribe_cb('match_color', self.color_change)
        self.client.add_subscribe_cb(self.robot + '_end_avoid', self.end_avoid_handler)
        #self.client.add_subscribe_cb(self.robot + '_telemetry', self.telemetry_handler)
        self.client.add_subscribe_cb("match_start", self.match_start_handler)
        self.client.add_subscribe_cb("match_end", self.match_end_handler)
        self.client.add_subscribe_cb("%s_reset" % self.robot, self.reset_handler)
        self.client.add_subscribe_cb("%s_recalibration" % self.robot, self._recalibration_handler)

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

    def mirror_pos(self, x = None, y = None, theta = None):
        if y is not None:
            y = (y if not self.side else 3000 - y)
        if theta is not None:
            theta  = (theta if not self.side else -1 * theta)

        return (x, y, theta)


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
        self.color = color
        self.tm.set_mdb_config(yellow=self.side)

    def end_avoid_handler(self):
        self.end_avoid.set()

    def timeout_handler(self):
        self.timeout.set()

    def telemetry_handler(self, status, robot, telemetry):
        if status != 'failed':
            self.telemetry = telemetry
        else:
            self.telemetry = None

    def reset_handler(self):
        self.reset.set()

    def _recalibration_handler(self):
        self._recalibration.set()
        self.reset.set()

    def match_start_handler(self):
        self.match_start.set()

    def match_end_handler(self):
        self.match_end.set()
        if self.match_end_cb is not None:
            self.match_end_cb()


    ########
    # Sets #
    ########

    def set_x(self, x):
        self.tm.set_x(x)

    def set_y(self, y, mirror=True):
        if mirror:
            y = self.mirror_pos(y=y)[1]

        self.tm.set_y(y)

    def set_theta(self, theta, mirror=True):
        if mirror:
            theta = self.mirror_pos(theta=theta)[2]

        self.tm.set_theta(theta)



    def set_pos(self, x, y, theta=None, mirror=True):
        self.set_x(x)
        self.set_y(y, mirror)
        if not theta is None:
            self.set_theta(theta, mirror)


    #########
    # Moves #
    #########

    def goto(self, x, y, mirror=True):

        if mirror:
            y = self.mirror_pos(y=y)[1]

        if self.goto_xy_block(x, y):
            return Status.has_avoid

        #if self.telemetry is None:
        pos = self.tm.get_position()
        #else:
        #    pos = self.telemetry

        if Point(x=x, y=y).dist(Point(dict=pos)) < DELTA_POS:
            return Status.reached
        return Status.unreached

    def goth(self, theta, mirror=True):

        if mirror:
            theta = self.mirror_pos(theta=theta)[2]

        if self.goto_theta_block(theta):
            return Status.has_avoid

        #if self.telemetry is None:
        pos = self.tm.get_position()
        #else:
        #    pos = self.telemetry

        error = abs(theta - float(pos['theta']))
        if error > pi:
            error = error - (2 * pi)

        if abs(error) < DELTA_THETA:
            return Status.reached
        return Status.unreached

    def goto_avoid(self, x, y, timeout=0.0, nb_try=None, mirror=True):
        tried = 1
        status = self.goto(x, y, mirror)
        while (nb_try is None or tried <= nb_try) and status == Status.has_avoid:
            tried += 1
            self.wait_until(timeout=timeout)
            status = self.goto(x, y, mirror)

        return status

    def goth_avoid(self, theta, timeout=0.0, nb_try=None, mirror=True):
        tried = 1
        status = self.goth(theta, mirror)
        while (nb_try is None or tried <= nb_try) and status == Status.has_avoid:
            tried += 1
            self.wait_until(timeout=timeout)
            status = self.goth(theta, mirror)

        return status

    # TODO : Check if we have done the trsl
    def move_trsl_avoid(self, dest, acc, dec, maxspeed, sens, timeout=0.0, nb_try=None):
        tried = 1
        status = Status.has_avoid if self.move_trsl_block(dest, acc, dec, maxspeed, sens) else Status.reached

        while (nb_try is None or tried <= nb_try) and status == Status.has_avoid:
            tried += 1
            self.wait_until(timeout=timeout)
            status = Status.has_avoid if self.move_trsl_block(dest, acc, dec, maxspeed, sens) else Status.reached

        return status


    ###############
    # Pathfinding #
    ###############

    def update_path(self, path):

        print("[ROBOT] Updating path")

        new = []

        try:
            #if self.telemetry is None:
            pos = self.tm.get_position()
            #else:
            #    pos = self.telemetry

            new = self.cs.map.get_path(pos, path[-1].to_dict(), self.robot)
            new = convert_path_to_point(new)

            # Next point is near current pos
            if new[1].dist(new[0]) < DELTA_POS:
                new.pop(0)

        except Exception as e:
            print('[ROBOT] Failed to update path: %s' % str(e))

        return new

    def goto_with_path(self, x, y, mirror=True):

        if mirror:
            y = self.mirror_pos(y=y)[1]

        print('[ROBOT] Destination x: %d y: %d' % (x, y))
        path = [Point(dict=self.tm.get_position()), Point(x, y)]

        if path[1].dist(path[0]) < DELTA_POS:
            print("[ROBOT] Already at destination")
            return Status.reached

        while len(path) >= 2:

            if(not self.cs.map.is_path_valid(convert_path_to_dict(path), self.robot)):
                path = self.update_path(path)

            if len(path) < 2:
                print('[ROBOT] Destination unreachable')
                return Status.unreachable

            print('[ROBOT] Current pos is x: %d y: %d' % (path[0].x, path[0].y))

            self.is_stopped.clear()
            print('[ROBOT] Going to %s' % str(path[1]))
            self.tm.goto_xy(x=path[1].x, y=path[1].y)

            # While the robot is not stopped
            while not self.is_stopped.is_set():

                if(self.cs.map.is_path_valid(convert_path_to_dict(path), self.robot)):
                    sleep(0.1)
                    continue

                tmp_path = self.update_path(path)

                if len(tmp_path) < 2:
                    self.tm.stop_asap(1000, 20)
                    print('[ROBOT] Destination unreachable')
                    return Status.unreachable

                if tmp_path[1::] != path[1::]:
                    # Next point changed, need to stop
                    print("[ROBOT] Next point changed")
                    self.tm.stop_asap(1000, 20)
                    self.is_stopped.wait()
                else:
                    # TODO : manage refresh
                    sleep(0.1)

                path = tmp_path

            print("[ROBOT] Robot stopped")

            if self.has_avoid.is_set():
                self.move_back(MOVE_BACK)
            self.has_avoid.clear()

            # We are supposed to be stopped
            pos = Point(dict=self.tm.get_position())

            if pos.dist(path[1]) < DELTA_POS:
                # We reached next point (path[1])
                path.pop(0)
                path[0] = pos

        print('[ROBOT] Robot near destination')
        return Status.reached


    #################
    # Recalibration #
    #################

    # TODO remove sleep after recalibration
    # x/y => recalibration x or y
    # side_x/y:
    #     first value:  touches with front or back (True is front)
    #     second value: touches high or low coordinates wall (True is high)
    # decal: adds an offset if there is an obstacle
    # init: TODO
    # mirror: mirrors everything depending on the ally side
    def recalibration(self,
                        x=True,
                        y=True,
                        side_x=(False, False),
                        side_y=(False, False),
                        decal_x=0,
                        decal_y=0,
                        init=False,
                        mirror=True):

        speeds = self.tm.get_speeds()
        self.tm.free()

        self.tm.set_trsl_max_speed(100)
        self.tm.set_trsl_acc(300)
        self.tm.set_trsl_dec(300)

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
            sleep(0.5)

            #if self.telemetry is None:
            pos = self.tm.get_position()
            #else:
            #    pos = self.telemetry

            print('[ROBOT] Robot position is x:%f y:%f theta:%f' %
                (pos['x'], pos['y'], pos['theta']))
            self.move_trsl_block(dest=2*(self.dist - self.size_x), acc=200, dec=200, maxspeed=200, sens=not side_x[0])

        if y:
            print('[ROBOT] Recalibration Y')
            theta = -pi/2 if side_x[0] ^ side_y[0] else pi/2
            self.goth(theta)
            self.recalibration_block(sens=int(side_y[0]), decal=float(decal_y))
            sleep(0.5)

            #if self.telemetry is None:
            pos = self.tm.get_position()
            #else:
            #    pos = self.telemetry

            print('[ROBOT] Robot position is x:%f y:%f theta:%f' %
                (pos['x'], pos['y'], pos['theta']))
            self.move_trsl_block(dest=2*(self.dist - self.size_x), acc=200, dec=200, maxspeed=200, sens=not side_y[0])

        self.tm.set_trsl_max_speed(speeds['trmax'])
        self.tm.set_trsl_acc(speeds['tracc'])
        self.tm.set_trsl_dec(speeds['trdec'])


    """ GO HOME """
    def go_home(self, point, point_theta):
        self.goto(point.x, point.y)
        self.goth(point_theta)

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

        if self.timeout.is_set():
            return False

        if not watchdog is None:
            watchdog.stop()
            self.timeout.clear()

        self.end_avoid.clear()
        return True

    def move_back(self, dist):
        print('[ROBOT] Moving back')

        self.wait_until(timeout=3)

        pos = self.tm.get_position()
        side = self.tm.avoid_status()['side']

        print('[ROBOT] Move back direction: ' + str(side))
        if side is None:
            return

        if self.move_trsl_block(acc=200, dec=200, dest=dist, maxspeed=400, sens=int(side != 'front')):
            print('[ROBOT] Robot avoided, moving front')
            if self.move_trsl_block(acc=200, dec=200, dest=dist/2, maxspeed=400, sens=int(side == 'front')):
                return Status.has_avoid

        return Status.reached
