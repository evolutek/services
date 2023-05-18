from evolutek.lib.robot.robot_actions_imports import *

@if_enabled
@async_task
def disguise(self, enable=True):
    self.actuators.orange_led_strip_set(enable)
    return RobotStatus.return_status(RobotStatus.Done)
