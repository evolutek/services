from enum import Enum
from evolutek.lib.status import RobotStatus
from evolutek.lib.utils.color import Color
from evolutek.lib.utils.task import async_task
from evolutek.lib.utils.wrappers import if_enabled
from time import sleep
from evolutek.lib.actuators.i2c_acts import I2CActsHandler, I2CActType, ESCVariation
from evolutek.lib.actuators.ax12 import AX12Controller

from evolutek.services.robot import Robot


# TODO: Use correct angles
# This a an enum of pair of angle
# (the first angle is the left servo and the second is the right servo)
class ElevatorPosition(Enum):
    LOW = (0, 45)
    HIGH = (45, 0)

@if_enabled
@async_task
def move_elevator(self: Robot, position: ElevatorPosition):
    # TODO: Use correct servo id
    status1 = self.actuators.servo_set_angle(1, position[0])
    status2 = self.actuators.servo_set_angle(2, position[1])
    return RobotStatus.check(status1, status2)


# TODO: Use correct angles
# This a list of angle with one angle per clamp,
# so here there list of length 3, so there is 3 clamps
class ClampsPosition(Enum):
    OPEN = [45, 45, 45]
    CLOSE = [0, 0, 0]

# Map clamps to their servo id
CLAMP_ID_TO_SERVO_ID = [2, 3, 4]

@if_enabled
@async_task
def move_clamps(self: Robot, clamp_ids: list[int], position: ClampsPosition):
    status = []
    for clamp_id in clamp_ids:
        status.append(self.actuators.servo_set_angle(CLAMP_ID_TO_SERVO_ID[clamp_id], position[clamp_id]))
    return RobotStatus.check(*status)


# Magnet id is 0, 1 or 2

@if_enabled
@async_task
def magnets_on(self: Robot, magnet_ids: list[int]):
    return RobotStatus.check(self.actuators.magnets_on(magnet_ids))

@if_enabled
@async_task
def magnets_off(self: Robot, magnet_ids: list[int]):
    return RobotStatus.check(self.actuators.magnets_off(magnet_ids))
