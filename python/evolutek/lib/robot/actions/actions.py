from evolutek.lib.robot.actions.actions import *
from evolutek.lib.robot.robot_actuators import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from evolutek.services.robot import Robot


@if_enabled
@async_task
def grab_crates(self, side: str):
    if side == "front":
        compacting_arms = [CompactingArmId.FRONT_LEFT, CompactingArmId.FRONT_RIGHT]
        reversing_arms = [ReversingArmId.FRONT_LEFT, ReversingArmId.FRONT_RIGHT]
        color_sensors = [1, 2, 3, 4]
    else:
        raise RuntimeError("Invalid side: %s" % side)

    self.move_compacting_arm(CompactingArmId.FRONT_RIGHT, CompactingArmPosition.OPENED, async_task=False)
    self.move_compacting_arm(CompactingArmId.FRONT_LEFT, CompactingArmPosition.OPENED, async_task=False)
    sleep(0.75)

    self.forward(130, avoid=True, async_task=False)

    self.move_compacting_arm(CompactingArmId.FRONT_RIGHT, CompactingArmPosition.TASSED, async_task=False)
    self.move_compacting_arm(CompactingArmId.FRONT_LEFT, CompactingArmPosition.TASSED, async_task=False)
    sleep(1.5)

    self.move_elevator(ElevatorId.FRONT, ElevatorPosition.LOWEST, async_task=False)
    sleep(1)

    self.move_lifting_arm(LiftingArmId.FRONT_1, LiftingArmPosition.GRAB, async_task=False)
    self.move_lifting_arm(LiftingArmId.FRONT_2, LiftingArmPosition.GRAB, async_task=False)
    self.move_lifting_arm(LiftingArmId.FRONT_3, LiftingArmPosition.GRAB, async_task=False)
    self.move_lifting_arm(LiftingArmId.FRONT_4, LiftingArmPosition.GRAB, async_task=False)
    sleep(1)

    self.actuators.pumps_grab(ids = [2, 3, 4, 5])
    sleep(0.2)

    self.move_compacting_arm(CompactingArmId.FRONT_RIGHT, CompactingArmPosition.OPENED, async_task=False)
    self.move_compacting_arm(CompactingArmId.FRONT_LEFT, CompactingArmPosition.OPENED, async_task=False)
    sleep(0.5)

    self.move_lifting_arm(LiftingArmId.FRONT_1, LiftingArmPosition.OPENED, async_task=False)
    self.move_lifting_arm(LiftingArmId.FRONT_2, LiftingArmPosition.OPENED, async_task=False)
    self.move_lifting_arm(LiftingArmId.FRONT_3, LiftingArmPosition.OPENED, async_task=False)
    self.move_lifting_arm(LiftingArmId.FRONT_4, LiftingArmPosition.OPENED, async_task=False)
    sleep(1)

    self.move_compacting_arm(CompactingArmId.FRONT_RIGHT, CompactingArmPosition.CLOSED, async_task=False)
    self.move_compacting_arm(CompactingArmId.FRONT_LEFT, CompactingArmPosition.CLOSED, async_task=False)
    sleep(0.5)

    """
    if RobotStatus.get_status(self.toggle_pumps(pumps, True, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    if RobotStatus.get_status(self.forward(180 if side == "front" else -180, async_task=False)) != RobotStatus.Reached:
        return RobotStatus.return_status(RobotStatus.Failed)

    if RobotStatus.get_status(self.move_plank_arm(plank_arms, PlankArmPosition.LIFT, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    if RobotStatus.get_status(self.move_pumps_arm(pumps_arm, PumpsArmPosition.EXPANDED, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.2)
    """

    return RobotStatus.return_status(RobotStatus.Done, score=0)


