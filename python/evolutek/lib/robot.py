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


class Robot:

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

    def __init__(self, robot):
        """
        Create a new robot object.

        :param str robot: The name of the robot you want to control
        """

        self.robot = robot

        self.cs = CellaservProxy()
        self.tm = self.cs.trajman[robot]

        # Events

        self.is_stopped = Event()
        self.robot_near_event = Event()
        self.robot_far_event = Event()
        self.robot_must_stop = Event()

        self.client = AsynClient(get_socket())
        self.client.add_subscribe_cb(robot + '_stopped', self.robot_stopped)
        self.client.add_subscribe_cb(robot + '_near', self.robot_near)
        self.client.add_subscribe_cb(robot + '_far', self.robot_far)

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

    def recalibration(self, sens):
        try:
            self.print(self.tm.recalibration(sens=sens))
        except RequestTimeout: # Recalibration will timeout
            pass

    #########
    # Moves #
    #########

    def find_position(self, side: int):
        """
        find_position(1 or -1) make the robot find it position by touching
        the walls.
        """
        self.tm.free()
        speeds = self.tm.get_speeds()
        self.tm.set_theta(theta=0)
        self.tm.set_trsl_max_speed(maxspeed=200)
        self.tm.set_trsl_acc(acc=200)
        self.tm.set_trsl_dec(dec=200)
        self.tm.set_x(x=1000)
        self.tm.set_y(y=1000)

        print("Recalibration X")
        self.recalibration_block(0)
        print("X pos found!")
        self.cs('beep_ok')
        sleep(1)

        self.goto_xy_block(x=470, y=1000)
        self.goto_theta_block(theta=math.pi / 2 * -side)

        print("Recalibration Y")
        self.recalibration_block(0)
        print("Y pos found!")
        self.cs('beep_ok')
        sleep(1)

        self.goto_xy_block(x=470, y=1500 + 1200*side)
        sleep(.5)
        self.goto_xy_block(x=410, y=1500 + 1310*side)

        self.tm.set_trsl_max_speed(maxspeed=speeds['trmax'])
        self.tm.set_trsl_acc(acc=speeds['tracc'])
        self.tm.set_trsl_dec(dec=speeds['trdec'])

        print("Setup done")
        self.cs('beep_ready')

default_robot = Robot(evolutek.lib.settings.ROBOT)
