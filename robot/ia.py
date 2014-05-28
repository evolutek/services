#!/usr/bin/env python3
from threading import Thread, Timer, Event
from time import sleep
import math

from cellaserv.service import Service, Variable, ConfigVariable
from cellaserv.proxy import CellaservProxy
from robot import Robot
from objective import *

import pathfinding
import robot_status


class ia(Service):

    match_start = Variable('start')
    color = ConfigVariable(section='match', option='color', coerc=lambda v:
            {'red': -1, 'yellow': 1}[v])

    def __init__(self):
        super().__init__()

        self.cs = CellaservProxy()

        self.match_stop_timer = Timer(85, self.match_stop)

        self.start_event = Event()
        self.pathfinding = pathfinding.Pathfinding(2000, 3000, 150)

        self.robot = Robot('pal')
        self.robot.setup()


    def setup(self):
        super().setup()

        # pathfinding.Init(200, 300, 15)
        self.cs('log.ia', msg="Setup done")

        self.robot.free()
        self.objectives =\
        DefaultObjectives.generate_default_objectives(self.color())
        self.status = robot_status.RobotStatus()
        self.pathfinding.AddObstacle(600, 900, 100)
        self.pathfinding.AddObstacle(600, 2100, 100)
        self.pathfinding.AddObstacle(1100, 400, 100)
        self.pathfinding.AddObstacle(1100, 2600, 100)
        self.pathfinding.AddObstacle(1600, 900, 100)
        self.pathfinding.AddObstacle(1600, 2100, 100)
        self.pathfinding.AddObstacle(1050, 1500, 150, "fireplacecenter")

        self.robot.unfree()

    @Service.action
    def status(self):
        return {'started': self.match_start.is_set()}


    #TODO: Check this function as a color wrapper
    def goto_xy_block(self, x, y):
        if self.color() == 1:
            self.robot.goto_xy_block(x, 3000 - y)
        else:
            self.robot.goto_xy_block(x, y)

    # Makes the robot go to a point avoiding obstacles.
    # We use aproximates coordinates for every point except for the last point
    # The first point is ignored since it's the robot's position
    def goto_with_pathfinding(self, x, y):
        pos = self.get_position()
        path = self.pathfinding.GetPath(pos['x'], pos['y'], x, y)
        for i in range(1, len(path) - 1):
            print("Waypoint : ", path[i].x, path[i].y)
            self.robot.goto_xy_block(path[i].x, path[i].y)
        print("Final waypoint : ", x, y)
        self.robot.goto_xy_block(x, y)

    def get_position(self):
        pos = None
        while not pos:
            try:
                pos = self.robot.get_position()
            except:
                pass
        return pos

    @Service.thread
    def start(self):
        print("Waiting...")
        self.log(msg='Waiting')
        self.match_start.wait()
        print("Start!")
        self.cs('log.ia', msg="Match started")


        # TODO: UNCOMMENT BEFORE GOING TO THE COUPE DE FRANCE
        #self.match_stop_timer.start()

        #self.robot.goto_xy_block(616, 1500 + self.color * (890))
        while len(self.objectives):
            pos = self.get_position()
            print(pos)
            obj = self.objectives.get_best(pos['x'], pos['y'], self.status)
            if obj.get_cost(pos['x'], pos['y'], self.status) > 10000:
                break
            obj.execute_requirements(self.robot, self.cs, self.status)
            print("going to obj " +  str(obj))
            print("At pos " +  str(obj.x) + " " + str(obj.y))
            self.goto_with_pathfinding(*(obj.get_position()))
            obj.execute(self.robot, self.cs, self.status)
            self.objectives.remove(obj)
            print("--------------------")
        self.robot.free()
        print("DONE")

        return



    # Called by a timer thread
    def match_stop(self):
        self.cs('log.ia', msg='Stopping robot')
        self.cs.trajman.free()
        self.cs.trajman.disable()

    @Service.event
    def robot_near(self):
        if self.match_start.is_set():
            self.cs('log.ia', msg='Detected robot near')
            self.match_stop()

def main():
    service = ia()
    service.run()

if __name__ == '__main__':
    main()
