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

ELEVATOR_SPEED = 500

# (Stepper ID)
class ElevatorId(Enum):
    FRONT = (2,)
    #BACK = (None,)

class ElevatorPosition(Enum):
    LOWEST = {
        ElevatorId.FRONT: (-920,),
        #ElevatorId.BACK: (0,)
    }
    MIDDLE = {
        ElevatorId.FRONT: (-700,),
        #ElevatorId.BACK: (-330,)
    }
    REVERSE_DOWN = {
        ElevatorId.FRONT: (-350,),
        #ElevatorId.BACK: (-700,)
    }
    REVERSE_UP = {
        ElevatorId.FRONT: (-150,),
        #ElevatorId.BACK: (-700,)
    }
    HIGHEST = {
        ElevatorId.FRONT: (-5,),
        #ElevatorId.BACK: (-700,)
    }

@if_enabled
@async_task
def move_elevator(self, id: ElevatorId, pos: ElevatorPosition):
    if isinstance(id, str):
        id = ElevatorId[id]

    if isinstance(pos, str):
        pos = ElevatorPosition[pos]

    # angles = (
    #     (ElevatorPosition.HIGHEST.value[id][0] - ElevatorPosition.LOWEST.value[id][0]) * pos + ElevatorPosition.LOWEST.value[id][0]
    # ,)

    angles = pos.value[id]

    status = RobotStatus.check(self.actuators.stepper_goto(
        id.value[0],
        angles[0],
        ELEVATOR_SPEED
    ))

    if RobotStatus.get_status(status) != RobotStatus.Done:
        return status

    #sleep(2)

    return RobotStatus.return_status(RobotStatus.Done)


# ====== Lifting Arm ======

# Pair (AX20 id, color sensor id)
class LiftingArmId(Enum):
    FRONT_1 = (6, 1)
    FRONT_2 = (7, 2)
    FRONT_3 = (8, 3)
    FRONT_4 = (9, 4)

class LiftingArmPosition(Enum):
    OPENED = 820
    GRAB = 493 #512
    DROP = 512
    CLOSED = 335

@if_enabled
@async_task
def move_lifting_arm(self, id: LiftingArmId, pos: LiftingArmPosition):
    if isinstance(id, str):
        id = LiftingArmId[id]

    if isinstance(pos, str):
        pos = LiftingArmPosition[pos]

    return RobotStatus.check(self.actuators.axs_moves(
        [id.value[0]],
        [pos.value]
    ))


# ====== Compacting Arm ======

class CompactingArmId(Enum):
    FRONT_RIGHT = 1
    FRONT_LEFT = 2

class CompactingArmPosition(Enum):
    OPENED = {
        CompactingArmId.FRONT_RIGHT: (155, 800),
        CompactingArmId.FRONT_LEFT: (870, 800)
    }
    TASSED = {
        CompactingArmId.FRONT_RIGHT: (305, 120),
        CompactingArmId.FRONT_LEFT: (720, 120)
    }
    CLOSED = {
        CompactingArmId.FRONT_RIGHT: (600, 800),
        CompactingArmId.FRONT_LEFT: (425, 800)
    }

@if_enabled
@async_task
def move_compacting_arm(self, id: CompactingArmId, pos: CompactingArmPosition):
    if isinstance(id, str):
        id = CompactingArmId[id]

    if isinstance(pos, str):
        pos = CompactingArmPosition[pos]

    angle, speed = pos.value[id]

    return RobotStatus.check(self.actuators.axs_moves(
        [id.value],
        [angle],
        [speed]
    ))


# ====== Reversing Arm High ======

class ReversingArmHighPosition(Enum):
    TOP = 545
    CLOSED = 840
    GROUND = 970

@if_enabled
@async_task
def move_reversing_arm_high(self, pos: ReversingArmHighPosition):
    if isinstance(pos, str):
        pos = ReversingArmHighPosition[pos]

    return RobotStatus.check(self.actuators.axs_moves(
        [5],
        [pos.value]
    ))


# ====== Reversing Arm ======

class ReversingArmId(Enum):
    FRONT_RIGHT = 3
    FRONT_LEFT = 4

class ReversingArmPosition(Enum):
    CRATE1 = {
        ReversingArmId.FRONT_RIGHT: 720,
        ReversingArmId.FRONT_LEFT: None
    }
    CRATE2 = {
        ReversingArmId.FRONT_RIGHT: 820,
        ReversingArmId.FRONT_LEFT: 104
    }
    CRATE3 = {
        ReversingArmId.FRONT_RIGHT: 920,
        ReversingArmId.FRONT_LEFT: 204
    }
    CRATE4 = {
        ReversingArmId.FRONT_RIGHT: None,
        ReversingArmId.FRONT_LEFT: 304
    }
    CLOSED = {
        ReversingArmId.FRONT_RIGHT: 512,
        ReversingArmId.FRONT_LEFT: 512
    }

@if_enabled
@async_task
def move_reversing_arm(self, id: ReversingArmId, pos: ReversingArmPosition):
    if isinstance(id, str):
        id = ReversingArmId[id]

    if isinstance(pos, str):
        pos = ReversingArmPosition[pos]

    angle = pos.value[id]

    return RobotStatus.check(self.actuators.axs_moves(
        [id.value],
        [angle]
    ))


# ====== Reversing Head ======

class ReversingHeadId(Enum):
    FRONT_RIGHT = 0
    FRONT_LEFT = 1

class ReversingHeadPosition(Enum):
    NORMAL = {
        ReversingHeadId.FRONT_RIGHT: 0,
        ReversingHeadId.FRONT_LEFT: 180
    }
    REVERSED = {
        ReversingHeadId.FRONT_RIGHT: 180,
        ReversingHeadId.FRONT_LEFT: 32
    }

@if_enabled
@async_task
def move_reversing_head(self, id: ReversingHeadId, pos: ReversingHeadPosition):
    if isinstance(id, str):
        id = ReversingHeadId[id]

    if isinstance(pos, str):
        pos = ReversingHeadPosition[pos]

    angle = pos.value[id]

    return RobotStatus.check(self.actuators.servos_set_angles(
        [id.value],
        [angle]
    ))


# ====== Cursor Arm Side ======

class CursorArmSide(Enum):
    RIGHT = 2
    LEFT = 3

class CursorArmPosition(Enum):
    DEPLOYED = {
        CursorArmSide.RIGHT: 60,
        CursorArmSide.LEFT: 120
    }
    CLOSED = {
        CursorArmSide.RIGHT: 4,
        CursorArmSide.LEFT: 175
    }

@if_enabled
@async_task
def move_cursor_arm(self, side: str, pos: CursorArmPosition):
    if isinstance(side, str):
        side = ReversingHeadId[side]

    if isinstance(pos, str):
        pos = ReversingHeadPosition[pos]

    angle = pos.value[side]

    s = RobotStatus.check(self.actuators.servos_set_angles(
        [side.value],
        [angle]
    ))

    sleep(0.5)

    return s

@if_enabled
@async_task
def get_color(self, id: LiftingArmId) -> bool:
    if isinstance(id, str):
        id = LiftingArmId[id]

    color = self.actuators.color_sensor_read(id.value[1])
    k = color[0] / color[2]

    return (k > 1.5) == self.side
