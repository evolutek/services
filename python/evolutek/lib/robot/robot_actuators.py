from enum import Enum
from evolutek.lib.utils.boolean import get_boolean
from evolutek.lib.status import RobotStatus
from evolutek.lib.utils.color import Color
from evolutek.lib.utils.task import async_task
from evolutek.lib.utils.wrappers import if_enabled
from time import sleep, time
from evolutek.lib.actuators.i2c_acts import I2CActsHandler, I2CActType, ESCVariation
from evolutek.lib.actuators.ax12 import AX12Controller


# ====== Elevator ======

ELEVATOR_SPEED = 1000

# (Stepper ID)
class ElevatorId(Enum):
    FRONT = (0,)
    BACK = (2,)

class ElevatorPosition(Enum):
    LOWEST = {
        ElevatorId.FRONT: (0,),
        ElevatorId.BACK: (0,)
    }
    MIDDLE = {
        ElevatorId.FRONT: (-330,),
        ElevatorId.BACK: (-330,)
    }
    HIGHEST = {
        ElevatorId.FRONT: (-700,),
        ElevatorId.BACK: (-700,)
    }

@if_enabled
@async_task
def move_elevator(self, id: ElevatorId, position: ElevatorPosition):
    if isinstance(id, str):
        id = ElevatorId[id]

    if isinstance(position, str):
        position = ElevatorPosition[position]

    angles = position.value[id]

    status = RobotStatus.check(self.actuators.stepper_goto(
        id.value[0],
        angles[0],
        ELEVATOR_SPEED
    ))

    if RobotStatus.get_status(status) != RobotStatus.Done:
        return status

    #sleep(1)

    return RobotStatus.return_status(RobotStatus.Done)

@if_enabled
@async_task
def move_elevator_ex(self, id: ElevatorId, position: float, wait = True):
    if isinstance(id, str):
        id = ElevatorId[id]

    if isinstance(position, str):
        position = float(position)

    angles = (
        (ElevatorPosition.HIGHEST.value[id][0] - ElevatorPosition.LOWEST.value[id][0]) * position + ElevatorPosition.LOWEST.value[id][0]
    ,)

    status = RobotStatus.check(self.actuators.stepper_goto(
        id.value[0],
        angles[0],
        ELEVATOR_SPEED
    ))

    if RobotStatus.get_status(status) != RobotStatus.Done:
        return status

    #sleep(2)

    return RobotStatus.return_status(RobotStatus.Done)


# ====== Plank Arm ======

# (Right, Left)
class PlankArmId(Enum):
    FRONT = (5, 6)
    BACK = (5 + 16, 6 + 16)

class PlankArmPosition(Enum):
    LIFT = {
        PlankArmId.FRONT: (108, 90),
        PlankArmId.BACK: (108, 90)
    }
    EXPANDED = {
        PlankArmId.FRONT: (90, 110),
        PlankArmId.BACK: (90, 110)
    }
    COLLAPSED = {
        PlankArmId.FRONT: (180, 20),
        PlankArmId.BACK: (180, 20)
    }

@if_enabled
@async_task
def move_plank_arm(self, id: PlankArmId, position: PlankArmPosition):
    if isinstance(id, str):
        id = PlankArmId[id]

    if isinstance(position, str):
        position = PlankArmPosition[position]

    angles = position.value[id]

    status = RobotStatus.check(self.actuators.servos_set_angles(
        [id.value[0], id.value[1]],
        [angles[0], angles[1]]
    ))

    if RobotStatus.get_status(status) != RobotStatus.Done:
        return status

    #sleep(1)

    return RobotStatus.return_status(RobotStatus.Done)


# ====== Magnets ======

class MagnetId(Enum):
    FRONT_MAGNET_1 = 1
    FRONT_MAGNET_2 = 2
    FRONT_MAGNET_3 = 3
    FRONT_MAGNET_4 = 4
    BACK_MAGNET_1 = 1 + 16
    BACK_MAGNET_2 = 2 + 16
    BACK_MAGNET_3 = 3 + 16
    BACK_MAGNET_4 = 4 + 16

class MagnetsSetId(Enum):
    FRONT = [
        MagnetId.FRONT_MAGNET_1,
        MagnetId.FRONT_MAGNET_2,
        MagnetId.FRONT_MAGNET_3,
        MagnetId.FRONT_MAGNET_4
    ]
    BACK = [
        MagnetId.BACK_MAGNET_1,
        MagnetId.BACK_MAGNET_2,
        MagnetId.BACK_MAGNET_3,
        MagnetId.BACK_MAGNET_4
    ]

