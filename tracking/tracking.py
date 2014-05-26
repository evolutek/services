#!/usr/bin/env python3

from collections import namedtuple
import math
import random
import threading
import time

from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service, ConfigVariable

Point = namedtuple('Point', ['x', 'y'])

def distance(point_a, point_b):
    return math.sqrt((point_b.x - point_a.x) ** 2 + (point_b.y - point_a.y) ** 2)


class Tracked:

    internal_id = 0

    def __init__(self, location):
        self.location = location

        self._name = "PLIPPE {}".format(self.internal_id)
        self.internal_id += 1

        self.last_seen = time.time()
        self.is_evolutek = False
        self.is_scanned = True
        self.alive = True

    def __str__(self):
        return '<{} at {}>'.format(self.name, self.location)

    def __repr__(self):
        return '<{} at {}>'.format(self.name, self.location)

    def seen(self):
        """Update when the robot was last seen."""
        self.last_seen = time.time()

    def is_scanned_set(self, is_scanned):
        self.is_scanned = is_scanned

    def name_get(self):
        """Get the name of the robot."""
        return self._name

    def name_set(self, name):
        """Change the name of the robot."""
        self._name = name

    name = property(name_get, name_set)

    def update_location(self, location):
        # TODO: compute speed, acceleration, etc.
        self.location = location


class Tracking(Service):

    color = ConfigVariable(section='match', option='color')
    half_life = ConfigVariable(section='tracking', option='half_life',
            coerc=float)
    hokuyo_scan_pal = ConfigVariable(section='tracking',
            option='hokuyo_scan_pal', coerc=eval)
    hokuyo_scan_pmi = ConfigVariable(section='tracking',
            option='hokuyo_scan_pmi', coerc=eval)

    def __init__(self):
        super().__init__()
        self.cs = CellaservProxy()

        self.robots_lock = threading.Lock()

        # Default robots
        pal = Tracked(Point(0, 0))
        pal.name = 'pal'
        pal.is_evolutek = True
        pmi = Tracked(Point(0, 0))
        pmi.name = 'pmi'
        pmi.is_evolutek = True
        self.robots = [pal, pmi]

        # Enable dynamic updates
        self.hokuyo_scan_pal.add_update_cb(pal.is_scanned_set)
        self.hokuyo_scan_pmi.add_update_cb(pmi.is_scanned_set)

    # Utility functions

    def is_alive(self, obj):
        """Return True if the object may still be alive."""
        return (time.time() - obj.last_seen) < self.half_life()

    # Events listened, updates internal representation of the robots

    @Service.event('log.monitor.robot_position')
    def update_odometry_position(self, robot, x, y, theta):
        point = Point(x=x, y=y, theta=theta)

        for obj in self.robots:
            if obj.name == robot:
                obj.point = point
                obj.seen()
                return

    def match_scans_to_robots(self, min_dist, robots, robots_filter, scans):
        """Will update robots to remove scanned robots"""
        while robots and scans:
            best_match = {}

            for r in filter(robots_filter, robots):
                for scan in scans:
                    dist = distance(scan, r.location)
                    if dist <= min_dist:
                        min_dist = dist
                        best_match['robot'] = r
                        best_match['scan'] = scan

            if best_match:
                best_match['robot'].update_location(best_match['scan'])
                best_match['robot'].seen()
                # remove matched scan from list of scans
                scans.remove(best_match['scan'])
                robots.remove(best_match['robot'])
            else:
                break  # could not lock on robots

    @Service.event('hokuyo.robots')
    def hokuyo(self, robots):
        with self.robots_lock:
            scans = [Point(r['x'], r['y']) for r in robots]  # XXX: dropping 'g'
            robots = [r for r in self.robots if r.is_scanned]

            # First, try to lock down on our robots in order to avoid false
            # positives with ourselves
            self.match_scans_to_robots(min_dist=200,
                    robots=robots,
                    robots_filter=lambda r: r.is_evolutek,
                    scans=scans)

            # Try to match alive robots
            self.match_scans_to_robots(min_dist=1000,
                    robots=robots,
                    robots_filter=lambda r: self.is_alive(r),
                    scans=scans)

            # Then try to revive dead robots
            self.match_scans_to_robots(min_dist=1000,
                    robots=robots,
                    robots_filter=lambda r: True,  # Do not filter
                    scans=scans)

            self.log(msg='Robots not matched to a scan',
                    robots=str(robots))

            # Pour toutes les mesures qui n'ont pas de robot
            for scan in scans:
                min_dist = 100
                for r in self.robots:
                    dist = distance(scan, r.location)
                    if dist < min_dist:
                        min_dist = dist
                # on cree donc un nouveau robot si la distance minimale a tous
                # les robots est superieur a XXcm
                if min_dist >= 100:
                    self.robots.append(Tracked(scan))

    @Service.event
    def sharp_avoid(self, n):
        robot_moving_side = self.get_robot_moving_side()
        # For now only pal has sharps
        front_sharps = [0, 1]
        back_sharps = [2, 3]
        if n in front_sharps:
            pass
        elif n in back_sharps:
            pass
        else:
            self.log('Unknown sharp: %s'.format(n))
            return

    # Threads

    def prune_dead_robots(self):
        """
        prune_dead_robots() remove robots that are too old.

        We use a lock because we are modifiying the list of robots.
        """

        with self.robots_lock:
            robots_alive = []
            for obj in self.robots:
                if self.is_alive(obj) or obj.is_evolutek:
                    robots_alive.append(obj)
                else:
                    self.log(msg='Dropping dead robot', robot=str(obj))


    @Service.thread
    def backgroup_loop(self):
        while not time.sleep(.1):
            self.prune_dead_robots()


if __name__ == '__main__':
    tracking = Tracking()
    tracking.run()
