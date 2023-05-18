from evolutek.lib.robot.robot_actions_imports import *
from math import pi


@if_enabled
@async_task
def build_cakes_raw(self, center, positions):
    cake_bot_dist = 120
    current_drop_level = 0
    current_position_index = 0
    nb_positions = len(positions)
    score = 0

    while current_drop_level < 3 and 0 <= current_position_index < nb_positions:
        # Compute real destination coordinates for each cake positions
        pos = positions[current_position_index]
        delta = Point.substract(pos, center)
        length = pos.dist(center)
        direction = Point(delta.x / length, delta.y / length)
        destination = Point.substract(pos, Point(direction.x * cake_bot_dist, direction.y * cake_bot_dist))

        # Goto cake position
        self.goth(theta = center.compute_angle(destination), async_task=False, mirror=False)
        r = self.goto_avoid(x=destination.x, y=destination.y, async_task=False, mirror=False)
        #if r != RobotStatus.Done and r != RobotStatus.Reached:
        #    return RobotStatus.return_status(RobotStatus.Failed, score=score)
        #sleep(destination.dist(center) / 200)

        # Is the cake position is on the edge of the positions list ?
        edge = (current_position_index == 0 and current_drop_level > 0) or current_position_index == nb_positions - 1

        # Drop 1 or 2 cake layer
        if edge and current_drop_level < 2:
            r = self.drop_until(amount = 2, drop_level = current_drop_level, async_task=False)
        else:
            r = self.drop_until(amount = 1, drop_level = current_drop_level, async_task=False)
        r = RobotStatus.get_status(r)
        if r != RobotStatus.Done and r != RobotStatus.Reached:
            return RobotStatus.return_status(RobotStatus.Failed, score=score)
    
        score += 2 if edge and current_drop_level < 2 else 1
        
        if current_drop_level == 2:
            score += 4

        # Return back to center
        r = RobotStatus.get_status(self.goto_avoid(x=center.x, y=center.y, async_task=False, mirror=False))
        if r != RobotStatus.Done and r != RobotStatus.Reached:
            return RobotStatus.return_status(RobotStatus.Failed, score=score)

        if edge:
            current_drop_level += 1
        current_position_index += 1 if current_drop_level % 2 == 0 else -1

    return RobotStatus.return_status(RobotStatus.Done, score=score)


@if_enabled
@async_task
def build_cakes(self, theta):
    dist = 120 * 2
    theta = float(theta)
    if not self.side:
        theta *= -1
    center = Point(dict=self.trajman.get_position())
    a = center.compute_delta_point(theta - pi / 2, dist)
    b = center.compute_delta_point(theta, dist)
    c = center.compute_delta_point(theta + pi / 2, dist)
    print(a, b, c, center)
    return self.build_cakes_raw(center, [a, b, c], async_task = False)
