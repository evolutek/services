#!/usr/bin/env python3
from threading import Thread, Timer, Event
from time import sleep
import math

from cellaserv.service import Service, Variable, ConfigVariable
from cellaserv.proxy import CellaservProxy
from robot import Robot
from objective import *
from subprocess import call

import pathfinding
import robot_status


class ia(Service):

    match_start = Variable('start')
    sharp_avoid = Variable('sharp_avoid')
    color = ConfigVariable(section='match', option='color', coerc=lambda v:
            {'red': -1, 'yellow': 1}[v])

    def __init__(self):
        super().__init__()

        self.cs = CellaservProxy()

        self.match_stop_timer = Timer(85, self.match_stop)

        self.start_event = Event()
        self.pathfinding = pathfinding.Pathfinding(2000, 3000, 200)

        self.robot = Robot('pal')
        self.robot.setup()
        self.stopped = False


    def setup(self):
        super().setup()

        # pathfinding.Init(200, 300, 15)
        self.cs('log.ia', msg="Setup done")

        self.robot.free()
        self.objectives =\
        DefaultObjectives.generate_default_objectives(self.color(),
                self.pathfinding)
        self.status = robot_status.RobotStatus()
        self.pathfinding.AddSquareObstacle(1050, 1500, 150, "fireplacecenter")
        self.pathfinding.AddRectangleObstacle(0, 400, 300, 1100, "bacj")
        self.pathfinding.AddRectangleObstacle(0, 1900, 300, 2600, "bacr")

        self.robot.unfree()

    @Service.action
    def status(self):
        return {'started': self.match_start.is_set()}


    #TODO: Check this function as a color wrapper
    def goto_xy_block(self, x, y):
        self.stopped = False
        self.robot.goto_xy_block(x, y)
        if self.stopped:
            raise AvoidException

    # Makes the robot go to a point avoiding obstacles.
    # We use aproximates coordinates for every point except for the last point
    # The first point is ignored since it's the robot's position
    def goto_with_pathfinding(self, x, y):
        pos = self.get_position()
        path = self.pathfinding.GetPath(pos['x'], pos['y'], x, y)
        for i in range(1, len(path) - 1):
            print("Waypoint : ", path[i].x, path[i].y)
            self.goto_xy_block(path[i].x, path[i].y)
        print("Final waypoint : ", x, y)
        self.goto_xy_block(x, y)

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
        avoid = Thread(target=self.avoid_opponent)
        avoid.start()
        print("Waiting...")
        self.log(msg='Waiting')
        self.match_start.wait()
        print("Start!")
        self.cs('log.ia', msg="Match started")


        # TODO: UNCOMMENT BEFORE GOING TO THE COUPE DE FRANCE
        #self.match_stop_timer.start()

        self.robot.goto_xy_block(437, 1500 + self.color() * (1500 - 232))
        tmpobj = None
        while len(self.objectives):
            pos = self.get_position()
            print(pos)
            obj = self.objectives.get_best(pos['x'], pos['y'], self.status)
            if tmpobj:
                self.objectives.append(tmpobj)
            if obj.get_cost(pos['x'], pos['y'], self.status) > 10000:
                break
            obj.execute_requirements(self.robot, self.cs, self.status)
            print("going to obj " +  str(obj))
            print("At pos " +  str(obj.x) + " " + str(obj.y))
            try:
                self.goto_with_pathfinding(*(obj.get_position()))
                obj.execute(self.robot, self.cs, self.status)
            except:
                tmpobj = obj
                self.objectives.remove(obj)
                pos = self.get_position()
                self.robot.goto_theta_block(pos[2] + math.pi / 2)
                continue
            if obj.get_tag():
                self.pathfinding.RemoveObstacleByTag(obj.get_tag())
            for obs in self.pathfinding.obstacles:
                print(str(obs))
            self.objectives.remove(obj)
            print("--------------------")
        self.robot.free()
        print("DONE")

        return


    def avoid_opponent(self):
        while True:
            sharp = self.sharp_avoid.wait()
            print(sharp)
            if not self.stopped:
                v = self.robot.get_vector_trsl()
                if ((v['trsl_vector'] > 0 and sharp['n'] in [0, 1])
                        or v['trsl_vector'] < 0 and sharp['n'] in [2, 3]):
                    self.robot.stop_asap(trsldec=1500, rotdec=3.1)
                    self.stopped = True
                    call(['aplay', '/root/horn.wav'])
            self.sharp_avoid.clear()

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
