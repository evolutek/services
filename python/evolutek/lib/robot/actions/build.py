from evolutek.lib.robot.robot_actions_imports import *

from evolutek.lib.robot.robot_actuators import *


@if_enabled
@async_task
def grab_materials(self):
    if RobotStatus.get_status(self.move_plank_arm(PlankArmId.FRONT, PlankArmPosition.EXPANDED, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    if RobotStatus.get_status(self.move_elevator_ex(ElevatorId.FRONT, 0.12, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    if RobotStatus.get_status(self.toggle_magnets(MagnetsSetId.FRONT, MagnetState.ENABLE, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(1)

    if RobotStatus.get_status(self.toggle_pumps(PumpsSetId.FRONT, True, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    if RobotStatus.get_status(self.forward(180, async_task=False)) != RobotStatus.Reached:
        return RobotStatus.return_status(RobotStatus.Failed)

    if RobotStatus.get_status(self.move_plank_arm(PlankArmId.FRONT, PlankArmPosition.LIFT, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.5)

    if RobotStatus.get_status(self.move_pumps_arm(PumpsArmId.FRONT, PumpsArmPosition.EXPANDED, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.5)

    return RobotStatus.return_status(RobotStatus.Done, score=0)


@if_enabled
@async_task
def place_materials(self):
    if RobotStatus.get_status(self.move_side_arms(SideArmsId.FRONT, SideArmPosition.SPREADED, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.8)

    if RobotStatus.get_status(self.move_plank_arm(PlankArmId.FRONT, PlankArmPosition.EXPANDED, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    if RobotStatus.get_status(self.move_elevator_ex(ElevatorId.FRONT, 1, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(1.2)

    if RobotStatus.get_status(self.move_side_arms(SideArmsId.FRONT, SideArmPosition.NORMAL, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.5)

    if RobotStatus.get_status(self.toggle_pumps(PumpsSetId.FRONT, False, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.5)

    if RobotStatus.get_status(self.toggle_magnets(MagnetsSetId.FRONT, MagnetState.DISABLE, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.5)

    if RobotStatus.get_status(self.move_elevator_ex(ElevatorId.FRONT, 0.9, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    if RobotStatus.get_status(self.move_pumps_arm(PumpsArmId.FRONT, PumpsArmPosition.ALMOST_EXPANDED, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.5)

    if RobotStatus.get_status(self.forward(-180, async_task=False)) != RobotStatus.Reached:
        return RobotStatus.return_status(RobotStatus.Failed)

    if RobotStatus.get_status(self.move_elevator_ex(ElevatorId.FRONT, 0, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    if RobotStatus.get_status(self.move_plank_arm(PlankArmId.FRONT, PlankArmPosition.COLLAPSED, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.5)

    if RobotStatus.get_status(self.move_pumps_arm(PumpsArmId.FRONT, PumpsArmPosition.COLLAPSED, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    return RobotStatus.return_status(RobotStatus.Done, score=12)
