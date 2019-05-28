#!/usr/bin/env python3

from functools import wraps
from threading import Event, Thread
from time import sleep
import asyncore
import math

from cellaserv.client import RequestTimeout
from cellaserv.proxy import CellaservProxy
from cellaserv.service import AsynClient
from cellaserv.settings import get_socket
from evolutek.lib.settings import ROBOT

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
            f(*args, **kwargs)
            self.is_stopped.wait()
            self.cs('log.robot', is_stopped=self.is_stopped.is_set(),
                        has_avoid=self.has_avoid.is_set())
            self.has_avoid.clear()
        return _f

    def __init__(self, robot=None):

        self.cs = CellaservProxy()

        # Current robot
        self.robot = robot if not robot is None else ROBOT
        self.tm = self.cs.trajman[self.robot]

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

        # AsynClient
        self.client = AsynClient(get_socket())
        self.client.add_subscribe_cb(ROBOT + '_stopped', self.robot_stopped)
        self.client.add_subscribe_cb('match_color', self.color_change)

        # Blocking wrapper
        self.recalibration_block = self.wrap_block(self.recalibration)
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
        if has_avoid:
            self.has_avoid.set()
        self.is_stopped.set()

    def color_change(self, color):
        self.side = color != self.color1

    #########
    # Moves #
    #########

    # TODO: GET ACTUATORS RECALIBRATION
    def recalibration(self, sens):
        try:
            self.tm.recalibration(sens=sens)
        except RequestTimeout:  # Recalibration will timeout
            pass

    def goto(self, x, y):
        return self.goto_xy_block(x, 1500 + (1500 - y) * self.side)

    def goth(self, th):
        return self.goto_theta_block(th * -self.side)

    # TODO: Add other trajman actions
