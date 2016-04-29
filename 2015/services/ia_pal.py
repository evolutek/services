#!/usr/bin/env python3
from subprocess import call
from threading import Timer
import math

from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service, Event, ConfigVariable
from evolutek.lib.pathfinding import AvoidException
from evolutek.lib.robot import default_robot
import evolutek.lib.pathfinding as pathfinding

from .objective import DefaultObjectives, Balls, Fresque


class RobotStatus:

    def __init__(self):
        self.has_fire = False


@Service.require("trajman", "pal")
class IaPal(Service):

    match_start = Event('start')
    color = ConfigVariable(section='match', option='color',
                           coerc=lambda v: {'red': -1, 'yellow': 1}[v])

    def __init__(self):
        self.cs = CellaservProxy()

        self.match_stop_timer = Timer(85, self.match_stop)

        self.pathfinding = pathfinding.Pathfinding(2000, 3000, 200)

        self.robot = default_robot

        self.stopped = False

        super().__init__()

    @Service.action
    def status(self):
        return {'started': self.match_start.is_set()}

    def goto_xy_block(self, x, y):
        self.stopped = False
        self.robot.goto_xy_block(x=x, y=y)
        if self.stopped:
            print("Raising exception")
            raise AvoidException

    # Makes the robot go to a point avoiding obstacles.
    # We use aproximates coordinates for every point except for the last point
    # The first point is ignored since it's the robot's position
    def goto_with_pathfinding(self, x, y):
        pos = self.get_position()
        path = self.pathfinding.GetPath(pos['x'], pos['y'], x, y)
        for i in range(1, len(path) - 1):
            self.log(msg="Waypoint : " + str(path[i].x) + " " + str(path[i].y))
            self.goto_xy_block(path[i].x, path[i].y)
        self.log(msg="Final waypoint : " + str(x) + " " + str(y))
        self.goto_xy_block(x, y)

    def get_position(self):
        return self.robot.tm.get_position()

    @Service.thread
    def start(self):
        # pathfinding.Init(200, 300, 15)
        self.objectives = DefaultObjectives.generate_default_objectives(self.color(), self.pathfinding)

        self.status = RobotStatus()
        self.pathfinding.AddSquareObstacle(1050, 1500, 150, "fireplacecenter")
        self.pathfinding.AddRectangleObstacle(1200, 0, 1400, 100, "tree")
        self.pathfinding.AddRectangleObstacle(1200, 2900, 1400, 0, "tree")
        self.pathfinding.AddRectangleObstacle(1900, 600, 2000, 800, "tree")
        self.pathfinding.AddRectangleObstacle(1900, 2200, 2000, 2400, "tree")
        self.pathfinding.AddRectangleObstacle(0, 400, 300, 1100, "bacj")
        self.pathfinding.AddRectangleObstacle(0, 1900, 300, 2600, "bacr")

        self.robot.tm.unfree()

        print("Waiting...")
        self.log(msg='Waiting')
        self.match_start.wait()
        print("Start!")
        self.log(msg="Match started")

        fresque = Fresque(1000, 400, 1500, 0)
        balls = Balls(500, *DefaultObjectives.color_pos(self.color(), 600, 700))
        # TODO: UNCOMMENT BEFORE GOING TO THE COUPE DE FRANCE
        self.match_stop_timer.start()

        self.robot.goto_xy_block(600, 1500 + self.color() * (1500 - 400))
        self.robot.goto_xy_block(600, 1500)
        self.robot.goto_theta_block(0)
        try:
            self.log(msg="Going to " + str(fresque.get_position()) + " using pathfinding")
            self.goto_with_pathfinding(*(fresque.get_position()))
            self.log(msg="Executing the objective")
            fresque.execute(self.robot, self.cs, self.status, self)
        except:
            if not fresque.is_done():
                self.objectives.append(fresque)
        try:
            self.log(msg="Going to " + str(balls.get_position()) + " using pathfinding")
            self.goto_with_pathfinding(*(balls.get_position()))
            self.log(msg="Executing the objective")
            balls.execute()
        except:
            self.objectives.append(balls)
        tmpobj = None
        while self.objectives:
            pos = self.get_position()
            self.log(msg="Selecting objective to do")
            obj = self.objectives.get_best(pos['x'], pos['y'], self.status,
                    self.pathfinding, self)
            self.log(msg="Obj " + str(obj) + " selected while being at "+
                    str(pos))
            self('ia_new_target', pos=obj.get_position(), name=str(obj))
            self.pathfinding.RemoveObstacleByTag('opponent')
            if tmpobj:
                self.log(msg="Re-adding obj " + str(tmpobj))
                self.objectives.append(tmpobj)
                tmpobj = None
            if obj.get_cost(pos['x'], pos['y'], self.status, self.pathfinding) > 10000:
                self.log(msg="Remaining objectives are not possible, leaving.")
                break
            obj.execute_requirements(self.robot, self.cs, self.status)
            try:
                self.log(msg="Going to " + str(obj.get_position()) + " using pathfinding")
                self.goto_with_pathfinding(*(obj.get_position()))
                self.log(msg="Executing the objective")
                obj.execute(self.robot, self.cs, self.status, self)
            except AvoidException:
                self.log(msg="We avoided a collision")
                if not obj.is_done():
                    tmpobj = obj
                self.log(msg="Temporary removing obj " + str(obj) + " from the current objectives list")
                self.objectives.remove(obj)
                pos = self.get_position()
                self.log(msg="Avoiding manoeuver")
                self.robot.goto_theta_block(pos['theta'] + math.pi / 2)
                continue
            if obj.get_tag():
                self.pathfinding.RemoveObstacleByTag(obj.get_tag())
            current_list = "Current list of obstacles is : \n"

            self.log(msg=current_list, list=str(list(map(str, self.pathfinding.obstacles))))
            self.log(msg="Objective " + str(obj) + " is done, removing it")

            self.objectives.remove(obj)

        self.robot.tm.free()
        self.log(msg="Nothing more to do here")
        return

    # Called by a timer thread
    def match_stop(self):
        self.cs('log.ia', msg='Stopping robot')
        self.cs.trajman['pal'].free()
        self.cs.trajman['pal'].disable()
        self.cs.trajman['pmi'].free()
        self.cs.trajman['pmi'].disable()
        self.cs.actuators.collector_open()

    @Service.event
    def robot_near(self, x, y):
        print("Robot near, robot should be avoiding")
        if not self.stopped:
            print("Avoiding")
            self.robot.tm.stop_asap(trsldec=1500, rotdec=3.1)
            self.stopped = True
            call(['aplay', '/root/horn.wav'])
            self.pathfinding.AddSquareObstacle(x, y, 15, "opponent")
        #if self.match_start.is_set():
        #    self.cs('log.ia', msg='Detected robot near')
        #    self.match_stop()

def main():
    service = IaPal()
    service.run()

if __name__ == '__main__':
    main()
