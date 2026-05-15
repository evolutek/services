from evolutek.lib.robot.actions.actions import *
from evolutek.lib.robot.robot_actuators import *
from time import sleep


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from evolutek.services.robot import Robot


@if_enabled
@async_task
def do_cursor(self):
    arm = CursorArmSide.RIGHT if self.side else CursorArmSide.LEFT

    self.move_cursor_arm(arm, CursorArmPosition.DEPLOYED, async_task=False)
    sleep(0.5)
    self.goto_avoid(1800, 710, async_task=False)
    self.move_cursor_arm(arm, CursorArmPosition.CLOSED, async_task=False)
    sleep(0.5)

    return RobotStatus.return_status(RobotStatus.Done)


@if_enabled
@async_task
def end_cursor(self):
    arm = CursorArmSide.RIGHT if self.side else CursorArmSide.LEFT

    self.move_cursor_arm(arm, CursorArmPosition.CLOSED, async_task=False)
    sleep(0.5)

    return RobotStatus.return_status(RobotStatus.Done)


@if_enabled
@async_task
def start_cursor(self):
    arm = CursorArmSide.RIGHT if self.side else CursorArmSide.LEFT

    self.move_cursor_arm(arm, CursorArmPosition.DEPLOYED, async_task=False)
    sleep(0.5)

    return RobotStatus.return_status(RobotStatus.Done)


@if_enabled
@async_task
def do_cursor_bis(self):
    arm = CursorArmSide.RIGHT if self.side else CursorArmSide.LEFT

    self.move_cursor_arm(arm, CursorArmPosition.DEPLOYED, async_task=False)
    sleep(0.5)
    self.goto_avoid_extend(1800, 710 + 300, async_task=False, acc=1000)
    self.move_cursor_arm(arm, CursorArmPosition.CLOSED, async_task=False)
    sleep(0.5)

    return RobotStatus.return_status(RobotStatus.Done)


@if_enabled
@async_task
def grab_all_crates(self, side: str):
    if side == "front":
        compacting_arms = [CompactingArmId.FRONT_LEFT, CompactingArmId.FRONT_RIGHT]
        lifting_arms = [LiftingArmId.FRONT_1, LiftingArmId.FRONT_2, LiftingArmId.FRONT_3, LiftingArmId.FRONT_4]
        elevator = ElevatorId.FRONT
        lifting_arms_pumps = [2, 3, 4, 5]
        move_direction = 1
    elif side == "back":
        compacting_arms = [CompactingArmId.BACK_LEFT, CompactingArmId.BACK_RIGHT]
        lifting_arms = [LiftingArmId.BACK_1, LiftingArmId.BACK_2, LiftingArmId.BACK_3, LiftingArmId.BACK_4]
        elevator = ElevatorId.BACK
        lifting_arms_pumps = [22, 23, 24, 25]
        move_direction = -1
    else:
        raise RuntimeError("Invalid side: %s" % side)

    self.move_elevator(elevator, ElevatorPosition.LOWEST, speed=0.5, async_task=False)

    for i in range(len(lifting_arms)):
        self.move_lifting_arm(lifting_arms[i], LiftingArmPosition.PRE_GRAB, async_task=False)

    self.move_compacting_arm(compacting_arms[0], CompactingArmPosition.OPENED, async_task=False)
    self.move_compacting_arm(compacting_arms[1], CompactingArmPosition.OPENED, async_task=False)
    sleep(0.2)

    self.forward(130 * move_direction, avoid=True, async_task=False)

    self.move_compacting_arm(compacting_arms[0], CompactingArmPosition.PRE_TASSED, async_task=False)
    self.move_compacting_arm(compacting_arms[1], CompactingArmPosition.PRE_TASSED, async_task=False)
    sleep(0.15)
    self.move_compacting_arm(compacting_arms[0], CompactingArmPosition.TASSED, async_task=False)
    self.move_compacting_arm(compacting_arms[1], CompactingArmPosition.TASSED, async_task=False)
    sleep(0.5)

    self.actuators.pumps_grab(ids = lifting_arms_pumps)

    for i in range(len(lifting_arms)):
        self.move_lifting_arm(lifting_arms[i], LiftingArmPosition.GRAB, async_task=False)
    sleep(0.15)

    self.move_compacting_arm(compacting_arms[0], CompactingArmPosition.OPENED, async_task=False)
    self.move_compacting_arm(compacting_arms[1], CompactingArmPosition.OPENED, async_task=False)
    sleep(0.06)

    sleep(0.5) # Wait elevator

    self.move_elevator(elevator, ElevatorPosition.MIDDLE, async_task=False)
    sleep(1)

    self.move_compacting_arm(compacting_arms[0], CompactingArmPosition.CLOSED, async_task=False)
    self.move_compacting_arm(compacting_arms[1], CompactingArmPosition.CLOSED, async_task=False)
    sleep(0.3)

    return RobotStatus.return_status(RobotStatus.Done, score=0)


