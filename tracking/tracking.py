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

class Obstacle:

    def __init__(self, x, y, width, height):
        self.x = x;
        self.y = y;
        self.width = width
        self.height = height

    def intersect(self, x, y):
        return (x >= self.x) and (x <= self.x + self.width) and (y >= self.y) and (y <= self.y + self.height)

class Tracked:

    internal_id = 0

    def __init__(self, location):
        self.location = location

        self._name = "PLIPPE {}".format(Tracked.internal_id)
        Tracked.internal_id += 1

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
    sharp_map_margin = ConfigVariable(section='tracking',
            option='sharp_map_margin',
            coerc=int)

    sharp_threshold = ConfigVariable(section='sharp', option='threshold',
            coerc=float)

    def __init__(self):
        super().__init__()
        self.cs = CellaservProxy()

        self.robots_lock = threading.Lock()

        # Default robots
        self.pal = Tracked(Point(0, 0))
        self.pal.theta = 0
        self.pal.name = 'pal'
        self.pal.is_evolutek = True
        self.pmi = Tracked (Point(0, 0))
        self.pmi.theta = 0
        self.pmi.name = 'pmi'
        self.pmi.is_evolutek = True
        self.robots = [self.pal, self.pmi]

        # Enable dynamic updates
        self.hokuyo_scan_pal.add_update_cb(self.pal.is_scanned_set)
        self.hokuyo_scan_pmi.add_update_cb(self.pmi.is_scanned_set)

    def setup(self):
        super().setup()
        
        # Define safe zones
        self.sharp_safe_zone = [Obstacle(0,0,2000,self.sharp_map_margin()), 
                Obstacle(0,0,self.sharp_map_margin(), 3000),
                Obstacle(0,3000-self.sharp_map_margin(),2000,self.sharp_map_margin()),
                Obstacle(2000-self.sharp_map_margin(),0,self.sharp_map_margin(),3000)]


    # Actions
    @Service.action
    def get_robots(self):
        ret = []
        for r in self.robots:
            robot = {'name': r.name,
                     'x': r.location.x,
                     'y': r.location.y}
            ret.append(robot)
        return ret


    # Utility functions

    def is_alive(self, obj):
        """Return True if the object may still be alive."""
        return (time.time() - obj.last_seen) < self.half_life()

    # Events listened, updates internal representation of the robots

    @Service.event('log.monitor.robot_position')
    def update_odometry_position(self, robot, x, y, theta):
        location = Point(x=x, y=y)

        for obj in self.robots:
            if obj.name == robot:
                obj.location = location
                obj.theta = theta
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
            # XXX: 'g' unused
            scans = [Point(r['x'], r['y']) for r in robots]
            robots = [r for r in self.robots if r.is_scanned]

            # First, try to lock down on our robots in order to avoid false
            # positives with ourselves
            self.match_scans_to_robots(
                min_dist=200,
                robots=robots,
                robots_filter=lambda r: r.is_evolutek,
                scans=scans)

            # Try to match alive robots
            self.match_scans_to_robots(
                min_dist=1000,
                robots=robots,
                robots_filter=lambda r: self.is_alive(r),
                scans=scans)

            # Then try to revive dead robots
            self.match_scans_to_robots(
                min_dist=1000,
                robots=robots,
                robots_filter=lambda r: True,  # Do not filter
                scans=scans)

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
        robot_moving_side = self.cs.trajman['pal'].get_vector_trsl()

        # trajman dead ....
        if robot_moving_side['trsl_vector'] == None: 
            return

        print(robot_moving_side['trsl_vector'])
        # For now only pal has sharps
        pal_front_sharps = [0, 1]
        pal_back_sharps = [2, 3]

        sharp_robot_x = (-150 if n in pal_back_sharps else 150)
        sharp_robot_y = (-140 if n in [2, 0] else 140)

        obj_x = sharp_robot_x + (self.sharp_threshold()*10,
                -self.sharp_threshold()*10)[n in 
                pal_back_sharps]

        obj_y = sharp_robot_y

        # apply rotation to object's position
        theta = self.pal.theta
        real_obj_x = obj_x*math.cos(theta) - obj_y*math.sin(theta)
        real_obj_y = obj_x*math.sin(theta) + obj_y*math.cos(theta)

        # Add robots's position to get absolute coord
        real_obj_x += self.pal.location.x
        real_obj_y += self.pal.location.y

        self.log(msg="[PAL|DETECTED] X="+str(real_obj_x)+";Y="+str(real_obj_y))
        
        if(real_obj_x < 0 or real_obj_x > 2000 or real_obj_y < 0 or real_obj_y >
                3000):
            return

        # Ignore if it's on the opposite side of its movement
        if ((n in pal_front_sharps) and (robot_moving_side['trsl_vector'] < 0)) or ((n in
            pal_back_sharps) and (robot_moving_side['trsl_vector'] > 0)):
            return

        # Check if inside any of safe zones
        if(any([x.intersect(real_obj_x, real_obj_y) for x in 
            self.sharp_safe_zone])):
            return

        # Check if it's the PMI
        if(Obstacle(self.pmi.location.x-75,
            self.pmi.location.y-100,150,200)
            .intersect(real_obj_x, real_obj_y)):
            return

        self.log(msg="[PAL|CONFIRMED] X="+str(real_obj_x)+";Y="+str(real_obj_y))

        self('robot_near', x=real_obj_x, y=real_obj_y)

    @Service.event
    def sharp_pmi_avoid(self, n):
        robot_moving_side = self.cs.trajman['pmi'].get_vector_trsl()
            
        # trajman dead ....
        if robot_moving_side['trsl_vector'] == None: 
            return

        front_sharp = [1]  # 80cm
        back_sharp = [0]  # 30cm

        sharp_robot_x = (-75 if n in back_sharp else 75)
        sharp_robot_y = 0
        
        obj_x = sharp_robot_x + (self.sharp_threshold()*10,
                -self.sharp_threshold()*10)[n in 
                back_sharp]

        obj_y = sharp_robot_y
        
        # apply rotation to object's position
        theta = self.pmi.theta
        real_obj_x = obj_x*math.cos(theta) - obj_y*math.sin(theta)
        real_obj_y = obj_x*math.sin(theta) + obj_y*math.cos(theta)

        # Add robots's position to get absolute coord
        real_obj_x += self.pmi.location.x
        real_obj_y += self.pmi.location.y

        self.log(msg="[PMI|DETECTED] X="+str(real_obj_x)+";Y="+str(real_obj_y))
       
        # Ignore if outside of the map
        if(real_obj_x < 0 or real_obj_x > 2000 or real_obj_y < 0 or real_obj_y >
                3000):
            return

        # Ignore if it's on the opposite side of its movement
        if ((n in front_sharp) and (robot_moving_side['trsl_vector'] < 0)) or ((n in
            back_sharp) and (robot_moving_side['trsl_vector'] > 0)):
            return

        # Check if inside any of safe zones
        if(any([x.intersect(real_obj_x, real_obj_y) for x in 
            self.sharp_safe_zone])):
            return

        # Check if it's the PAL
        if(Obstacle(self.pal.location.x-150,
            self.pal.location.y-150,300,300)
            .intersect(real_obj_x, real_obj_y)):
            return

        self.log(msg="[PMI|CONFIRMED] X="+str(real_obj_x)+";Y="+str(real_obj_y))
        
        self('beep_ko')
        self('robot_near_pmi', x=real_obj_x, y=real_obj_y)


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
                    self.robots.remove(obj)

    @Service.thread
    def backgroup_loop(self):
        while not time.sleep(.01):
            self.prune_dead_robots()


if __name__ == '__main__':
    tracking = Tracking()
    tracking.run()
