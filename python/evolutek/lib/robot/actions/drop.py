from evolutek.lib.robot.robot_actions_imports import *


@if_enabled
@async_task
def drop_n(self):
    robot_pos = Point(dict=self.trajman.get_position())

    if (len(self.HOLDING) == 0):
        return RobotStatus.return_status(RobotStatus.Done)

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
        self.HOLDING.pop()
    print(f"HOLDING : {self.HOLDING}")

    return RobotStatus.return_status(RobotStatus.Done, score=3)


@if_enabled
@async_task
def drop_all(self):
    status = []
    status.append(self.clamp_open(async_task=False))
    sleep(0.5)
    status.append(self.forward(-140, async_task=False))
    print("******************* Status :", status)
    return check_status(*status, score=3)
    
