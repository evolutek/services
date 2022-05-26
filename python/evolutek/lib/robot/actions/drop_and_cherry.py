from evolutek.lib.robot.robot_actions_imports import *

@if_enabled
@async_task
def drop_and_cherry(self, n):
    status = []

    if (len(self.HOLDING) == 0):
        return RobotStatus.return_status(RobotStatus.Done)

    status.append(self.elevator_move("Low", async_task=False))
    sleep(0.5)

    status.append(self.clamp_open(async_task=False))
    sleep(0.5)

    status.append(self.elevator_move("GetFourth", async_task=False))
    sleep(0.5)

    status.append(self.clamp_close(async_task=False))
    sleep(0.5)

    status.append(self.elevator_move("High", async_task=False))
    sleep(0.5)

    status.append(self.canon_off(async_task=False))
    sleep(0.2)

    status.append(self.push_tank(async_task=False))
    sleep(0.2)

    status.append(self.push_canon(async_task=False))
    sleep(0.2)

    status.append(self.push_tank(async_task=False))
    sleep(1.2)

    if (self.proximity_sensor_read(id = 2)):
        return RobotStatus.check(*status, score = 3)
    return RobotStatus.check(*status, score = 0)