@if_enabled
@async_task
def drop_all_crates(self, side: str):
    if side == "front":
        lifting_arms = [LiftingArmId.FRONT_1, LiftingArmId.FRONT_2, LiftingArmId.FRONT_3, LiftingArmId.FRONT_4]
        lifting_arms_pumps = [2, 3, 4, 5]
        move_direction = 1
    elif side == "back":
        lifting_arms = [LiftingArmId.BACK_1, LiftingArmId.BACK_2, LiftingArmId.BACK_3, LiftingArmId.BACK_4]
        lifting_arms_pumps = [22, 23, 24, 25]
        move_direction = -1
    else:
        raise RuntimeError("Invalid side: %s" % side)

    for arm in lifting_arms:
        self.move_lifting_arm(arm, LiftingArmPosition.DROP, async_task=False)
    sleep(0.5)

    self.actuators.pumps_drop(ids = lifting_arms_pumps)
    sleep(0.2)

    for arm in lifting_arms:
        self.move_lifting_arm(arm, LiftingArmPosition.OPENED, async_task=False)
    sleep(0.5)

    self.forward(-160 * move_direction, avoid=True, async_task=False)

    return RobotStatus.return_status(RobotStatus.Done)


@if_enabled
@async_task
def lift_crates(self, side: str):
    if side == "front":
        lifting_arms = [LiftingArmId.FRONT_1, LiftingArmId.FRONT_2, LiftingArmId.FRONT_3, LiftingArmId.FRONT_4]
        elevator = ElevatorId.FRONT
    elif side == "back":
        lifting_arms = [LiftingArmId.BACK_1, LiftingArmId.BACK_2, LiftingArmId.BACK_3, LiftingArmId.BACK_4]
        elevator = ElevatorId.BACK
    else:
        raise RuntimeError("Invalid side: %s" % side)

    self.move_elevator(elevator, ElevatorPosition.MIDDLE, async_task=False)

    for arm in lifting_arms:
        self.move_lifting_arm(arm, LiftingArmPosition.OPENED, async_task=False)

    sleep(1)

    return RobotStatus.return_status(RobotStatus.Done)


@if_enabled
@async_task
def store_crates(self, side: str):
    if side == "front":
        lifting_arms = [LiftingArmId.FRONT_1, LiftingArmId.FRONT_2, LiftingArmId.FRONT_3, LiftingArmId.FRONT_4]
        elevator = ElevatorId.FRONT
    elif side == "back":
        lifting_arms = [LiftingArmId.BACK_1, LiftingArmId.BACK_2, LiftingArmId.BACK_3, LiftingArmId.BACK_4]
        elevator = ElevatorId.BACK
    else:
        raise RuntimeError("Invalid side: %s" % side)

    self.move_elevator(elevator, ElevatorPosition.HIGHEST, async_task=False)
    sleep(1.4)

    for arm in lifting_arms:
        self.move_lifting_arm(arm, LiftingArmPosition.CLOSED, async_task=False)
    sleep(0.5)

    return RobotStatus.return_status(RobotStatus.Done)