@if_enabled
@async_task
def drop_crates(self, side: str):
    if side == "front":
        compacting_arms = [CompactingArmId.FRONT_LEFT, CompactingArmId.FRONT_RIGHT]
        reversing_arms = [ReversingArmId.FRONT_LEFT, ReversingArmId.FRONT_RIGHT]
        color_sensors = [1, 2, 3, 4]
    else:
        raise RuntimeError("Invalid side: %s" % side)

    self.move_lifting_arm(LiftingArmId.FRONT_1, LiftingArmPosition.DROP, async_task=False)
    self.move_lifting_arm(LiftingArmId.FRONT_2, LiftingArmPosition.DROP, async_task=False)
    self.move_lifting_arm(LiftingArmId.FRONT_3, LiftingArmPosition.DROP, async_task=False)
    self.move_lifting_arm(LiftingArmId.FRONT_4, LiftingArmPosition.DROP, async_task=False)
    sleep(0.5)

    self.actuators.pumps_drop(ids = [2, 3, 4, 5])
    sleep(0.2)

    self.move_lifting_arm(LiftingArmId.FRONT_1, LiftingArmPosition.OPENED, async_task=False)
    self.move_lifting_arm(LiftingArmId.FRONT_2, LiftingArmPosition.OPENED, async_task=False)
    self.move_lifting_arm(LiftingArmId.FRONT_3, LiftingArmPosition.OPENED, async_task=False)
    self.move_lifting_arm(LiftingArmId.FRONT_4, LiftingArmPosition.OPENED, async_task=False)
    sleep(0.5)

    self.forward(-130, avoid=True, async_task=False)

    return RobotStatus.return_status(RobotStatus.Done)


@if_enabled
@async_task
def do_cursor(self):
    arm = CursorArmSide.LEFT if self.side else CursorArmSide.RIGHT

    self.move_cursor_arm(arm, CursorArmPosition.DEPLOYED, async_task=False)
    sleep(0.5)
    self.goto_avoid(1790, 710, async_task=False)
    self.move_cursor_arm(arm, CursorArmPosition.CLOSED, async_task=False)
    sleep(0.5)

    return RobotStatus.return_status(RobotStatus.Done)


