#!/usr/bin/env python3

from abc import ABCMeta, abstractmethod
import time

import math

class Objective(metaclass=ABCMeta):

    def __init__(self, x, y, points):
        self.x = x
        self.y = y
        self.points = points

    def get_cost(self, x, y):
        print(x, self.x, y, self.y)
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

    def __init__(self, x, y, points, direction):
        super.__init__(x, y, points)
        self.direction = direction

    def execute(self, robot, cs):
        robot.goto_theta_block(direction)
        robot.goto_xy_block(self.x + 200 * math.sin(self.direction),
                            self.y + 200 * math.cos(self.direction))
        robot.goto_xy_block(self.x, self.y)


class DefaultObjectives():

    def color_pos(self, x, y, color):
        dy = 1500 - y
        return (x, 1500 + color * dy)

    def generate_default_objectives(self, color):
        defobj = ObjectiveList()
        positions = [
                [800, 400, 0],
                [600, 600, math.pi / 2],
                [1600, 1200, -math.pi / 2],]