@if_enabled
@async_task
def drop_good_crates(self, side: str):
    if side == "front":
        lifting_arms = [LiftingArmId.FRONT_1, LiftingArmId.FRONT_2, LiftingArmId.FRONT_3, LiftingArmId.FRONT_4]
        elevator = ElevatorId.FRONT
        lifting_arms_pumps = [2, 3, 4, 5]
        move_direction = 1
    elif side == "back":
        lifting_arms = [LiftingArmId.BACK_1, LiftingArmId.BACK_2, LiftingArmId.BACK_3, LiftingArmId.BACK_4]
        elevator = ElevatorId.BACK
        lifting_arms_pumps = [22, 23, 24, 25]
        move_direction = -1
    else:
        raise RuntimeError("Invalid side: %s" % side)

    # Read color sensors
    colors = []
    for arm in lifting_arms:
        colors.append(self.get_color(arm))

    # Prepare to drop
    for i, color in enumerate(colors):
        if color:
            self.move_lifting_arm(lifting_arms[i], LiftingArmPosition.DROP, async_task=False)
        else:
            self.move_lifting_arm(lifting_arms[i], LiftingArmPosition.PRE_GRAB, async_task=False)

    self.move_elevator(elevator, ElevatorPosition.DROP, speed=0.5, async_task=False)
    sleep(2.6)

    # Drop good ones
    self.actuators.pumps_drop(ids = [lifting_arms_pumps[i] for i, color in enumerate(colors) if color])
    sleep(0.2)

    self.store_crates(side, async_task=False)

    self.forward(-160 * move_direction, avoid=True, async_task=False)

    return RobotStatus.return_status(RobotStatus.Done)


