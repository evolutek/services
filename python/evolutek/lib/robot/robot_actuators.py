from enum import Enum
from evolutek.lib.status import RobotStatus
from evolutek.lib.utils.color import Color
from evolutek.lib.utils.task import async_task
from evolutek.lib.utils.wrappers import if_enabled
from time import sleep, time
from evolutek.lib.actuators.i2c_acts import I2CActsHandler, I2CActType, ESCVariation
from evolutek.lib.actuators.ax12 import AX12Controller


# ====== Elevator ======

# TODO: Use correct angles (ax12 angles)
# This a an enum of pair of angle
# (the first angle is the right servo and the second is the left servo)
class ElevatorPosition(Enum):
    #LOWEST = (315, 656)
    LOW = (315, 656)
    BORDER = (409, 560)
    POTS = (512, 452)
    HIGH = (677, 293)

@if_enabled
@async_task
def move_elevator(self, position: ElevatorPosition, wait = True):
    if isinstance(position, str):
        position = ElevatorPosition[position]
    
    if position == ElevatorPosition.HIGH:
        self.actuators.ax_set_speed(1, 220)
        self.actuators.ax_set_speed(2, 220)
    else:
        self.actuators.ax_set_speed(1, 170)
        self.actuators.ax_set_speed(2, 170)
    
    status = RobotStatus.check(
        self.actuators.ax_move(1, position.value[0]), # Right servo
        self.actuators.ax_move(2, position.value[1]) # Left servo
    )

    if RobotStatus.get_status(status) != RobotStatus.Done:
        return status

    if wait:
        if position != ElevatorPosition.HIGH:
            threshold = 800
            # Check if the servos are forcing
            end_time = time() + (0.6 if position != ElevatorPosition.LOW else 0.8)
            while time() < end_time:
                if abs(self.actuators.ax_get_load(1)) > threshold or abs(self.actuators.ax_get_load(2)) > threshold:
                    self.actuators.ax_move(1, ElevatorPosition.HIGH.value[0]), # Right servo
                    self.actuators.ax_move(2, ElevatorPosition.HIGH.value[1])  # Left servo
                    return RobotStatus.return_status(RobotStatus.Failed)
                sleep(0.1)
        else:
            sleep(0.3)

    return RobotStatus.return_status(RobotStatus.Done)


# ====== Clamps ======

# TODO: Use correct angles
# This a list of angle with one angle per clamp,
# so here there list of length 3, so there is 3 clamps
class ClampsPosition(Enum):
    OPEN = [180, 175, 180]
    CLOSE = [120, 115, 125]

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
    UP = [696, 332]
    MIDDLE = [498, 529]
    DOWN = [331, 695]

@if_enabled
@async_task
def move_herse(self, position: HersePosition, wait = True):
    if isinstance(position, str):
        position = HersePosition[position]

    if position != HersePosition.DOWN:
        self.actuators.ax_set_speed(4, 450)
        self.actuators.ax_set_speed(5, 450)
    else:
        self.actuators.ax_set_speed(4, 250)
        self.actuators.ax_set_speed(5, 250)

    status = RobotStatus.check(
        self.actuators.ax_move(4, position.value[0]), # Right servo
        self.actuators.ax_move(5, position.value[1])  # Left servo
    )

    if RobotStatus.get_status(status) != RobotStatus.Done:
        return status

    if wait:
        if position == HersePosition.DOWN:
            # Check if the servo are forcing
            end_time = time() + 0.4
            while time() < end_time:
                if abs(self.actuators.ax_get_load(4)) > 800 or abs(self.actuators.ax_get_load(5)) > 800:
                    self.actuators.ax_move(4, HersePosition.MIDDLE.value[0]), # Right servo
                    self.actuators.ax_move(5, HersePosition.MIDDLE.value[1])  # Left servo
                    return RobotStatus.return_status(RobotStatus.Failed)
                sleep(0.05)
        else:
            sleep(0.3)

    return RobotStatus.return_status(RobotStatus.Done)


# ====== Rack ======

# TODO: Use correct angles (ax12 angles)
class RackPosition(Enum):
    FOLDED = 512
    POTS = 200
    PLANTS = 100
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
    CLOSE = (175, 18)

# Map clamps to their servo id
ARM_ID_TO_SERVO_ID = [0, 1]

@if_enabled
@async_task
def move_arm(self, id: int, position: ArmsPosition):
    id = int(id)
    if isinstance(position, str):
        position = ArmsPosition[position]
    return RobotStatus.check(self.actuators.servo_set_angle(ARM_ID_TO_SERVO_ID[id], position.value[id]))
