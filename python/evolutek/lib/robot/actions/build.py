from evolutek.lib.robot.robot_actions_imports import *

from evolutek.lib.robot.robot_actuators import *


@if_enabled
@async_task
def grab_materials(self, side):
    if side == "front":
        side_arms = SideArmsId.FRONT
        plank_arms = PlankArmId.FRONT
        pumps_arm = PumpsArmId.FRONT
        pumps = PumpsSetId.FRONT
        magnets = MagnetsSetId.FRONT
        elevator = ElevatorId.FRONT
    else:
        side_arms = SideArmsId.BACK
        plank_arms = PlankArmId.BACK
        pumps_arm = PumpsArmId.BACK
        pumps = PumpsSetId.BACK
        magnets = MagnetsSetId.BACK
        elevator = ElevatorId.BACK

    if RobotStatus.get_status(self.move_plank_arm(plank_arms, PlankArmPosition.EXPANDED, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    if RobotStatus.get_status(self.move_elevator_ex(elevator, 0, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    if RobotStatus.get_status(self.toggle_magnets(magnets, MagnetState.ENABLE, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(1)

    if RobotStatus.get_status(self.toggle_pumps(pumps, True, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    if RobotStatus.get_status(self.forward(180 if side == "front" else -180, async_task=False)) != RobotStatus.Reached:
        return RobotStatus.return_status(RobotStatus.Failed)

    if RobotStatus.get_status(self.move_plank_arm(plank_arms, PlankArmPosition.LIFT, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.5)

    if RobotStatus.get_status(self.move_pumps_arm(pumps_arm, PumpsArmPosition.EXPANDED, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.5)

    return RobotStatus.return_status(RobotStatus.Done, score=0)


@if_enabled
@async_task
def place_materials(self, side):
    if side == "front":
        side_arms = SideArmsId.FRONT
        plank_arms = PlankArmId.FRONT
        pumps_arm = PumpsArmId.FRONT
        pumps = PumpsSetId.FRONT
        magnets = MagnetsSetId.FRONT
        elevator = ElevatorId.FRONT
    else:
        side_arms = SideArmsId.BACK
        plank_arms = PlankArmId.BACK
        pumps_arm = PumpsArmId.BACK
        pumps = PumpsSetId.BACK
        magnets = MagnetsSetId.BACK
        elevator = ElevatorId.BACK

    if RobotStatus.get_status(self.move_side_arms(side_arms, SideArmPosition.SPREADED, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.8)

    if RobotStatus.get_status(self.move_plank_arm(plank_arms, PlankArmPosition.EXPANDED, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    if RobotStatus.get_status(self.move_elevator_ex(elevator, 1, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(1.2)

    if RobotStatus.get_status(self.move_side_arms(side_arms, SideArmPosition.NORMAL, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.5)

    if RobotStatus.get_status(self.toggle_pumps(pumps, False, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.5)

    if RobotStatus.get_status(self.toggle_magnets(magnets, MagnetState.DISABLE, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.5)

    if RobotStatus.get_status(self.move_elevator_ex(elevator, 0.85, async_task=False)) != RobotStatus.Done:
       return RobotStatus.return_status(RobotStatus.Failed)

    if RobotStatus.get_status(self.move_pumps_arm(pumps_arm, PumpsArmPosition.ALMOST_EXPANDED, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.8)

    if RobotStatus.get_status(self.forward(-180 if side == "front" else 180, async_task=False)) != RobotStatus.Reached:
        return RobotStatus.return_status(RobotStatus.Failed)

    if RobotStatus.get_status(self.move_elevator_ex(elevator, 0, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    if RobotStatus.get_status(self.move_plank_arm(plank_arms, PlankArmPosition.COLLAPSED, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.5)

    if RobotStatus.get_status(self.move_pumps_arm(pumps_arm, PumpsArmPosition.COLLAPSED, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    return RobotStatus.return_status(RobotStatus.Done, score=12)
