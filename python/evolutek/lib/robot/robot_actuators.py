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
    FRONT = (0,)
    BACK = (1,)

class ElevatorPosition(Enum):
    LOWEST = {
        ElevatorId.FRONT: (-760,),
        ElevatorId.BACK: (-760,)
    }
    DROP = {
        ElevatorId.FRONT: (-740,),
        ElevatorId.BACK: (-740,)
    }
    MIDDLE = {
        ElevatorId.FRONT: (-500,),
        ElevatorId.BACK: (-500,)
    }
    REVERSE_DOWN = {
        ElevatorId.FRONT: (-200,),
        ElevatorId.BACK: (-200,)
    }
    REVERSE_UP = {
        ElevatorId.FRONT: (-140,),
        ElevatorId.BACK: (-140,)
    }
    START = {
        ElevatorId.FRONT: (-200,),
        ElevatorId.BACK: (-200,)
    }
    HIGHEST = {
        ElevatorId.FRONT: (-5,),
        ElevatorId.BACK: (-5,)
    }

@if_enabled
@async_task
def move_elevator(self, id: ElevatorId, pos: ElevatorPosition, speed: float = 1):
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
        ELEVATOR_SPEED * speed
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
    BACK_1 = (26, 21)
    BACK_2 = (27, 22)
    BACK_3 = (28, 23)
    BACK_4 = (29, 24)

class LiftingArmPosition(Enum):
    OPENED = 820
    REVERSE = 680
    PRE_GRAB = 593
    DROP = 512
    GRAB = 493 #512
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
    BACK_RIGHT = 21
    BACK_LEFT = 22

