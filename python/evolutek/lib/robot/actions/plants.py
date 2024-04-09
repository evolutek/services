from evolutek.lib.robot.robot_actions_imports import *

from evolutek.lib.robot.robot_actuators import ElevatorPosition, ClampsPosition, RackPosition


@if_enabled
@async_task
def grab_plants(self):
    #if RobotStatus.get_status(self.move_rack(RackPosition.PLANTS, async_task=False)) != RobotStatus.Done:
    #    return RobotStatus.return_status(RobotStatus.Failed)

    #sleep(0.5)

    if RobotStatus.get_status(self.move_clamps([0, 1, 2], ClampsPosition.OPEN, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    if RobotStatus.get_status(self.move_elevator(ElevatorPosition.LOW, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(1)

    if RobotStatus.get_status(self.move_clamps([0, 1, 2], ClampsPosition.CLOSE, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.3)

    return RobotStatus.return_status(RobotStatus.Done, score=0)


@if_enabled
@async_task
def lift_plants(self):
    if RobotStatus.get_status(self.move_elevator(ElevatorPosition.HIGH, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.7)

    #if RobotStatus.get_status(self.move_rack(RackPosition.FOLDED, async_task=False)) != RobotStatus.Done:
    #    return RobotStatus.return_status(RobotStatus.Failed)

    #sleep(0.5)

    return RobotStatus.return_status(RobotStatus.Done, score=0)


@if_enabled
@async_task
def place_plants(self):
    if RobotStatus.get_status(self.move_elevator(ElevatorPosition.LOW, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(1)

    if RobotStatus.get_status(self.move_clamps([0, 1, 2], ClampsPosition.OPEN, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.3)

    if RobotStatus.get_status(self.move_elevator(ElevatorPosition.HIGH, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.7)

    return RobotStatus.return_status(RobotStatus.Done, score=0)


@if_enabled
@async_task
def place_plants_in_planter(self):
    if RobotStatus.get_status(self.move_rack(RackPosition.UNFOLDED, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.5)

    if RobotStatus.get_status(self.move_elevator(ElevatorPosition.BORDER, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.9)

    if RobotStatus.get_status(self.move_clamps([0, 1, 2], ClampsPosition.OPEN, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.3)

    if RobotStatus.get_status(self.move_elevator(ElevatorPosition.HIGH, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.7)

    if RobotStatus.get_status(self.move_rack(RackPosition.FOLDED, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.5)

    return RobotStatus.return_status(RobotStatus.Done, score=0)


@if_enabled
@async_task
def place_plants_in_pots(self):
    if RobotStatus.get_status(self.move_rack(RackPosition.POTS, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.5)

    if RobotStatus.get_status(self.move_elevator(ElevatorPosition.POTS, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.9)

    if RobotStatus.get_status(self.move_clamps([0, 1, 2], ClampsPosition.OPEN, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.3)

    if RobotStatus.get_status(self.move_elevator(ElevatorPosition.HIGH, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.7)

    if RobotStatus.get_status(self.move_rack(RackPosition.FOLDED, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.5)

    return RobotStatus.return_status(RobotStatus.Done, score=0)
