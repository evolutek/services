from evolutek.lib.robot.robot_actions_imports import *


@if_enabled
@async_task
def drop_n(self):
    robot_pos = Point(dict=self.trajman.get_position())

    status = RobotStatus.get_status(self.elevator_move("Low", async_task=False))
    print(status)
    sleep(0.5)

    status = RobotStatus.get_status(self.clamp_open(async_task=False))
    print(status)
    sleep(0.5)

    status = RobotStatus.get_status(self.elevator_move("GetFourth", async_task=False))
    print(status)
    sleep(0.5)

    status = RobotStatus.get_status(self.clamp_close(async_task=False))
    print(status)
    sleep(0.5)

    status = RobotStatus.get_status(self.elevator_move("High", async_task=False))
    print(status)
    sleep(0.5)

    print("move trsl")
    status = RobotStatus.get_status(self.move_trsl(acc=100, dec=100, maxspeed=500, dest=120, sens=0))
    print(status)
    sleep(0.5)
    print("trsl done")

    status = RobotStatus.get_status(self.elevator_move("Low", async_task=False))
    print(status)
    sleep(0.5)

    for i in range(3):
        HOLDING.pop()
    print(f"HOLDING : {HOLDING}")

    return RobotStatus.return_status(RobotStatus.Done, score=3)


@if_enabled
@async_task
def drop_all(self):
    zone_pos = Point(dict=self.mirror_pos(275, 225))

    robot_point = Point(dict=self.trajman.get_position())
    dest_point = robot_point.compute_offset_point(zone_pos, -160)
    status = self.goth(robot_point.compute_angle(dest_point), async_task=False, mirror=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached:
        return RobotStatus.return_status(RobotStatus.get_status(status))

    status = self.goto_avoid(x=dest_point.x, y=dest_point.y, async_task=False, mirror=False, timeout=10)
    if RobotStatus.get_status(status) != RobotStatus.Reached:
        return RobotStatus.return_status(RobotStatus.get_status(status))

    # On va en zone
    dest_point = robot_point.compute_offset_point(zone_pos, -110)
    status = self.goto_avoid(x=dest_point.x, y=dest_point.y, async_task=False, mirror=False, timeout=10)
    if RobotStatus.get_status(status) != RobotStatus.Reached:
        return RobotStatus.return_status(RobotStatus.get_status(status))

    status = RobotStatus.get_status(self.elevator_move("Low", async_task=False))
    sleep(1)

    # On drop la pile
    self.clamp_open(async_task=False)
    sleep(0.5)

    # On recule pour manoeuvrer
    go_to_point = robot_point.compute_offset_point(zone_pos, -225)
    status = self.goto_avoid(x=go_to_point.x, y=go_to_point.y, mirror=False, async_task=False, timeout=10)
    if RobotStatus.get_status(status) != RobotStatus.Reached:
        return RobotStatus.return_status(RobotStatus.get_status(status))
    #sleep(5)

    return RobotStatus.return_status(RobotStatus.Done, score=3)