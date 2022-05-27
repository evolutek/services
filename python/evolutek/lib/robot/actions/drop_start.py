from evolutek.lib.robot.robot_actions_imports import *


@if_enabled
@async_task
def drop_start(self):
    scor = 0
    for e in self.actuators.proximity_sensor_read():
        scor += e*flip*3
    self.pumps_drop(ids="1", async_task=False)
    self.pumps_drop(ids="3", async_task=False)

    return RobotStatus.return_status(RobotStatus.Done, score=scor)
