from evolutek.lib.robot.robot_trajman import RecalSensor
from evolutek.lib.settings import ROBOT
from evolutek.lib.status import RobotStatus
from evolutek.lib.utils.color import Color
from evolutek.lib.utils.task import async_task
from evolutek.lib.utils.wrappers import if_enabled

from time import sleep
from math import pi




@if_enabled
def statuette(self):
    self.trajman.free()
    self.trajman.unfree()
    self.actuators.pumps_get(ids='4')
    self.robot.set_head_config(arm=2, config=0)
    self.robot.set_elevator_config(arm=2, config=2)
    print('Please poot the statuette')
    self.actuators.pumps_get(ids='2')
    self.robot.set_elevator_config(arm=2, config=5)
    sleep(0.5)
    self.actuators.pumps_drop(ids='4')
    self.robot.set_head_config(arm=2, config=2)
    self.robot.set_elevator_config(arm=2, config=2)
    status = self.robot.goto_avoid(120, 225)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(RobotStatus.get_status(status))
    self.actuators.pumps_drop(ids='2')
    status = self.robot.goto_avoid(250, 225)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(RobotStatus.get_status(status))
    self.robot.set_head_config(arm=2, config=0)
    self.robot.set_elevator_config(arm=2, config=5)

    return RobotStatus.return_status(RobotStatus.Done)