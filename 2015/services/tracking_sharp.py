#!/usr/bin/env python3

from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service, ConfigVariable

from evolutek.lib.map import Vector2, Vector3, Map, Circle


@Service.require('trajman', 'pal')
@Service.require('trajman', 'pmi')
class SharpAvoid(Service):

    sharp_map_margin = ConfigVariable(
        section='tracking', option='sharp_map_margin', coerc=int)
    sharp_threshold = ConfigVariable(
        section='sharp', option='threshold',
        # Convert cm to mm
        coerc=lambda i: float(i) * 10)

    def __init__(self):
        super().__init__()

        self.cs = CellaservProxy()

        # Match a sharp ID to a robot
        self.sharps_robots = {
            0: 'pal',
            1: 'pal',
            2: 'pal',
            3: 'pal',
            4: 'pmi',
            5: 'pmi',
            6: 'pmi',
            7: 'pmi',
        }

        """
        Robot's sharps positions:

            0     Rear      1
            +---------------+
            |               |
            |               |
            |theta = 0 (ccw)|
            |       ·-->    | theta ccw
            |       |  x    |
            |       |       |
            |     y v       |
            +---------------+
            3     Front     2
        """

        self.sharps_pos = {
            2: Vector2(x=0, y=320),
            3: Vector2(x=0, y=320),
        }

        self.sharps_side = {
            0: 'rear',
            1: 'read',
            2: 'front',
            3: 'front',

        }

        self.sharp_state = {
            n: None for n in range(8)
        }

        self.other_robot = {
            'pmi': 'pal',
            'pal': 'pmi',
        }

        # TODO: Use rotated rectangles for better accuracy
        self.robots_shapes = {
            'pal': Circle(x=0, y=0, r=150),
            'pmi': Circle(x=0, y=0, r=100),
        }

    @Service.event('log.sharp.on')
    def sharp_on(self, n: 'int'):
        """When a sharp is triggered"""
        n = int(n)

        # Which robot is the sharp on?
        robot = self.sharps_robots[n]

        # Compute the position of the object #
        robot_pos = Vector3(**self.cs.trajman[robot].get_position())
        # Get sharp base position
        base_pos = self.sharps_pos[n]
        # Rotate sharp to match the robot's angle
        sharp_pos = base_pos.rotated_by(robot_pos.theta)

        obj_pos = robot_pos.to_2() + sharp_pos

        if not Map.inside(obj_pos, self.sharp_map_margin()):
            self.log(what='outside_map', obj=obj_pos, sharp=n)
            return

        # No immediate avoidance if not in the same direction of the robot
        robot_moving_side = self.cs.trajman[robot].get_vector_trsl()

        # Ignore if it's on the opposite side of its movement
        sharp_side = self.sharps_side[n]
        if ((sharp_side == 'front' and robot_moving_side['trsl_vector'] < 0)
           or (sharp_side == 'rear' and robot_moving_side['trsl_vector'] > 0)):
            self.log(what='other_side', obj=obj_pos, sharp=n)
            return

        # Check if it's the other robot
        other_robot = self.other_robot[robot]
        other_pos = Vector3(**self.cs.trajman[other_robot].get_position())
        other = self.robots_shapes[other_robot]
        other = other._replace(x=other_pos.x, y=other_pos.x)
        if other.contains(obj_pos):
            self.log(what='{}_detect_{}'.format(robot, other_robot),
                     obj=obj_pos, sharp=n)
            return

        self.log(sharp=n, robot=robot, x=obj_pos.x, y=obj_pos.y)


def main():
    sharpavoid = SharpAvoid()
    sharpavoid.run()

if __name__ == '__main__':
    main()
