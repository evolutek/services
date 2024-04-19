from enum import Enum
from evolutek.lib.status import RobotStatus
from evolutek.lib.utils.color import Color
from evolutek.lib.utils.task import async_task
from evolutek.lib.utils.wrappers import if_enabled
from time import sleep
from evolutek.lib.actuators.i2c_acts import I2CActsHandler, I2CActType, ESCVariation
from evolutek.lib.actuators.ax12 import AX12Controller


# ====== Elevator ======

# TODO: Use correct angles (ax12 angles)
# This a an enum of pair of angle
# (the first angle is the right servo and the second is the left servo)
class ElevatorPosition(Enum):
    LOW = (350, 620)
    BORDER = (420, 560)
    HIGH = (720, 250)

@if_enabled
@async_task
def move_elevator(self, position: ElevatorPosition):
    if isinstance(position, str):
        position = ElevatorPosition[position]
    # TODO: Use correct servo id
    status1 = self.actuators.servo_set_angle(1, position.value[0]) # Right servo
    status2 = self.actuators.servo_set_angle(2, position.value[1]) # Left servo
    return RobotStatus.check(status1, status2)


# ====== Clamps ======

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
def move_clamps(self, clamp_ids: list[int], position: ClampsPosition):
    if isinstance(position, str):
        position = ClampsPosition[position]
    status = []
    for clamp_id in clamp_ids:
        status.append(self.actuators.servo_set_angle(CLAMP_ID_TO_SERVO_ID[clamp_id], position.value[clamp_id]))
    return RobotStatus.check(*status)


# ====== Herse ======

# TODO: Use correct angles
# This a an enum of pair of angle
# (the first angle is the right servo and the second is the left servo)
class HersePosition(Enum):
    UP = [160, 20]
    MIDDLE = [110, 70]
    DOWN = [50, 130]

@if_enabled
@async_task
def move_herse(self, position: HersePosition):
    if isinstance(position, str):
        position = HersePosition[position]
    status1 = self.actuators.servo_set_angle(1, position.value[0]) # Right servo
    status2 = self.actuators.servo_set_angle(2, position.value[1]) # Left servo
    return RobotStatus.check(status1, status2)


# ====== Rack ======

# TODO: Use correct angles (ax12 angles)
class RackPosition(Enum):
    FOLDED = 512
    UNFOLDED = 0

@if_enabled
@async_task
def move_rack(self, position: RackPosition):
    if isinstance(position, str):
        position = RackPosition[position]
    # TODO: Use correct servo id
    return RobotStatus.check(self.actuators.servo_set_angle(1, position.value))


# ====== Magnets ======

# Magnet id is 0, 1 or 2

@if_enabled
@async_task
def magnets_on(self, magnet_ids: list[int]):
    return RobotStatus.check(self.actuators.magnets_on(magnet_ids))

@if_enabled
@async_task
def magnets_off(self, magnet_ids: list[int]):
    return RobotStatus.check(self.actuators.magnets_off(magnet_ids))
