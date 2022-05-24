from evolutek.lib.robot.robot_actions_imports import *
from evolutek.lib.utils.boolean import get_boolean

@if_enabled
@async_task
def drop_start(self):
    self.goto_avoid(x = 380, y = 225, async_task = False)
    self.goth(theta = 0, async_task = False)
    score = 1 if get_boolean(self.actuators.proximity_sensor_read(id = 1)) else 0
    score += 1 if get_boolean(self.actuators.proximity_sensor_read(id = 3)) else 0
    self.pumps_drop(ids="1,3", async_task=False)

    return RobotStatus.return_status(RobotStatus.Done, score=score)