# TODO: Set angles
class MagnetState(Enum):
    DISABLE = {
        MagnetId.FRONT_MAGNET_1: 180,
        MagnetId.FRONT_MAGNET_2: 0,
        MagnetId.FRONT_MAGNET_3: 180,
        MagnetId.FRONT_MAGNET_4: 0,
        MagnetId.BACK_MAGNET_1: 180,
        MagnetId.BACK_MAGNET_2: 180,
        MagnetId.BACK_MAGNET_3: 180,
        MagnetId.BACK_MAGNET_4: 0
    }
    ENABLE = {
        MagnetId.FRONT_MAGNET_1: 0,
        MagnetId.FRONT_MAGNET_2: 180,
        MagnetId.FRONT_MAGNET_3: 0,
        MagnetId.FRONT_MAGNET_4: 180,
        MagnetId.BACK_MAGNET_1: 0,
        MagnetId.BACK_MAGNET_2: 0,
        MagnetId.BACK_MAGNET_3: 0,
        MagnetId.BACK_MAGNET_4: 180
    }

@if_enabled
@async_task
def toggle_magnets(self, id: MagnetsSetId, state: MagnetState):
    if isinstance(id, str):
        id = MagnetsSetId[id]

    if isinstance(state, str):
        state = MagnetState[state]

    ids = list(map(lambda x: x.value, id.value))
    angles = list(map(lambda x: state.value[x], id.value))

    status = RobotStatus.check(self.actuators.servos_set_angles(ids, angles))
    # TODO: Wait if status is OK ?

    return status


# ====== Pumps ======

# TODO
class PumpsSetId(Enum):
    FRONT = [0, 1]
    BACK = [2, 3]

@if_enabled
@async_task
def toggle_pumps(self, id: PumpsSetId, grab: bool):
    if isinstance(id, str):
        id = PumpsSetId[id]

    drop_delay = 0.5 # TODO: Do not hardcode

    grab = get_boolean(grab)

    if grab:
        return RobotStatus.check(self.actuators.pumps_grab(id.value))
    else:
        return RobotStatus.check(self.actuators.pumps_drop(id.value, drop_delay))


# ====== Pumps Arms ======

class PumpsArmId(Enum):
    FRONT = 0
    BACK = 16

class PumpsArmPosition(Enum):
    COLLAPSED = {
        PumpsArmId.FRONT: 20,
        PumpsArmId.BACK: 20
    }
    EXPANDED = {
        PumpsArmId.FRONT: 92,
        PumpsArmId.BACK: 92
    }
    ALMOST_EXPANDED = {
        PumpsArmId.FRONT: 80,
        PumpsArmId.BACK: 80
    }

@if_enabled
@async_task
def move_pumps_arm(self, id: PumpsArmId, position: PumpsArmPosition):
    if isinstance(id, str):
        id = PumpsArmId[id]

    if isinstance(position, str):
        position = PumpsArmPosition[position]

    angles = position.value[id]

    status = RobotStatus.check(self.actuators.servo_set_angle(
        id.value,
        position.value[id]
    ))

    if RobotStatus.get_status(status) != RobotStatus.Done:
        return status

    #sleep(1)

    return RobotStatus.return_status(RobotStatus.Done)


# ====== Side Arms ======

# (Right, Left)
class SideArmsId(Enum):
    FRONT = (1, 2)
    BACK = (3, 4)

# TODO: Set angles
class SideArmPosition(Enum):
    NORMAL   = {
        SideArmsId.FRONT: (205, 820),
        SideArmsId.BACK: (205, 820)
    }
    SPREADED = {
        SideArmsId.FRONT: (615, 410),
        SideArmsId.BACK: (615, 410)
    }

@if_enabled
@async_task
def move_side_arms(self, id: SideArmsId, position: SideArmPosition):
    if isinstance(id, str):
        id = SideArmsId[id]

    if isinstance(position, str):
        position = SideArmPosition[position]

    angles = position.value[id]

    status = RobotStatus.check(
        self.actuators.ax_move(id.value[0], angles[0]), # Right servo
        self.actuators.ax_move(id.value[1], angles[1])  # Left servo
    )

    if RobotStatus.get_status(status) != RobotStatus.Done:
        return status

    #sleep(1)

    return RobotStatus.return_status(RobotStatus.Done)