def _reverse_crates(self, side: str, colors: list[bool]) -> None:
    if side == "front":
        reversing_arms = [ReversingArmId.FRONT_RIGHT, ReversingArmId.FRONT_LEFT]
        reversing_heads = [ReversingHeadId.FRONT_RIGHT, ReversingHeadId.FRONT_LEFT]
        lifting_arms = [LiftingArmId.FRONT_1, LiftingArmId.FRONT_2, LiftingArmId.FRONT_3, LiftingArmId.FRONT_4]
        elevator = ElevatorId.FRONT
        reversing_arms_pumps = [0, 1]
        lifting_arms_pumps = [2, 3, 4, 5]
    elif side == "back":
        reversing_arms = [ReversingArmId.BACK_RIGHT, ReversingArmId.BACK_LEFT]
        reversing_heads = [ReversingHeadId.BACK_RIGHT, ReversingHeadId.BACK_LEFT]
        lifting_arms = [LiftingArmId.BACK_1, LiftingArmId.BACK_2, LiftingArmId.BACK_3, LiftingArmId.BACK_4]
        elevator = ElevatorId.BACK
        reversing_arms_pumps = [20, 21]
        lifting_arms_pumps = [22, 23, 24, 25]
    else:
        raise RuntimeError("Invalid side: %s" % side)

    left_crate_index = None
    right_crate_index = None
    if not colors[0]:
        right_crate_index = 0
    if not colors[3]:
        left_crate_index = 3
    if not colors[1] and right_crate_index is None:
        right_crate_index = 1
    if not colors[2] and left_crate_index is None:
        left_crate_index = 2
    if not colors[1] and left_crate_index is None:
        left_crate_index = 1
    if not colors[2] and right_crate_index is None:
        right_crate_index = 2

    # Logic to move reversing arm positions
    reversing_arm_positions = [
        ReversingArmPosition.CRATE1,
        ReversingArmPosition.CRATE2,
        ReversingArmPosition.CRATE3,
        ReversingArmPosition.CRATE4
    ]

    # Put reversing arms at right positions
    if right_crate_index is not None:
        self.move_reversing_arm(reversing_arms[0], reversing_arm_positions[right_crate_index], async_task=False)
    if left_crate_index is not None:
        self.move_reversing_arm(reversing_arms[1], reversing_arm_positions[left_crate_index], async_task=False)

    # Turn head of reversing arm upward
    if right_crate_index is not None:
        self.move_reversing_head(reversing_heads[0], ReversingHeadPosition.REVERSED, async_task=False)
    if left_crate_index is not None:
        self.move_reversing_head(reversing_heads[1], ReversingHeadPosition.REVERSED, async_task=False)

    sleep(0.6)

    # Enable reversing arm pumps
    if right_crate_index is not None:
        self.actuators.pumps_grab(ids = [reversing_arms_pumps[0]])
    if left_crate_index is not None:
        self.actuators.pumps_grab(ids = [reversing_arms_pumps[1]])

    # Stick lifting arms on reversing arms
    if right_crate_index is not None:
        self.move_lifting_arm(lifting_arms[right_crate_index], LiftingArmPosition.GRAB, async_task=False)
    if left_crate_index is not None:
        self.move_lifting_arm(lifting_arms[left_crate_index], LiftingArmPosition.GRAB, async_task=False)

    self.move_elevator(elevator, ElevatorPosition.REVERSE_DOWN, speed=0.5, async_task=False)
    sleep(0.7)

    # Disable lifting arm pumps
    if right_crate_index is not None:
        self.actuators.pumps_drop(ids = [lifting_arms_pumps[right_crate_index]])
    if left_crate_index is not None:
        self.actuators.pumps_drop(ids = [lifting_arms_pumps[left_crate_index]])

    sleep(0.1)

    # Detach lifting arms from reversing arms
    if right_crate_index is not None:
        self.move_lifting_arm(lifting_arms[right_crate_index], LiftingArmPosition.DROP, async_task=False)
    if left_crate_index is not None:
        self.move_lifting_arm(lifting_arms[left_crate_index], LiftingArmPosition.DROP, async_task=False)

    # Lift up lifting arms
    for arm in lifting_arms:
        self.move_lifting_arm(arm, LiftingArmPosition.REVERSE, async_task=False)

    self.move_elevator(elevator, ElevatorPosition.HIGHEST, async_task=False)
    sleep(1)

    # Put reversing arms at correct position to do reverse without collision
    if right_crate_index is not None:
        self.move_reversing_arm(reversing_arms[0], ReversingArmPosition.RIGHT_REVERSE, async_task=False)
    if left_crate_index is not None:
        self.move_reversing_arm(reversing_arms[1], ReversingArmPosition.LEFT_REVERSE, async_task=False)
    sleep(0.25)

    # Reverse
    if right_crate_index is not None:
        self.move_reversing_head(reversing_heads[0], ReversingHeadPosition.NORMAL, async_task=False)
        colors[right_crate_index] ^= True
    if left_crate_index is not None:
        self.move_reversing_head(reversing_heads[1], ReversingHeadPosition.NORMAL, async_task=False)
        colors[left_crate_index] ^= True
    sleep(0.55)

    # Disable reversing arm pumps (drop)
    if right_crate_index is not None:
        self.actuators.pumps_drop(ids = [reversing_arms_pumps[0]])
    if left_crate_index is not None:
        self.actuators.pumps_drop(ids = [reversing_arms_pumps[1]])

    sleep(0.1)

    # Reset lifting arm position
    for i in range(len(lifting_arms)):
        self.move_lifting_arm(lifting_arms[i], LiftingArmPosition.PRE_GRAB, async_task=False)