class CompactingArmPosition(Enum):
    OPENED = {
        CompactingArmId.FRONT_RIGHT: (155, 800),
        CompactingArmId.BACK_RIGHT: (155, 800),
        CompactingArmId.FRONT_LEFT: (870, 800),
        CompactingArmId.BACK_LEFT: (870, 800),
    }
    PRE_TASSED = {
        CompactingArmId.FRONT_RIGHT: (255, 800),
        CompactingArmId.BACK_RIGHT: (255, 800),
        CompactingArmId.FRONT_LEFT: (770, 800),
        CompactingArmId.BACK_LEFT: (770, 800),
    }
    TASSED = {
        CompactingArmId.FRONT_RIGHT: (305, 120),
        CompactingArmId.BACK_RIGHT: (305, 120),
        CompactingArmId.FRONT_LEFT: (720, 120),
        CompactingArmId.BACK_LEFT: (720, 120),
    }
    CLOSED = {
        CompactingArmId.FRONT_RIGHT: (600, 800),
        CompactingArmId.BACK_RIGHT: (600, 800),
        CompactingArmId.FRONT_LEFT: (425, 800),
        CompactingArmId.BACK_LEFT: (425, 800),
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

class ReversingArmHighId(Enum):
    FRONT = 5
    BACK = 25

class ReversingArmHighPosition(Enum):
    TOP = 545
    CLOSED = 840
    GROUND = 970

@if_enabled
@async_task
def move_reversing_arm_high(self, id: ReversingArmHighId, pos: ReversingArmHighPosition):
    if isinstance(id, str):
        id = ReversingArmHighId[id]

    if isinstance(pos, str):
        pos = ReversingArmHighPosition[pos]

    return RobotStatus.check(self.actuators.axs_moves(
        [id.value],
        [pos.value]
    ))


# ====== Reversing Arm ======

class ReversingArmId(Enum):
    FRONT_RIGHT = 3
    FRONT_LEFT = 4
    BACK_RIGHT = 23
    BACK_LEFT = 24

class ReversingArmPosition(Enum):
    CRATE1 = {
        ReversingArmId.FRONT_LEFT: None,
        ReversingArmId.BACK_LEFT: None,
        ReversingArmId.FRONT_RIGHT: 720,
        ReversingArmId.BACK_RIGHT: 720,
    }
    RIGHT_REVERSE = {
        ReversingArmId.FRONT_LEFT: None,
        ReversingArmId.BACK_LEFT: None,
        ReversingArmId.FRONT_RIGHT: 770,
        ReversingArmId.BACK_RIGHT: 770,
    }
    CRATE2 = {
        ReversingArmId.FRONT_LEFT: 104,
        ReversingArmId.BACK_LEFT: 104,
        ReversingArmId.FRONT_RIGHT: 820,
        ReversingArmId.BACK_RIGHT: 820,
    }
    CRATE3 = {
        ReversingArmId.FRONT_LEFT: 204,
        ReversingArmId.BACK_LEFT: 204,
        ReversingArmId.FRONT_RIGHT: 920,
        ReversingArmId.BACK_RIGHT: 920,
    }
    LEFT_REVERSE = {
        ReversingArmId.FRONT_LEFT: 254,
        ReversingArmId.BACK_LEFT: 254,
        ReversingArmId.FRONT_RIGHT: None,
        ReversingArmId.BACK_RIGHT: None,
    }
    CRATE4 = {
        ReversingArmId.FRONT_LEFT: 304,
        ReversingArmId.BACK_LEFT: 304,
        ReversingArmId.FRONT_RIGHT: None,
        ReversingArmId.BACK_RIGHT: None,
    }
    CLOSED = {
        ReversingArmId.FRONT_LEFT: 512,
        ReversingArmId.BACK_LEFT: 512,
        ReversingArmId.FRONT_RIGHT: 512,
        ReversingArmId.BACK_RIGHT: 512,
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
    FRONT_RIGHT = 12
    FRONT_LEFT = 13
    BACK_RIGHT = 7
    BACK_LEFT = 6

class ReversingHeadPosition(Enum):
    REVERSED = {
        ReversingHeadId.FRONT_RIGHT: 0,
        ReversingHeadId.FRONT_LEFT: 175,
        ReversingHeadId.BACK_RIGHT: 0,
        ReversingHeadId.BACK_LEFT: 175,
    }
    VERTICAL = {
        ReversingHeadId.FRONT_RIGHT: 70,
        ReversingHeadId.FRONT_LEFT: 180,
        ReversingHeadId.BACK_RIGHT: 70,
        ReversingHeadId.BACK_LEFT: 180,
    }
    NORMAL = {
        ReversingHeadId.FRONT_RIGHT: 180,
        ReversingHeadId.FRONT_LEFT: 0,
        ReversingHeadId.BACK_RIGHT: 180,
        ReversingHeadId.BACK_LEFT: 0,
    }

    #NORMAL = {
    #    ReversingHeadId.FRONT_RIGHT: 0,
    #    ReversingHeadId.FRONT_LEFT: 180
    #}
    #REVERSED = {
    #    ReversingHeadId.FRONT_RIGHT: 180,
    #    ReversingHeadId.FRONT_LEFT: 32
    #}

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
    RIGHT = 5
    LEFT = 4

class CursorArmPosition(Enum):
    DEPLOYED = {
        CursorArmSide.RIGHT: 87,
        CursorArmSide.LEFT: 95
    }
    CLOSED = {
        CursorArmSide.RIGHT: 146,
        CursorArmSide.LEFT: 35
    }

@if_enabled
@async_task
def move_cursor_arm(self, side: str, pos: CursorArmPosition):
    if isinstance(side, str):
        side = CursorArmSide[side]

    if isinstance(pos, str):
        pos = CursorArmPosition[pos]

    angle = pos.value[side]

    s = RobotStatus.check(self.actuators.servos_set_angles(
        [side.value],
        [angle]
    ))

    sleep(0.5)

    return s

def get_color(self, id: LiftingArmId) -> bool:
    if isinstance(id, str):
        id = LiftingArmId[id]

    color = self.actuators.color_sensor_read(id.value[1])
    if color[2] == 0:
        return self.side
    k = color[0] / color[2]

    return (k > 1.5) == self.side
