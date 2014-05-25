#!/usr/bin/env python3

from collections import namedtuple
import random
import threading
import time

from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service, ConfigVariable

Point = namedtuple('Point', ['x', 'y', 'theta'])

class Tracked:

    internal_id = 0

    def __init__(self, point):
        self.location = point

        self.name = "PLIPPE {}".format(self.internal_id)
        self.internal_id += 1

        self.last_seen = time.time()
        self.is_evolutek = False

    def seen(self):
        """Update when the robot was last seen."""
        self.last_seen = time.time()

    def rename(self, name):
        """Change the robot name."""
        self.name = name

class Tracking(Service):

    color = ConfigVariable(section='match', option='color')
    half_life = ConfigVariable(section='tracking', option='half_life',
            coerc=float)
    detect_pal = ConfigVariable(section='tracking', option='detect_pal',
            coerc=eval)
    detect_pmi = ConfigVariable(section='tracking', option='detect_pmi',
            coerc=eval)

    def __init__(self):
        super().__init__()
        self.cs = CellaservProxy()

        self.robots_lock = threading.Lock()
        self.robots = []

    def is_dead(self, obj):
        """Return True if the object is dead."""
        return (time.time() - obj.last_seen) > self.half_life()

    @Service.thread
    def prune_dead_robots(self):
        """prune_dead_robots() remove robots that are too old."""

        self.robots_lock.acquire()
        self.robots = [obj for obj in self.robots if not self.is_dead(obj)]
        self.robots_release.release()


    # Events listened, update internal representation of the robots

    @Service.event('log.monitor.robot_position')
    def update_odometry_position(self, robot, x, y, theta):
        # TODO: use detect_pal/detect_pmi?
        if not any(obj.name == robot for obj in self.robots):
            self.log('New robot', robot=robot)
            new_robot = Tracked(Point(x=x, y=y, theta=theta))
            self.robots.append(new_robot)


if __name__ == '__main__':
    tracking = Tracking()
    tracking.run()
