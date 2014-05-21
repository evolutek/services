#!/usr/bin/env python3

from abc import ABCMeta, abstractmethod
import time

import math

class Objective(metaclass=ABCMeta):

    def __init__(self, points, x, y, direction=0):
        self.x = x
        self.y = y
        self.direction = direction
        self.points = points

    def get_cost(self, x, y):
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

    def get_position(self):
        return (self.x, self.y)

    @abstractmethod
    def execute(self, robot, cs):
        pass

class ObjectiveList(list):

    def get_best(self, x, y):
        self.sort(key=lambda k: k.get_cost(x, y))
        return self[0]

class FedexObjective(Objective):

    def execute(self, robot, cs):
        robot.goto_theta_block(1.6)
        time.sleep(1)
        robot.goto_theta_block(0)
        time.sleep(1)

class StandingFire(Objective):

    def execute(self, robot, cs):
        robot.goto_theta_block(self.direction)
        robot.goto_xy_block(self.x + 200 * math.cos(self.direction),
                            self.y + 200 * math.sin(self.direction))
        robot.goto_xy_block(self.x, self.y)

    def __str__(self):
        return "Standing fire " +\
                str(self.x + 200 * math.cos(self.direction)) +\
                " " + str(self.y + 200 * math.sin(self.direction))

class WallFire(Objective):

    def execute(self, robot, cs):
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

    def execute(self, robot, cs):
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
        defobj = ObjectiveList()
        positions = [
                [800, 400, 0],
                [1400, 2600, math.pi],
                [600, 600, math.pi / 2],
                [600, 1900, math.pi / 2],
                [1600, 1200, -math.pi / 2],
                [1600, 2400, -math.pi / 2],
        ]
        for pos in positions:
            defobj.append(
                StandingFire(
                    1,
                    *DefaultObjectives.color_pos(color, pos[0], pos[1], pos[2])
                )
            )
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