@if_enabled
@async_task
def drop_and_sort_crates(self, side: str):
    if side == "front":
        reversing_arms = [ReversingArmId.FRONT_RIGHT, ReversingArmId.FRONT_LEFT]
        reversing_heads = [ReversingHeadId.FRONT_RIGHT, ReversingHeadId.FRONT_LEFT]
        lifting_arms = [LiftingArmId.FRONT_1, LiftingArmId.FRONT_2, LiftingArmId.FRONT_3, LiftingArmId.FRONT_4]
        elevator = ElevatorId.FRONT
        reversing_arms_pumps = [0, 1]
        lifting_arms_pumps = [2, 3, 4, 5]
    else:
        raise RuntimeError("Invalid side: %s" % side)

    colors = []

    # Read color sensors
    for arm in lifting_arms:
        colors.append(self.get_color(arm))

    is_all_right = all(colors)
    if is_all_right:
        return self.drop_crates(side, async_task=False)

    # Prepare to reverse

    for arm in lifting_arms:
        self.move_lifting_arm(arm, LiftingArmPosition.DROP, async_task=False)
    sleep(0.5)

    self.move_elevator(elevator, ElevatorPosition.REVERSE)
    sleep(1.5)

    self.move_reversing_arm_high(ReversingArmHighPosition.TOP)
    sleep(0.5)

    # Start reversing colors

    reversing_arm_positions = [
        ReversingArmPosition.CRATE1,
        ReversingArmPosition.CRATE2,
        ReversingArmPosition.CRATE3,
        ReversingArmPosition.CRATE4
    ]

    for _ in range(2): # Max 3 iterations
        # (right lifting arm crate pos, left lifting arm crate pos)
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

        # Put reversing arms at right positions
        # reversing_arms[0] is the right, reversing_arms[1] is the left
        if right_crate_index is not None:
            self.move_reversing_arm(reversing_arms[0], reversing_arm_positions[right_crate_index], async_task=False)
        if left_crate_index is not None:
            self.move_reversing_arm(reversing_arms[1], reversing_arm_positions[left_crate_index], async_task=False)
        sleep(0.5)

        # Stick lifting arms on reversing arms
        if right_crate_index is not None:
            self.move_lifting_arm(lifting_arms[right_crate_index], LiftingArmPosition.GRAB, async_task=False)
        if left_crate_index is not None:
            self.move_lifting_arm(lifting_arms[left_crate_index], LiftingArmPosition.GRAB, async_task=False)
        sleep(0.5)

        # Enable reversing arm pumps
        if right_crate_index is not None:
            self.actuators.pumps_grab(ids = [reversing_arms_pumps[0]])
        if left_crate_index is not None:
            self.actuators.pumps_grab(ids = [reversing_arms_pumps[1]])
        sleep(0.2)

        # Disable lifting arm pumps
        if right_crate_index is not None:
            self.actuators.pumps_drop(ids = [lifting_arms_pumps[right_crate_index]])
        if left_crate_index is not None:
            self.actuators.pumps_drop(ids = [lifting_arms_pumps[left_crate_index]])
        sleep(0.2)

        # Detach lifting arms from reversing arms
        if right_crate_index is not None:
            self.move_lifting_arm(lifting_arms[right_crate_index], LiftingArmPosition.DROP, async_task=False)
        if left_crate_index is not None:
            self.move_lifting_arm(lifting_arms[left_crate_index], LiftingArmPosition.DROP, async_task=False)
        sleep(0.5)

        # Reverse
        if right_crate_index is not None:
            self.move_reversing_head(reversing_heads[0], ReversingHeadPosition.REVERSED, async_task=False)
            colors[right_crate_index] = True # Reversed to the right color
        if left_crate_index is not None:
            self.move_reversing_head(reversing_heads[1], ReversingHeadPosition.REVERSED, async_task=False)
            colors[left_crate_index] = True # Reversed to the right color
        sleep(1)

        # Put reversing arms at at position 2 and 3 (there natural position)
        if right_crate_index is not None:
            self.move_reversing_arm(reversing_arms[0], ReversingArmPosition.CRATE2, async_task=False)
        if left_crate_index is not None:
            pass # TO TEST BEFORE #self.move_reversing_arm(reversing_arms[1], ReversingArmPosition.CRATE3, async_task=False)
        sleep(1)

        # Disable reversing arm pumps (drop)
        if right_crate_index is not None:
            self.actuators.pumps_drop(ids = [reversing_arms_pumps[0]])
        if left_crate_index is not None:
            self.actuators.pumps_drop(ids = [reversing_arms_pumps[1]])
        sleep(0.2)

        # Put reversing head in normal position
        if right_crate_index is not None:
            self.move_reversing_head(reversing_heads[0], ReversingHeadPosition.NORMAL, async_task=False)
        if left_crate_index is not None:
            self.move_reversing_head(reversing_heads[1], ReversingHeadPosition.NORMAL, async_task=False)
        sleep(0.5)

        # Go back to drop the rest
        self.forward(-160, avoid=True, async_task=False)

    # Drop the rest
    for i in range(2):
        self.move_reversing_arm(reversing_arms[i], ReversingArmPosition.CLOSED, async_task=False)
    sleep(0.5)

    self.move_reversing_arm_high(ReversingArmHighPosition.CLOSED)
    sleep(0.5)

    self.move_elevator(elevator, ElevatorPosition.LOWEST)
    sleep(1.5)

    # Drop the rest
    self.actuators.pumps_drop(ids = [2, 3, 4, 5])
    sleep(0.2)

    # Lift up arms
    for i in range(4):
        self.move_lifting_arm(lifting_arms[i], LiftingArmPosition.OPENED, async_task=False)
    sleep(0.5)

    self.forward(-160, avoid=True, async_task=False)

    return RobotStatus.return_status(RobotStatus.Done)
