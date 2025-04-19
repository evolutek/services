from evolutek.lib.robot.robot_actions_imports import *

from evolutek.lib.robot.robot_actuators import *


@if_enabled
@async_task
def grab_materials(self):
    if RobotStatus.get_status(self.move_plank_arm(PlankArmId.FRONT, PlankArmPosition.EXPANDED, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    if RobotStatus.get_status(self.move_elevator_ex(ElevatorId.FRONT, 0.12, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    if RobotStatus.get_status(self.toggle_magnets(MagnetsSet.FRONT_MAGNETS, MagnetState.ENABLE, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(1)

    if RobotStatus.get_status(self.toggle_pumps(PumpsSet.FRONT_PLANK, True, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    if RobotStatus.get_status(self.forward(150, async_task=False)) != RobotStatus.Reached:
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
def drop_materials(self):
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

    if RobotStatus.get_status(self.toggle_pumps(PumpsSet.FRONT_PLANK, False, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.5)

    if RobotStatus.get_status(self.toggle_magnets(MagnetsSet.FRONT_MAGNETS, MagnetState.DISABLE, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.5)

    if RobotStatus.get_status(self.move_elevator_ex(ElevatorId.FRONT, 0.9, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    if RobotStatus.get_status(self.move_pumps_arm(PumpsArmId.FRONT, PumpsArmPosition.ALMOST_EXPANDED, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.5)

    if RobotStatus.get_status(self.forward(-150, async_task=False)) != RobotStatus.Reached:
        return RobotStatus.return_status(RobotStatus.Failed)

    if RobotStatus.get_status(self.move_elevator_ex(ElevatorId.FRONT, 0, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    if RobotStatus.get_status(self.move_plank_arm(PlankArmId.FRONT, PlankArmPosition.COLLAPSED, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.5)

    if RobotStatus.get_status(self.move_pumps_arm(PumpsArmId.FRONT, PumpsArmPosition.COLLAPSED, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    return RobotStatus.return_status(RobotStatus.Done, score=12)



"""
@if_enabled
@async_task
def spread_side_cans(self):
    r = self.move_rot(dest=2*pi, acc=5, dec=5, maxspeed=15, sens=1)
    return RobotStatus.return_status(RobotStatus.get_status(r))


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

    if RobotStatus.get_status(self.move_clamps([0, 1, 2], ClampsPosition.CLOSE, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.2)

    return RobotStatus.return_status(RobotStatus.Done, score=0)


@if_enabled
@async_task
def lift_plants(self):
    if RobotStatus.get_status(self.move_elevator(ElevatorPosition.HIGH, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    #if RobotStatus.get_status(self.move_rack(RackPosition.FOLDED, async_task=False)) != RobotStatus.Done:
    #    return RobotStatus.return_status(RobotStatus.Failed)

    #sleep(0.5)

    return RobotStatus.return_status(RobotStatus.Done, score=0)

@if_enabled
@async_task
def count_plants_in_pots(self):
    score = 0
    sensors = [0, 1, 2]
    for i in sensors:
        if self.actuators.proximity_sensor_read(id=i):
            score += 4

    return RobotStatus.return_status(RobotStatus.Done, score=score)

@if_enabled
@async_task
def place_plants(self):
    if RobotStatus.get_status(self.move_elevator(ElevatorPosition.LOW, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    if RobotStatus.get_status(self.move_clamps([0, 1, 2], ClampsPosition.OPEN, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.2)

    if RobotStatus.get_status(self.move_elevator(ElevatorPosition.HIGH, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    return RobotStatus.return_status(RobotStatus.Done, score=0)


@if_enabled
@async_task
def place_plants_in_planter(self):
    if RobotStatus.get_status(self.move_rack(RackPosition.UNFOLDED, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.4)

    if RobotStatus.get_status(self.move_elevator(ElevatorPosition.BORDER, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    if RobotStatus.get_status(self.move_clamps([0, 1, 2], ClampsPosition.OPEN, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.2)

    if RobotStatus.get_status(self.move_elevator(ElevatorPosition.HIGH, wait=False, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.2)

    if RobotStatus.get_status(self.move_rack(RackPosition.FOLDED, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.4)

    return RobotStatus.return_status(RobotStatus.Done, score=0)


@if_enabled
@async_task
def place_plants_in_pots(self):
    if RobotStatus.get_status(self.move_rack(RackPosition.POTS, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.4)

    if RobotStatus.get_status(self.move_elevator(ElevatorPosition.POTS, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    if RobotStatus.get_status(self.move_clamps([0, 1, 2], ClampsPosition.OPEN, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.2)

    if RobotStatus.get_status(self.move_elevator(ElevatorPosition.HIGH, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    if RobotStatus.get_status(self.move_rack(RackPosition.FOLDED, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.4)

    return RobotStatus.return_status(RobotStatus.Done, score=0)


@if_enabled
@async_task
def place_plants_in_pots_and_grab_plants(self):
    if RobotStatus.get_status(self.move_rack(RackPosition.POTS, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.2)

    if RobotStatus.get_status(self.move_elevator(ElevatorPosition.POTS, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    if RobotStatus.get_status(self.move_clamps([0, 1, 2], ClampsPosition.OPEN, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.15)

    if RobotStatus.get_status(self.move_elevator(ElevatorPosition.HIGH, wait = False, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.15)

    if RobotStatus.get_status(self.move_rack(RackPosition.FOLDED, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    if RobotStatus.get_status(self.forward(-80, async_task=False)) != RobotStatus.Reached:
        return RobotStatus.return_status(RobotStatus.Failed)

    if RobotStatus.get_status(self.move_herse(HersePosition.MIDDLE, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    if RobotStatus.get_status(self.move_herse(HersePosition.UP, wait = False, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    if RobotStatus.get_status(self.move_elevator(ElevatorPosition.LOW, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    if RobotStatus.get_status(self.move_clamps([0, 1, 2], ClampsPosition.CLOSE, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.15)

    return RobotStatus.return_status(RobotStatus.Done, score=0)
"""
