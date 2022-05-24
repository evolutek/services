from evolutek.lib.robot.robot_trajman import RecalSensor
from evolutek.lib.settings import ROBOT
from evolutek.lib.status import RobotStatus
from evolutek.lib.utils.color import Color
from evolutek.lib.utils.task import async_task
from evolutek.lib.utils.wrappers import if_enabled
from evolutek.lib.robot.robot_actuators import ElevatorConfig, HeadConfig, FrontArmsEnum, HeadSpeed, ElevatorSpeed

from time import sleep
from math import pi


def pickup_statuette(self):
    # Mid and prepare to pickup
    self.set_elevator_config(arm=FrontArmsEnum.Center, config=ElevatorConfig.Mid, async_task=False)
    self.set_head_config(arm=FrontArmsEnum.Center, config=HeadConfig.Pickup, async_task=False)
    self.pumps_get(ids="2", async_task=False) # Pump the central arm pump
    sleep(0.5)
    # Pickup
    self.set_elevator_config(arm=FrontArmsEnum.Center, config=ElevatorConfig.StoreStatuette, async_task=False)
    sleep(0.2)
    self.pumps_drop(ids="4", async_task=False)
    sleep(1)
    return (self.actuators.proximity_sensor_read(id = 2))
