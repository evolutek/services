#!/usr/bin/env python3

from abc import ABCMeta, abstractmethod
from time import sleep

from math import pi, cos, sin, sqrt

DST_STDFR = 300

class Objective(metaclass=ABCMeta):

    def __init__(self, points, x, y, direction=0, tag=None):
        self.x = x
        self.y = y
        self.direction = direction
        self.points = points
        self.tag = tag
        self.done = False

    def get_cost(self, x, y, status, pathfinding):
        #return (pathfinding.PathLen(pathfinding.GetPath(x, y, self.x, self.y))
        #        / self.points)
        return sqrt((x - self.x) ** 2 + (y - self.y) ** 2) / self.points

    def get_position(self):
        return (self.x, self.y)

    @abstractmethod
    def execute(self, robot, cs, status, ia):
        pass

    def get_tag(self):
        return self.tag

    def execute_requirements(self, robot, cs, status):
        """ Function supposed to be called while going to the place of the
        current objective. Do *NOT* make blocking calls in this method"""
        pass

    def is_done(self):
        return self.done

    def __str__(self):
        return str(self.x) + " " + str(self.y) + " " + str(self.direction)

class ObjectiveList(list):

    def get_best(self, x, y, status, pathfinding, ia):
        self.sort(key=lambda k: k.get_cost(x, y, status, pathfinding))
        return self[0]

class FedexObjective(Objective):

    def execute(self, robot, cs, status, ia):
        pass

class FirePlaceDrop(Objective):

    def get_cost(self, x, y, status, pathfinding):
        if not status.has_fire:
            return 10**9
        return super().get_cost(x, y, status, pathfinding)

    def execute_requirements(self, robot, cs, status):
        cs.actuators.collector_up()

    def execute(self, robot, cs, status, ia):
        robot.goto_theta_block(theta=self.direction)
        ia.goto_xy_block(self.x + 130 * cos(self.direction), self.y +
                130 * sin(self.direction))
        cs.actuators.collector_open()
        sleep(.5)
        cs.actuators.collector_fireplace()
        ia.goto_xy_block(self.x + 50 * cos(self.direction), self.y +
                50 * sin(self.direction))
        cs.actuators.collector_close()
        sleep(1)
        ia.goto_xy_block(self.x + 130 * cos(self.direction), self.y +
                130 * sin(self.direction))
        ia.goto_xy_block(self.x, self.y)
        status.has_fire = False

    def __str__(self):
        return "FirePlaceDrop " + super().__str__()

class FirePlaceDropCenter(FirePlaceDrop):
    def execute(self, robot, cs, status, ia):
        robot.goto_theta_block(theta=self.direction)
        ia.goto_xy_block(self.x + 130 * cos(self.direction), self.y +
                130 * sin(self.direction))
        cs.actuators.collector_open()
        sleep(.5)
        cs.actuators.collector_fireplace()
        ia.goto_xy_block(self.x + 20 * cos(self.direction), self.y +
                20 * sin(self.direction))
        cs.actuators.collector_close()
        sleep(1)
        ia.goto_xy_block(self.x + 150 * cos(self.direction), self.y +
                150 * sin(self.direction))
        ia.goto_xy_block(self.x, self.y)
        status.has_fire = False

    def __str__(self):
        return "FirePlaceDropCenter " + super().__str__()

class StandingFire(Objective):

    def get_cost(self, x, y, status, pathfinding):
        if status.has_fire:
            return 10**9
        return super().get_cost(x, y, status, pathfinding)

    def execute_requirements(self, robot, cs, status):
        cs.actuators.collector_push_fire()

    def execute(self, robot, cs, status, ia):
        robot.goto_theta_block(theta=self.direction)
        ia.goto_xy_block(self.x + (DST_STDFR + 100) * cos(self.direction),
                            self.y + (DST_STDFR + 100) * sin(self.direction))
        cs.actuators.collector_open()
        ia.goto_xy_block(self.x + DST_STDFR * cos(self.direction),
                            self.y + DST_STDFR * sin(self.direction))
        cs.actuators.collector_down()
        sleep(1)
        ia.goto_xy_block(self.x + (DST_STDFR + 150) * cos(self.direction),
                            self.y + (DST_STDFR + 150) * sin(self.direction))
        cs.actuators.collector_close()
        sleep(.5)
        cs.actuators.collector_hold()
        sleep(.5)
        cs.actuators.collector_up()
        sleep(1)
        if not cs.actuators.collector_has_fire():
            cs.actuators.collector_open()
            ia.goto_xy_block(self.x + (DST_STDFR + 50) * cos(self.direction),
                                self.y + (DST_STDFR + 50) * sin(self.direction))
            cs.actuators.collector_down()
            sleep(1)
            ia.goto_xy_block(self.x + (DST_STDFR + 250) * cos(self.direction),
                                self.y + (DST_STDFR + 250) * sin(self.direction))
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
        return "StandingFire " + super().__str__()

