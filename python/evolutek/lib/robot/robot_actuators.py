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
    LOW = (360, 610)
    BORDER = (420, 560)
    HIGH = (720, 250)

@if_enabled
@async_task
def move_elevator(self, position: ElevatorPosition):
    if isinstance(position, str):
        position = ElevatorPosition[position]
    if position == ElevatorPosition.HIGH:
        self.actuators.ax_set_speed(1, 450)
        self.actuators.ax_set_speed(2, 450)
    else:
        self.actuators.ax_set_speed(1, 170)
        self.actuators.ax_set_speed(2, 170)
    status1 = self.actuators.ax_move(1, position.value[0]) # Right servo
    status2 = self.actuators.ax_move(2, position.value[1]) # Left servo
    return RobotStatus.check(status1, status2)


# ====== Clamps ======

# TODO: Use correct angles
# This a list of angle with one angle per clamp,
# so here there list of length 3, so there is 3 clamps
class ClampsPosition(Enum):
    OPEN = [180, 175, 180]
    CLOSE = [138, 138, 138]

# Map clamps to their servo id
CLAMP_ID_TO_SERVO_ID = [2, 3, 4]

@if_enabled
@async_task
def move_clamps(self, ids: list[int], position: ClampsPosition):
    if isinstance(position, str):
        position = ClampsPosition[position]
    _ids = []
    for id in ids:
        _ids.append(int(id))
    status = []
    for clamp_id in _ids:
        status.append(self.actuators.servo_set_angle(CLAMP_ID_TO_SERVO_ID[clamp_id], position.value[clamp_id]))
    return RobotStatus.check(*status)


# ====== Herse ======

# TODO: Use correct angles
# This a an enum of pair of angle
# (the first angle is the right servo and the second is the left servo)
class HersePosition(Enum):
    UP = [173, 36]
    MIDDLE = [121, 90]
    DOWN = [74, 140]

@if_enabled
@async_task
def move_herse(self, position: HersePosition):
    if isinstance(position, str):
        position = HersePosition[position]
    status1 = self.actuators.servo_set_angle(0, position.value[0]) # Right servo
    status2 = self.actuators.servo_set_angle(1, position.value[1]) # Left servo
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
    return RobotStatus.check(self.actuators.ax_move(3, position.value))


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


# ====== Arms ======

# TODO: Use correct angles
# Right then left angle
class ArmsPosition(Enum):
    OPEN = (85, 98)
    CLOSE = (170, 18)

# Map clamps to their servo id
ARM_ID_TO_SERVO_ID = [5, 6]

@if_enabled
@async_task
def move_arm(self, id: int, position: ArmsPosition):
    id = int(id)
    if isinstance(position, str):
        position = HersePosition[position]
    return RobotStatus.check(self.actuators.servo_set_angle(ARM_ID_TO_SERVO_ID[id], position.value[id]))
