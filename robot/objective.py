#!/usr/bin/env python3

from abc import ABCMeta, abstractmethod
from time import sleep

import math

class Objective(metaclass=ABCMeta):

    def __init__(self, points, x, y, direction=0):
        self.x = x
        self.y = y
        self.direction = direction
        self.points = points

    def get_cost(self, x, y, status):
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2) / self.points

    def get_position(self):
        return (self.x, self.y)

    @abstractmethod
    def execute(self, robot, cs, status):
        pass

    @abstractmethod
    def execute_requirements(self, robot, cs, status):
        """ Function supposed to be called while going to the place of the
        current objective. Do *NOT* make blocking calls in this method"""
        pass

class ObjectiveList(list):

    def get_best(self, x, y, status):
        self.sort(key=lambda k: k.get_cost(x, y, status))
        return self[0]

class FedexObjective(Objective):

    def execute(self, robot, cs, status):
        pass

class FirePlaceDrop(Objective):

    def get_cost(self, x, y, status):
        if not status.has_fire:
            return 10**9
        return super.get_cost(x, y, status)

    def execute_requirements(self, robot, cs, status):
        cs.actuators.collector_up()

    def execute(self, robot, cs, status):
        robot.goto_theta_block(self.direction)
        sleep(.5)
        robot.goto_xy_block(self.x + 130 * math.cos(self.direction), self.y +
                130 * math.sin(self.direction))
        cs.actuators.collector_open()
        sleep(.5)
        cs.actuators.collector_fireplace()
        robot.goto_xy_block(self.x + 50 * math.cos(self.direction), self.y +
                50 * math.sin(self.direction))
        cs.actuators.collector_close()
        sleep(1)
        robot.goto_xy_block(self.x + 130 * math.cos(self.direction), self.y +
                130 * math.sin(self.direction))
        robot.goto_xy_block(self.x, self.y)
        status.has_fire = False


class StandingFire(Objective):

    def get_cost(self, x, y, status):
        if status.has_fire:
            return 10**9
        return super.get_cost(x, y, status)

    def execute_requirements(self, robot, cs, status):
        cs.actuators.collector_push_fire()

    def execute(self, robot, cs, status):
        robot.goto_theta_block(self.direction)
        robot.goto_xy_block(self.x + 300 * math.cos(self.direction),
                            self.y + 300 * math.sin(self.direction))
        cs.actuators.collector_open()
        robot.goto_xy_block(self.x + 200 * math.cos(self.direction),
                            self.y + 200 * math.sin(self.direction))
        cs.actuators.collector_down()
        robot.goto_xy_block(self.x + 350 * math.cos(self.direction),
                            self.y + 350 * math.sin(self.direction))
        cs.actuators.collector_close()
        sleep(.5)
        cs.actuators.collector_hold()
        sleep(.5)
        cs.actuators.collector_up()
        sleep(1)
        if not cs.actuators.collector_has_fire():
            cs.actuators.collector_open()
            robot.goto_xy_block(self.x + 250 * math.cos(self.direction),
                                self.y + 250 * math.sin(self.direction))
            cs.actuators.collector_down()
            sleep(.5)
            robot.goto_xy_block(self.x + 450 * math.cos(self.direction),
                                self.y + 450 * math.sin(self.direction))
            cs.actuators.collector_close()
            sleep(.5)
            cs.actuators.collector_hold()
            sleep(.5)
            cs.actuators.collector_up()
            if cs.actuators.collector_has_fire():
                status.has_fire = True
        else:
            status.has_fire = True


    def __str__(self):
        return "Standing fire " +\
                str(self.x + 200 * math.cos(self.direction)) +\
                " " + str(self.y + 200 * math.sin(self.direction))

class WallFire(Objective):

    def execute(self, robot, cs, status):
        robot.goto_theta_block(self.direction)
        robot.goto_xy_block(self.x + 100 * math.cos(self.direction),
                            self.y + 100 * math.sin(self.direction))
        robot.goto_xy_block(self.x, self.y)
        robot.goto_theta_block(2 * math.pi - self.direction)

    def __str__(self):
        return "Wall fire " +\
                str( self.x + 100 * math.cos(self.direction)) +\
                " " + str(self.y + 100 * math.sin(self.direction))

class Torch(Objective):

    def execute(self, robot, cs, status):
        robot.goto_theta_block(0)
        robot.goto_theta_block(math.pi / 2)

    def __str__(self):
        return "Torche fire " +\
               str( self.x + 200 * math.cos(self.direction)) +\
                " " + str(self.y + 200 * math.sin(self.direction))

class DefaultObjectives():

    def color_pos(color, x, y, theta=0):
        dy = 1500 - y
        return (x, 1500 + color * dy, theta * -color)

    def generate_default_objectives(color):
        """ Objectives should be declared using position for the red player
        The color_pos function will convert the given position to the correct
        one depending on the robot's color"""

        defobj = ObjectiveList()
        positions = [[1650, 350, -math.pi / 4]]
        for pos in positions:
            defobj.append(FirePlaceDrop(1, *DefaultObjectives.color_pos(color,
                pos[0], pos[1], pos[2])))

        defobj.append(FedexObjective(1, *DefaultObjectives.color_pos(color,
            437, 232, 0)))
        positions = [
                [800, 400, 0],
        #        [1400, 2600, math.pi],
        #        [600, 600, math.pi / 2],
        #        [600, 1900, math.pi / 2],
        #        [1600, 1200, -math.pi / 2],
        #        [1600, 2400, -math.pi / 2],
        ]
        for pos in positions:
            defobj.append(StandingFire(1, *DefaultObjectives.color_pos(color,
                pos[0], pos[1], pos[2])))
        return defobj
        positions = [
                [800, 400, -math.pi / 2],
                [1600, 1300, 0],
                ]
        for pos in positions:
            defobj.append(
                    WallFire(
                        1, *DefaultObjectives.color_pos(color, pos[0], pos[1],
                            pos[2])
                    )
                )
            defobj.append(
                    WallFire(
                        1, *DefaultObjectives.color_pos(-color, pos[0], pos[1],
                            pos[2])
                    )
                )
        positions = [
                [1100, 900],
                ]
        for pos in positions:
            defobj.append(
                    Torch(1, *DefaultObjectives.color_pos(color, pos[0], pos[1])
                    )
            )
            defobj.append(
                    Torch(1, *DefaultObjectives.color_pos(-color, pos[0], pos[1])
            )
        )
        return defobj





