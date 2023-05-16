from evolutek.lib.robot.robot_actions_imports import *

@if_enabled
@async_task
def drop_and_cherry(self, n):
    # if (len(self.HOLDING) == 0):
    #     return RobotStatus.return_status(RobotStatus.Done)

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

    status = RobotStatus.get_status(self.canon_off(async_task=False))
    print(status)
    sleep(0.2)

    status = RobotStatus.get_status(self.push_tank(async_task=False))
    print(status)
    sleep(0.2)

    status = RobotStatus.get_status(self.push_canon(async_task=False))
    print(status)
    sleep(0.2)

    return check_status()