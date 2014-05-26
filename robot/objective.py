#!/usr/bin/env python3

from abc import ABCMeta, abstractmethod
from time import sleep

from math import pi, cos, sin

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
        robot.goto_xy_block(self.x + 130 * cos(self.direction), self.y +
                130 * sin(self.direction))
        cs.actuators.collector_open()
        sleep(.5)
        cs.actuators.collector_fireplace()
        robot.goto_xy_block(self.x + 50 * cos(self.direction), self.y +
                50 * sin(self.direction))
        cs.actuators.collector_close()
        sleep(1)
        robot.goto_xy_block(self.x + 130 * cos(self.direction), self.y +
                130 * sin(self.direction))
        robot.goto_xy_block(self.x, self.y)
        status.has_fire = False

class FirePlaceDropCenter(FirePlaceDrop):
    def execute(self, robot, cs, status):
        robot.goto_theta_block(self.direction)
        robot.goto_xy_block(self.x + 100 * cos(self.direction), self.y +
                100 * sin(self.direction))
        cs.actuators.collector_open()
        sleep(.5)
        cs.actuators.collector_fireplace()
        robot.goto_xy_block(self.x + 50 * cos(self.direction), self.y +
                50 * sin(self.direction))
        cs.actuators.collector_close()
        sleep(1)
        robot.goto_xy_block(self.x + 100 * cos(self.direction), self.y +
                100 * sin(self.direction))
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
        robot.goto_xy_block(self.x + 300 * cos(self.direction),
                            self.y + 300 * sin(self.direction))
        cs.actuators.collector_open()
        robot.goto_xy_block(self.x + 200 * cos(self.direction),
                            self.y + 200 * sin(self.direction))
        cs.actuators.collector_down()
        robot.goto_xy_block(self.x + 350 * cos(self.direction),
                            self.y + 350 * sin(self.direction))
        cs.actuators.collector_close()
        sleep(.5)
        cs.actuators.collector_hold()
        sleep(.5)
        cs.actuators.collector_up()
        sleep(1)
        if not cs.actuators.collector_has_fire():
            cs.actuators.collector_open()
            robot.goto_xy_block(self.x + 250 * cos(self.direction),
                                self.y + 250 * sin(self.direction))
            cs.actuators.collector_down()
            sleep(.5)
            robot.goto_xy_block(self.x + 450 * cos(self.direction),
                                self.y + 450 * sin(self.direction))
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
                str(self.x + 200 * cos(self.direction)) +\
                " " + str(self.y + 200 * sin(self.direction))

class WallFire(Objective):

    def execute(self, robot, cs, status):
        robot.goto_theta_block(self.direction)
        robot.goto_xy_block(self.x + 100 * cos(self.direction),
                            self.y + 100 * sin(self.direction))
        robot.goto_xy_block(self.x, self.y)
        robot.goto_theta_block(2 * pi - self.direction)

    def __str__(self):
        return "Wall fire " +\
                str( self.x + 100 * cos(self.direction)) +\
                " " + str(self.y + 100 * sin(self.direction))

class Torch(Objective):

    def execute(self, robot, cs, status):
        robot.goto_theta_block(0)
        robot.goto_theta_block(pi / 2)

    def __str__(self):
        return "Torche fire " +\
               str( self.x + 200 * cos(self.direction)) +\
                " " + str(self.y + 200 * sin(self.direction))

class DefaultObjectives():

    def color_pos(color, x, y, theta=0):
        dy = 1500 - y
        return (x, 1500 + color * dy, theta * -color)

    def generate_default_objectives(color):
        """ Objectives should be declared using position for the red player
        The color_pos function will convert the given position to the correct
        one depending on the robot's color"""

        defobj = ObjectiveList()

        # Objective needed to exit the startup zone
        defobj.append(FedexObjective(1, *DefaultObjectives.color_pos(color,
            437, 232, 0)))

        # Both corner fireplace
        positions = [
                [1650, 350, -pi / 4],
                [1650, 2650, pi / 4],
        ]
        for pos in positions:
            defobj.append(FirePlaceDrop(1, *DefaultObjectives.color_pos(color,
                pos[0], pos[1], pos[2])))

        # Standing fire. all 6 of them are declared because of the change
        # needed depending on which color you are
        positions = [
                [800, 400, 0],
                [1300, 2600, pi],
                [600, 700, pi / 2],
                [600, 1900, pi / 2],
                [1600, 1100, -pi / 2],
                [1600, 2300, -pi / 2],
        ]
        for pos in positions:
            defobj.append(StandingFire(1, *DefaultObjectives.color_pos(color,
                pos[0], pos[1], pos[2])))


        # Center fire. Is defined as multiple position to prevent stacking
        # fires
        for i in range(8):
            defobj.append(FirePlaceDropCenter(2, 1050 + cos(pi/4 * i) * 400, 1500 +
                sin(pi/4 * i) * 400, pi - pi/8*i))

        return defobj

        positions = [
                [800, 400, -pi / 2],
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





