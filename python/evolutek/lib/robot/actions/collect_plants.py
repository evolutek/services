from evolutek.lib.robot.robot_actions_imports import *

"""
from evolutek.lib.robot.robot_actuators import ElevatorPosition, ClampsPosition

@if_enabled
@async_task
def prepare_solar_panel(self, id):
    id = int(id)

    if RobotStatus.get_status(self.move_claw(id, ClawPositions.CLOSE, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)
    if RobotStatus.get_status(self.move_arm(id, ArmPositions.SOLAR_PANEL, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.5)

    return RobotStatus.return_status(RobotStatus.Done, score=0)


@if_enabled
@async_task
def prepare_grab_all(self):

    if RobotStatus.get_status(self.move_claw(1, ClawPositions.OPEN, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)
    if RobotStatus.get_status(self.move_arm(1, ArmPositions.LOW, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)
    if RobotStatus.get_status(self.move_claw(2, ClawPositions.OPEN, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)
    if RobotStatus.get_status(self.move_arm(2, ArmPositions.LOW, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)
    if RobotStatus.get_status(self.move_claw(3, ClawPositions.OPEN, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)
    if RobotStatus.get_status(self.move_arm(3, ArmPositions.LOW, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.5)

    return RobotStatus.return_status(RobotStatus.Done, score=0)



@if_enabled
@async_task
def prepare_grab(self, id):
    id = int(id)

    if RobotStatus.get_status(self.move_claw(id, ClawPositions.OPEN, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)
    if RobotStatus.get_status(self.move_arm(id, ArmPositions.LOW, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.5)

    return RobotStatus.return_status(RobotStatus.Done, score=0)


@if_enabled
@async_task
def grab(self, id):
    id = int(id)

    if RobotStatus.get_status(self.move_claw(id, ClawPositions.CLOSE, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(1)

    if RobotStatus.get_status(self.move_arm(id, ArmPositions.HIGH, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    return RobotStatus.return_status(RobotStatus.Done, score=0)


@if_enabled
@async_task
def drop(self, id):
    id = int(id)

    if RobotStatus.get_status(self.move_arm(id, ArmPositions.DROP_OFF, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.5)

    if RobotStatus.get_status(self.move_claw(id, ClawPositions.RELEASE, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(1)

    if RobotStatus.get_status(self.move_claw(id, ClawPositions.OPEN, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)
    """
    if RobotStatus.get_status(self.move_arm(id, ArmPositions.HIGH, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.5)

    if RobotStatus.get_status(self.move_claw(id, ClawPositions.CLOSE, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)
    """ # fait tomber les plantes au bords des jardinières en levant le bras

    return RobotStatus.return_status(RobotStatus.Done, score=0)


"""
@if_enabled
@async_task
def grab_plants(self):
    if RobotStatus.get_status(self.move_clamps([0, 1, 2], ClampsPosition.OPEN, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    if RobotStatus.get_status(self.move_elevator(ElevatorPosition.LOW, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.5)

    if RobotStatus.get_status(self.move_clamps([0, 1, 2], ClampsPosition.CLOSE, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.3)

    if RobotStatus.get_status(self.move_elevator(ElevatorPosition.HIGH, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.5)

    return RobotStatus.return_status(RobotStatus.Done, score=0)


@if_enabled
@async_task
def place_plants(self, n=-1):
    if RobotStatus.get_status(self.move_elevator(ElevatorPosition.LOW, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.5)

    if RobotStatus.get_status(self.move_clamps([0, 1, 2], ClampsPosition.OPEN, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.3)

    if RobotStatus.get_status(self.move_elevator(ElevatorPosition.HIGH, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.5)

    return RobotStatus.return_status(RobotStatus.Done, score=0)
"""
