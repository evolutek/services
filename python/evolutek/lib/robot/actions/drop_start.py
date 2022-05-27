from evolutek.lib.robot.robot_actions_imports import *


@if_enabled
@async_task
def drop_start(self):
    self.goto_avoid(380,225, async_task=False)
    self.goth(theta=0, async_task=False)

    scor = 0
    sensors = self.actuators.proximity_sensors.read_all_sensors()
    scor += sensors[0] + sensors[2]


    self.pumps_drop(ids="1", async_task=False)
    self.pumps_drop(ids="3", async_task=False)

    return RobotStatus.return_status(RobotStatus.Done, score=scor)
