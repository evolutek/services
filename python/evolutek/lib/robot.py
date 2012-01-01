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
import evolutek.lib.settings
from evolutek.lib.match import get_side


class Robot:

    # Holds the singleton of Robot
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = Robot()
        return cls._instance

    # Wrappers

    def wrap_block(self, f):
        @wraps(f)
        def _f(*args, **kwargs):
            self.is_stopped.clear()
            f(*args, **kwargs)
            self.is_stopped.wait()

        return _f

    def wrap_block_avoid(self, f):
        """Avoid no. 1"""

        @wraps(f)
        def _f(*args, **kwargs):
            self.is_stopped.clear()
            f(*args, **kwargs)
            while not self.is_stopped.is_set():
                self.robot_must_stop.wait()
                self.cs('log.robot', is_stopped=self.is_stopped.is_set(),
                        robot_must_stop=self.robot_must_stop.is_set(),
                        robot_near=self.robot_near_event.is_set())

                if not self.robot_near_event.is_set():
                    # The robot stopped because it completed the move
                    break
                else:
                    self.cs('log.robot', msg='Robot evitement')
                    self.tm.free()
                    # Wait for the other robot to leave
                    self.robot_far_event.wait()
                    # Then retry the operation
                    f(*args, **kwargs)
        return _f

    def __init__(self, robot=None, proxy=None):
        """
        Create a new robot object.

        :param str robot: The name of the robot you want to control
        """

        self.robot = robot if robot is not None else evolutek.lib.settings.ROBOT
        self.cs = proxy if proxy is not None else CellaservProxy()
        self.tm = self.cs.trajman[self.robot]
        self.side = get_side(proxy=self.cs)

        # Events

        self.is_stopped = Event()
        self.robot_near_event = Event()
        self.robot_far_event = Event()
        self.robot_must_stop = Event()

        self.client = AsynClient(get_socket())
        self.client.add_subscribe_cb(self.robot + '_stopped', self.robot_stopped)
        self.client.add_subscribe_cb(self.robot + '_near', self.robot_near)
        self.client.add_subscribe_cb(self.robot + '_far', self.robot_far)

        # Blocking wrappers

        self.recalibration_block = self.wrap_block(self.recalibration)
        self.goto_xy_block = self.wrap_block(self.tm.goto_xy)
        self.goto_theta_block = self.wrap_block(self.tm.goto_theta)
        self.curve_block = self.wrap_block(self.tm.curve)
        self.move_rot_block = self.wrap_block(self.tm.move_rot)
        self.move_trsl_block = self.wrap_block(self.tm.move_trsl)

        self.goto_xy_block_avoid = self.wrap_block_avoid(self.tm.goto_xy)
        self.goto_theta_block_avoid = self.wrap_block_avoid(self.tm.goto_theta)
        self.move_rot_block_avoid = self.wrap_block_avoid(self.tm.move_rot)
        self.move_trsl_block_avoid = self.wrap_block_avoid(self.tm.move_trsl)

        # Start the event listening thread

        self.client_thread = Thread(target=asyncore.loop)
        self.client_thread.daemon = True
        self.client_thread.start()

    ##########
    # Events #
    ##########

    def robot_stopped(self):
        self.is_stopped.set()
        self.robot_must_stop.set()

    def robot_near(self):
        self.robot_near_event.set()
        self.robot_must_stop.set()
        self.robot_far_event.clear()

    def robot_far(self):
        self.robot_far_event.set()
        self.robot_near_event.clear()
        self.robot_must_stop.clear()

    #########
    # Moves #
    #########

    def recalibration(self, sens):
        try:
            self.tm.recalibration(sens=sens)
        except RequestTimeout:  # Recalibration will timeout
            pass

    def goto(self, x, y):
        return self.goto_xy_block(x, 1500 + (1500 - y) * self.side)

    def goth(self, th):
        return self.goto_theta_block(th * -self.side)