@if_enabled
@async_task
def reverse_bad_crates(self, side: str):
    if side == "front":
        lifting_arms = [LiftingArmId.FRONT_1, LiftingArmId.FRONT_2, LiftingArmId.FRONT_3, LiftingArmId.FRONT_4]
        elevator = ElevatorId.FRONT
        reversing_arm_high = ReversingArmHighId.FRONT
    elif side == "back":
        lifting_arms = [LiftingArmId.BACK_1, LiftingArmId.BACK_2, LiftingArmId.BACK_3, LiftingArmId.BACK_4]
        elevator = ElevatorId.BACK
        reversing_arm_high = ReversingArmHighId.BACK
    else:
        raise RuntimeError("Invalid side: %s" % side)

    # Read color sensors
    colors = []
    for arm in lifting_arms:
        colors.append(self.get_color(arm))

    if all(colors):
        return RobotStatus.return_status(RobotStatus.Done)

    for arm in lifting_arms:
        self.move_lifting_arm(arm, LiftingArmPosition.DROP, async_task=False)

    self.move_elevator(elevator, ElevatorPosition.REVERSE_UP, async_task=False)
    sleep(1.4)

    self.move_reversing_arm_high(reversing_arm_high, ReversingArmHighPosition.TOP, async_task=False)
    sleep(0.35)

    _reverse_crates(self, side, colors)

    return RobotStatus.return_status(RobotStatus.Done)


@if_enabled
@async_task
def reverse_and_drop_crates(self, side: str):
    if side == "front":
        reversing_arms = [ReversingArmId.FRONT_RIGHT, ReversingArmId.FRONT_LEFT]
        reversing_heads = [ReversingHeadId.FRONT_RIGHT, ReversingHeadId.FRONT_LEFT]
        lifting_arms = [LiftingArmId.FRONT_1, LiftingArmId.FRONT_2, LiftingArmId.FRONT_3, LiftingArmId.FRONT_4]
        elevator = ElevatorId.FRONT
        lifting_arms_pumps = [2, 3, 4, 5]
        move_direction = 1
        reversing_arm_high = ReversingArmHighId.FRONT
    elif side == "back":
        reversing_arms = [ReversingArmId.BACK_RIGHT, ReversingArmId.BACK_LEFT]
        reversing_heads = [ReversingHeadId.BACK_RIGHT, ReversingHeadId.BACK_LEFT]
        lifting_arms = [LiftingArmId.BACK_1, LiftingArmId.BACK_2, LiftingArmId.BACK_3, LiftingArmId.BACK_4]
        elevator = ElevatorId.BACK
        lifting_arms_pumps = [22, 23, 24, 25]
        move_direction = -1
        reversing_arm_high = ReversingArmHighId.BACK
    else:
        raise RuntimeError("Invalid side: %s" % side)

    colors = []
    for arm in lifting_arms:
        colors.append(self.get_color(arm))

    if all(colors):
        return self.drop_all_crates(side, async_task=False)

    for arm in lifting_arms:
        self.move_lifting_arm(arm, LiftingArmPosition.DROP, async_task=False)

    self.move_elevator(elevator, ElevatorPosition.REVERSE_UP, async_task=False)
    sleep(1.4)

    self.move_reversing_arm_high(reversing_arm_high, ReversingArmHighPosition.TOP, async_task=False)
    sleep(0.35)

    for _ in range(1):
        if all(colors): break

        _reverse_crates(self, side, colors)

        self.forward(-170 * move_direction, avoid=True, async_task=False)

    for i in range(2):
        self.move_reversing_head(reversing_heads[i], ReversingHeadPosition.NORMAL, async_task=False)
    sleep(0.5)

    for i in range(2):
        self.move_reversing_arm(reversing_arms[i], ReversingArmPosition.CLOSED, async_task=False)
    sleep(0.5)

    self.move_reversing_arm_high(reversing_arm_high, ReversingArmHighPosition.CLOSED, async_task=False)
    sleep(0.5)

    self.move_elevator(elevator, ElevatorPosition.DROP, speed=0.5, async_task=False)
    sleep(2.6)

    self.actuators.pumps_drop(ids = lifting_arms_pumps)
    sleep(0.2)

    for arm in lifting_arms:
        self.move_lifting_arm(arm, LiftingArmPosition.OPENED, async_task=False)
    sleep(0.5)

    self.forward(-160 * move_direction, avoid=True, async_task=False)

    return RobotStatus.return_status(RobotStatus.Done)