class OponnentStandingFire(Objective):

    def execute(self, robot, cs, status, ia):
        super().execute(robot, cs, status, ia)
        sleep(1)
        cs.actuators.collector_rotate()

class WallFire(Objective):

    def execute(self, robot, cs, status, ia):
        robot.goto_theta_block(theta=self.direction)
        ia.goto_xy_block(self.x + 100 * cos(self.direction),
                            self.y + 100 * sin(self.direction))
        ia.goto_xy_block(self.x, self.y)
        robot.goto_theta_block(theta=2 * pi - self.direction)

    def __str__(self):
        return "Wall fire " + super().__str__()

class Fresque(Objective):

    def execute(self, robot, cs, status, ia):
        robot.goto_theta_block(theta=self.direction)
        pos = robot.tm.get_position()
        speeds = robot.tm.get_speeds()
        robot.tm.set_trsl_max_speed(maxspeed=100)
        ia.goto_xy_block(200, pos['y'])
        ia.goto_xy_block(141, pos['y'])
        ia.goto_xy_block(300, pos['y'])
        ia.goto_xy_block(141, pos['y'])
        self.is_done = True
        robot.tm.set_trsl_max_speed(maxspeed=(speeds['trmax']))
        ia.goto_xy_block(500, pos['y'])

class Balls(Objective):
    """ We have balls. """

    def execute(self, robot, cs, status, ia):
        robot.goto_theta_block(theta=0)
        cs.actuators.launcher_fire()

class Torch(Objective):

    def execute(self, robot, cs, status, ia):
        robot.goto_theta_block(theta=0)
        robot.goto_theta_block(theta=pi / 2)

    def __str__(self):
        return "Torche fire " + super().__str__()

class DefaultObjectives():

    def color_pos(color, x, y, theta=0):
        dy = 1500 - y
        return (x, 1500 + color * dy, theta * -color)

    def generate_default_objectives(color, pathfinding):
        """ Objectives should be declared using position for the red player
        The color_pos function will convert the given position to the correct
        one depending on the robot's color"""

        defobj = ObjectiveList()

        # Objective needed to exit the startup zone
        #defobj.append(FedexObjective(1, *DefaultObjectives.color_pos(color,
        #    437, 232, 0)))

        # Both corner fireplace
        positions = [
                [1650, 350, -pi / 4],
                [1650, 2650, pi / 4],
        ]
        for pos in positions:
            defobj.append(FirePlaceDrop(2, *DefaultObjectives.color_pos(color,
                pos[0], pos[1], pos[2])))

        # Standing fire. all 6 of them are declared because of the change
        # needed depending on which color you are
        positions = [
                [1100, 400, 0],
                [1100, 2600, pi],
                #[600, 900, pi / 2],
                [600, 2100, pi / 2],
                [1600, 900, -pi / 2],
                [1600, 2100, -pi / 2],
        ]
        i = 0
        for pos in positions:
            tag = "fire" + str(i)
            i += 1
            if pathfinding != None:
                # Adding the correspongind obstacle
                pathfinding.AddSquareObstacle(
                        pos[0],
                        pos[1],
                        50,
                        tag)
            defobj.append(StandingFire(1,
                *DefaultObjectives.color_pos(color,
                pos[0] - cos(pos[2]) * DST_STDFR,
                pos[1] - sin(pos[2]) * DST_STDFR,
                pos[2]),
                tag=tag))

        # Center fire. Is defined as multiple position to prevent stacking
        # fires
        for i in range(8):
            defobj.append(FirePlaceDropCenter(1, 1050 + cos(pi/4 * i) * 400, 1500 +
                sin(pi/4 * i) * 400, pi/4*i - pi))

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




if __name__ == "__main__":
    objs = DefaultObjectives.generate_default_objectives(1, None)
    print("Yellow objectives :")
    for obj in objs:
        print(str(obj))
    objs = DefaultObjectives.generate_default_objectives(-1, None)
    print()
    print()
    print()
    print("Red objectives :")
    for obj in objs:
        print(str(obj))


