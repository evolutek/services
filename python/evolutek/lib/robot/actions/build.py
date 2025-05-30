from evolutek.lib.robot.robot_actions_imports import *
from evolutek.lib.robot.robot_actuators import *

import math


FRONT_PROXIMITY_SENSORS = [0, 1, 2, 3]
BACK_PROXIMITY_SENSORS = [5, 6, 7, 8]


@async_task
def detect_materials(self, side):
    has_all_materials = True
    for i in FRONT_PROXIMITY_SENSORS:
        if not self.actuators.proximity_sensor_read(i):
            has_all_materials = False
            break

    #if not has_all_materials:
    #    self.environment[""]


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
def separate_and_place_first_layer(self, side):
    if side == "front":
        side_arms = SideArmsId.FRONT
        plank_arms = PlankArmId.FRONT
        pilar_arms = PilarArmId.FRONT
        pumps_arm = PumpsArmId.FRONT
        pumps = PumpsSetId.FRONT
        magnets = MagnetsSetId.FRONT
        elevator = ElevatorId.FRONT
    else:
        side_arms = SideArmsId.BACK
        plank_arms = PlankArmId.BACK
        pilar_arms = PilarArmId.BACK
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

    return RobotStatus.return_status(RobotStatus.Done)


@if_enabled
@async_task
def move_back_after_first_layer_build(self, side):
    if side == "front":
        side_arms = SideArmsId.FRONT
        plank_arms = PlankArmId.FRONT
        pilar_arms = PilarArmId.FRONT
        pumps_arm = PumpsArmId.FRONT
        pumps = PumpsSetId.FRONT
        magnets = MagnetsSetId.FRONT
        elevator = ElevatorId.FRONT
    else:
        side_arms = SideArmsId.BACK
        plank_arms = PlankArmId.BACK
        pilar_arms = PilarArmId.BACK
        pumps_arm = PumpsArmId.BACK
        pumps = PumpsSetId.BACK
        magnets = MagnetsSetId.BACK
        elevator = ElevatorId.BACK

    if RobotStatus.get_status(self.forward(-180 if side == "front" else 180, async_task=False)) != RobotStatus.Reached:
        return RobotStatus.return_status(RobotStatus.Failed)

    if RobotStatus.get_status(self.move_elevator_ex(elevator, 0, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    if RobotStatus.get_status(self.move_plank_arm(plank_arms, PlankArmPosition.COLLAPSED, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.5)

    if RobotStatus.get_status(self.move_pumps_arm(pumps_arm, PumpsArmPosition.COLLAPSED, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)


@if_enabled
@async_task
def place_second_layer(self, side):
    if side == "front":
        side_arms = SideArmsId.FRONT
        plank_arms = PlankArmId.FRONT
        pilar_arms = PilarArmId.FRONT
        pumps_arm = PumpsArmId.FRONT
        pumps = PumpsSetId.FRONT
        magnets = MagnetsSetId.FRONT
        elevator = ElevatorId.FRONT
    else:
        side_arms = SideArmsId.BACK
        plank_arms = PlankArmId.BACK
        pilar_arms = PilarArmId.BACK
        pumps_arm = PumpsArmId.BACK
        pumps = PumpsSetId.BACK
        magnets = MagnetsSetId.BACK
        elevator = ElevatorId.BACK

    if RobotStatus.get_status(self.toggle_pumps(pumps, False, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.5)

    if RobotStatus.get_status(self.toggle_magnets(magnets, MagnetState.DISABLE, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

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

    return RobotStatus.return_status(RobotStatus.Done)


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

    sleep(1.4)

    if RobotStatus.get_status(self.move_side_arms(side_arms, SideArmPosition.NORMAL, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.5)

    if RobotStatus.get_status(self.toggle_pumps(pumps, False, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.5)

    if RobotStatus.get_status(self.toggle_magnets(magnets, MagnetState.DISABLE, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

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


def dbg():
    input("...")


@if_enabled
@async_task
def prepare_second_layer(self, side):
    if side == "front":
        side_arms = SideArmsId.FRONT
        plank_arms = PlankArmId.FRONT
        pilar_arms = PilarArmId.FRONT
        pumps_arm = PumpsArmId.FRONT
        pumps = PumpsSetId.FRONT
        magnets = MagnetsSetId.FRONT
        inner_magnets = MagnetsSetId.FRONT_INTERIOR
        outer_magnets = MagnetsSetId.FRONT_EXTERIOR
        elevator = ElevatorId.FRONT
    elif side == "back":
        side_arms = SideArmsId.BACK
        plank_arms = PlankArmId.BACK
        pilar_arms = PilarArmId.BACK
        pumps_arm = PumpsArmId.BACK
        pumps = PumpsSetId.BACK
        magnets = MagnetsSetId.BACK
        inner_magnets = MagnetsSetId.BACK_INTERIOR
        outer_magnets = MagnetsSetId.BACK_EXTERIOR
        elevator = ElevatorId.BACK
    else:
        raise Exception(f"Bad side '{side}'")

    # Move pilar aside, lift them up and place them on top of layer 1

    #dbg()
    if RobotStatus.get_status(self.move_side_arms(side_arms, SideArmPosition.SPREADED, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.5)

    #dbg()
    if RobotStatus.get_status(self.move_elevator_ex(elevator, 1, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(1.2) # Wait for the elevator

    #dbg()
    if RobotStatus.get_status(self.move_side_arms(side_arms, SideArmPosition.NORMAL, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.5)

    return RobotStatus.return_status(RobotStatus.Done)


@if_enabled
@async_task
def build_3_layers(self, side):
    if side == "front":
        side_arms = SideArmsId.FRONT
        plank_arms = PlankArmId.FRONT
        pilar_arms = PilarArmId.FRONT
        pumps_arm = PumpsArmId.FRONT
        pumps = PumpsSetId.FRONT
        magnets = MagnetsSetId.FRONT
        inner_magnets = MagnetsSetId.FRONT_INTERIOR
        outer_magnets = MagnetsSetId.FRONT_EXTERIOR
        elevator = ElevatorId.FRONT
    elif side == "back":
        side_arms = SideArmsId.BACK
        plank_arms = PlankArmId.BACK
        pilar_arms = PilarArmId.BACK
        pumps_arm = PumpsArmId.BACK
        pumps = PumpsSetId.BACK
        magnets = MagnetsSetId.BACK
        inner_magnets = MagnetsSetId.BACK_INTERIOR
        outer_magnets = MagnetsSetId.BACK_EXTERIOR
        elevator = ElevatorId.BACK
    else:
        raise Exception(f"Bad side '{side}'")

    # Spread the two center pilar

    dbg()
    if RobotStatus.get_status(self.toggle_magnets(magnets, MagnetState.DISABLE, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    dbg()
    if RobotStatus.get_status(self.move_elevator_ex(elevator, 0.85, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.5)

    dbg()
    if RobotStatus.get_status(self.toggle_pumps(pumps, False, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.2)

    dbg()
    if RobotStatus.get_status(self.move_pilar_arm(pilar_arms, PilarArmPosition.SPREADED, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.2)

    dbg()
    if RobotStatus.get_status(self.move_plank_arm(plank_arms, PlankArmPosition.EXPANDED, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.2)

    dbg()
    if RobotStatus.get_status(self.move_pilar_arm(pilar_arms, PilarArmPosition.COLLAPSED, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    # Prepare the elevator to go down

    dbg()
    if RobotStatus.get_status(self.move_pumps_arm(pumps_arm, PumpsArmPosition.COLLAPSED, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.5)

    # Elevator going down and slightly going back

    dbg()
    if RobotStatus.get_status(self.forward(-20 if side == "front" else 20, async_task=False)) != RobotStatus.Reached:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.2)

    dbg()
    if RobotStatus.get_status(self.move_side_arms(side_arms, SideArmPosition.SPREADED, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    dbg()
    if RobotStatus.get_status(self.move_elevator_ex(elevator, 0, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(2)

    # Prepare to grab lower layer of the two ones

    dbg()
    if RobotStatus.get_status(self.move_side_arms(side_arms, SideArmPosition.NORMAL, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    dbg()
    if RobotStatus.get_status(self.move_pumps_arm(pumps_arm, PumpsArmPosition.ALMOST_EXPANDED, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.5)

    dbg()
    if RobotStatus.get_status(self.toggle_magnets(outer_magnets, MagnetState.ENABLE, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    dbg()
    if RobotStatus.get_status(self.forward(40 if side == "front" else -40)) != RobotStatus.Reached:
        return RobotStatus.return_status(RobotStatus.Failed)

    # Grab the lower layer of the two ones

    dbg()
    if RobotStatus.get_status(self.move_pumps_arm(pumps_arm, PumpsArmPosition.OVER_EXPANDED, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    dbg()
    if RobotStatus.get_status(self.toggle_pumps(pumps, True, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.5)

    if RobotStatus.get_status(self.move_pumps_arm(pumps_arm, PumpsArmPosition.EXPANDED, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.2)

    dbg()
    if RobotStatus.get_status(self.move_elevator_ex(elevator, 1, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(1)

    dbg()
    if RobotStatus.get_status(self.move_trsl(dest=140, acc=200, dec=200, maxspeed=500, sens=(1 if side == "front" else 0))) != RobotStatus.Reached:
        return RobotStatus.return_status(RobotStatus.Failed)

    # Drop the layer 2 & 3 on top of layer 1

    dbg()
    if RobotStatus.get_status(self.toggle_magnets(magnets, MagnetState.DISABLE, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    dbg()
    if RobotStatus.get_status(self.move_elevator_ex(elevator, 0.85, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.5)

    dbg()
    if RobotStatus.get_status(self.toggle_pumps(pumps, False, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    # Going back

    dbg()
    if RobotStatus.get_status(self.move_pumps_arm(pumps_arm, PumpsArmPosition.ALMOST_EXPANDED, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.2)

    dbg()
    if RobotStatus.get_status(self.forward(-180 if side == "front" else 180, async_task=False)) != RobotStatus.Reached:
        return RobotStatus.return_status(RobotStatus.Failed)

    dbg()
    if RobotStatus.get_status(self.move_elevator_ex(elevator, 0, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    dbg()
    if RobotStatus.get_status(self.move_plank_arm(plank_arms, PlankArmPosition.COLLAPSED, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    dbg()
    if RobotStatus.get_status(self.move_pumps_arm(pumps_arm, PumpsArmPosition.COLLAPSED, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    return RobotStatus.return_status(RobotStatus.Done, score=28)
