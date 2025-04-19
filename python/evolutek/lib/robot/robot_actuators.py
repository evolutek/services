from enum import Enum
from evolutek.lib.status import RobotStatus
from evolutek.lib.utils.color import Color
from evolutek.lib.utils.task import async_task
from evolutek.lib.utils.wrappers import if_enabled
from time import sleep, time
from evolutek.lib.actuators.i2c_acts import I2CActsHandler, I2CActType, ESCVariation
from evolutek.lib.actuators.ax12 import AX12Controller


# ====== Elevator ======

class ElevatorId(Enum):
    FRONT_CANS = 0
    FRONT_PLANK = 1
    BACK_CANS = 2
    BACK_PLANK = 3

class ElevatorPosition(Enum):
    GRAB_LOW = (315, 656)
    LIFT_LOW = (409, 560)
    GRAB_HIGH = (512, 452)
    LIFT_HIGH = (677, 293)
    PLACE_BANNER = (677, 293)
    LIFT_BANNER = (677, 293)

@if_enabled
@async_task
def move_elevator(self, elevator_id: ElevatorId, position: ElevatorPosition, wait = True):
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
            threshold = 1100
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


# ====== Plank Arm ======

class PlankArmId(Enum):
    FRONT = 0
    BACK = 1

class PlankArmPosition(Enum):
    COLLAPSED = (180, 175)
    EXPANDED = (120, 115)

# Map clamps to their servo id
CLAMP_ID_TO_SERVO_ID = [2, 3, 4]

@if_enabled
@async_task
def move_plank_arm(self, plank_arm_id: PlankArmId, position: PlankArmPosition):
    if isinstance(position, str):
        position = ClampsPosition[position]
    _ids = []
    for id in ids:
        _ids.append(int(id))
    status = []
    for clamp_id in _ids:
        status.append(self.actuators.servo_set_angle(CLAMP_ID_TO_SERVO_ID[clamp_id], position.value[clamp_id]))
    return RobotStatus.check(*status)


# ====== Magnets ======

class MagnetId(Enum):
    FRONT_MAGNET_1 = 0
    FRONT_MAGNET_2 = 1
    FRONT_MAGNET_3 = 2
    FRONT_MAGNET_4 = 3
    BACK_MAGNET_1 = 4
    BACK_MAGNET_2 = 5
    BACK_MAGNET_3 = 6
    BACK_MAGNET_4 = 7

class MagnetsSet(Enum):
    FRONT_MAGNETS = [
        MagnetId.FRONT_MAGNET_1,
        MagnetId.FRONT_MAGNET_2,
        MagnetId.FRONT_MAGNET_3,
        MagnetId.FRONT_MAGNET_4
    ]
    BACK_MAGNETS = [
        MagnetId.BACK_MAGNET_1,
        MagnetId.BACK_MAGNET_2,
        MagnetId.BACK_MAGNET_3,
        MagnetId.BACK_MAGNET_4
    ]

# TODO: Set angles
class MagnetState(Enum):
    ENABLE = {
        MagnetId.FRONT_MAGNET_1: 0,
        MagnetId.FRONT_MAGNET_2: 0,
        MagnetId.FRONT_MAGNET_3: 0,
        MagnetId.FRONT_MAGNET_4: 0,
        MagnetId.BACK_MAGNET_1: 0,
        MagnetId.BACK_MAGNET_2: 0,
        MagnetId.BACK_MAGNET_3: 0,
        MagnetId.BACK_MAGNET_4: 0
    }
    DISABLE = {
        MagnetId.FRONT_MAGNET_1: 90,
        MagnetId.FRONT_MAGNET_2: 90,
        MagnetId.FRONT_MAGNET_3: 90,
        MagnetId.FRONT_MAGNET_4: 90,
        MagnetId.BACK_MAGNET_1: 90,
        MagnetId.BACK_MAGNET_2: 90,
        MagnetId.BACK_MAGNET_3: 90,
        MagnetId.BACK_MAGNET_4: 90
    }

@if_enabled
@async_task
def toggle_magnets(self, magnets: MagnetsSet, state: MagnetState):
    if isinstance(magnet_id, str):
        magnet_id = MagnetId[magnet_id]

    if isinstance(state, str):
        state = MagnetState[state]

    ids = list(map(lambda x: x.value, magnets.value))
    angles = list(map(lambda x: state.value[x], magnets.value))

    return RobotStatus.check(self.actuators.servos_set_angles(ids, angles))


# ====== Pumps ======

# TODO
class PumpsSet(Enum):
    FRONT_PLANK = [0, 1]
    BACK_PLANK = [2, 3]

@if_enabled
@async_task
def toggle_pumps(self, pumps: PumpsSet, grab: bool):
    if isinstance(pumps, str):
        pumps = PumpsSet[pumps]

    if grab:
        return RobotStatus.check(self.actuators.pumps_grab(pumps.value))
    else:
        return RobotStatus.check(self.actuators.pumps_drop(pumps.value))
