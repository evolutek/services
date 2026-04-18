from evolutek.lib.robot.robot_actions_imports import *
from evolutek.lib.robot.robot_actuators import *

@if_enabled
@async_task
def initial(self):
    status = []
    status.append(self.move(1, "up", async_task=False))
    status.append(self.move(2, "up", async_task=False))
    status.append(self.move(3, "up", async_task=False))
    status.append(self.move(1, "a", async_task=False))
    status.append(self.move(2, "a", async_task=False))
    status.append(self.move(3, "a", async_task=False))
    return RobotStatus.check(*status)

@if_enabled
@async_task
def prepare_grab(self, face):
    face = int(face)
    status = []
    status.append(self.move(face, "down", async_task=False))
    status.append(self.move(face, "opened", async_task=False))
    status.append(self.move(face, "a", async_task=False))
    return RobotStatus.check(*status)

@if_enabled
@async_task
def grab(self, face):
    if self.side:
        goal_color = "BLUE"
    else :
        goal_color = "YELLOW"

    face = int(face)
    status = []
    status.append(self.move(face, "closed", async_task=False))
    sleep(0.5)
    status.append(self.move(face * 10 + 1, "up", async_task=False))
    status.append(self.move(face * 10 + 2, "half", async_task=False))
    status.append(self.move(face * 10 + 3, "up", async_task=False))
    status.append(self.move(face * 10 + 4, "half", async_task=False))
    sleep(0.5)
    for i in range(1, 5):
        color = self.actuators.color_read(i)
        if (color != goal_color):
            status.append(self.move(face * 10 + i, "b", async_task=False))
    sleep(0.5)
    status.append(self.move(face, "up", async_task=False))


    return RobotStatus.check(*status)



'''
#########
# RESET #
#########

@if_enabled
@async_task
def setup(self):
    print("Reset")
    status = []
    status.append(self.drop(MagnetGroups.all, async_task=False))
    status.append(self.move_elevator(2, ElevatorPosition.down, 300, async_task=False))
    status.append(self.move_elevator(1, ElevatorPosition.down, 300, async_task=False))
    status.append(self.move_elevator(0, ElevatorPosition.banner, 300, async_task=False))
    status.append(self.grab(MagnetGroups.elevator_AB, async_task=False))
    status.append(self.arm_height(ArmToAx.A, ArmHeight.up))
    status.append(self.arm_height(ArmToAx.C, ArmHeight.up))
    status.append(self.tip(0, TipPositions.stow))
    status.append(self.tip(1, TipPositions.stow))
    status.append(self.tip(2, TipPositions.stow))
    status.append(self.arm_position(ArmToAx.A, ArmPosition.center))
    status.append(self.arm_position(ArmToAx.C, ArmPosition.center))

    print("TODO")
    return RobotStatus.check(*status)

##############
# DROP BANER #
##############
@if_enabled
@async_task
def drop_banner(self):
    status = RobotStatus.check(self.drop(MagnetGroups.elevator_AB))
    sleep(1);
    return status


##############
# GRAB STACK #
##############
class Zone(Enum):
    AB = 0,
    BC = 1,
    CA = 2,

@if_enabled
@async_task
def grab_stack(self, zone: Zone):
    status = []

    if(isinstance(zone, str)):
        zone = Zone[zone]
    
    if(zone == Zone.AB):
        status.append(RobotStatus.check(self.grab(MagnetGroups.elevator_AB, async_task=False)))
        status.append(RobotStatus.check(self.grab(MagnetGroups.outer_AB, async_task=False)))
        status.append(RobotStatus.check(self.tip(0, TipPositions.grab, async_task=False)))
    elif(zone == Zone.BC):
        status.append(RobotStatus.check(self.grab(MagnetGroups.elevator_BC, async_task=False)))
        status.append(RobotStatus.check(self.grab(MagnetGroups.outer_BC, async_task=False)))
        status.append(RobotStatus.check(self.tip(1, TipPositions.grab, async_task=False)))

    elif(zone == Zone.CA):
        status.append(RobotStatus.check(self.grab(MagnetGroups.elevator_CA, async_task=False)))
        status.append(RobotStatus.check(self.grab(MagnetGroups.outer_CA, async_task=False)))
        status.append(RobotStatus.check(self.tip(2, TipPositions.grab, async_task=False)))
    
    return RobotStatus.check(*status)

@if_enabled
@async_task
def drop_stack(self, zone: Zone):
    status = []

    if(isinstance(zone, str)):
        zone = Zone[zone]
    
    if(zone == Zone.AB):
        status.append(RobotStatus.check(self.drop(MagnetGroups.elevator_AB, async_task=False)))
        status.append(RobotStatus.check(self.drop(MagnetGroups.outer_AB, async_task=False)))
        status.append(RobotStatus.check(self.tip(0, TipPositions.stow, async_task=False)))
    elif(zone == Zone.BC):
        status.append(RobotStatus.check(self.drop(MagnetGroups.elevator_BC, async_task=False)))
        status.append(RobotStatus.check(self.drop(MagnetGroups.outer_BC, async_task=False)))
        status.append(RobotStatus.check(self.tip(1, TipPositions.stow, async_task=False)))

    elif(zone == Zone.CA):
        status.append(RobotStatus.check(self.drop(MagnetGroups.elevator_CA, async_task=False)))
        status.append(RobotStatus.check(self.drop(MagnetGroups.outer_CA, async_task=False)))
        status.append(RobotStatus.check(self.tip(2, TipPositions.stow, async_task=False)))
    
    return RobotStatus.check(*status)


#########
# BUILD #
#########

@if_enabled
@async_task
def build(self, zone: Zone):
    if(isinstance(zone, str)):
        zone = Zone[zone]
    
    if(zone == Zone.AB):
        if RobotStatus.check(self.arm_position(ArmToAx.A, ArmPosition.left)) != RobotStatus.Done:
            return RobotStatus.Failed
        sleep(1)
        if RobotStatus.check(self.arm_height(ArmToAx.A, ArmHeight.down)) != RobotStatus.Done:
            return RobotStatus.Failed
        if RobotStatus.check(self.arm_grab(ArmToAx.A)) != RobotStatus.Done:
            return RobotStatus.Failed
        sleep(1)
        if RobotStatus.check(self.arm_position(ArmToAx.A, ArmPosition.right)) != RobotStatus.Done:
            return RobotStatus.Failed
        if RobotStatus.check(self.arm_height(ArmToAx.A, ArmHeight.up)) != RobotStatus.Done:
            return RobotStatus.Failed
        sleep(1)
        if(RobotStatus.check(self.actuators.move_elevator(0, ElevatorPosition.third_approach)) != RobotStatus.Done):
            return RobotStatus.Failed
        sleep(3)
        if(RobotStatus.check(self.actuators.arm_position(ArmToAx.A, ArmPosition.left)) != RobotStatus.Done):
            return RobotStatus.Failed
        sleep(1)
        #if(RobotStatus.check(self.actuators.arm_height(ArmToAx.A, ArmHeight.down)) != RobotStatus.Done):
        #    return RobotStatus.Failed
        if(RobotStatus.check(self.arm_drop(ArmToAx.A)) != RobotStatus.Done):
            return RobotStatus.Failed
        sleep(1)
        if(RobotStatus.check(self.arm_position(ArmToAx.A, ArmPosition.center)) != RobotStatus.Done):
            return RobotStatus.Failed
        sleep(1)
        if(RobotStatus.check(self.move_elevator(0,ElevatorPosition.second_place)) != RobotStatus.Done):
            return RobotStatus.Failed
        sleep(1)
        if(RobotStatus.check(self.drop(MagnetGroups.elevator_AB)) != RobotStatus.Done):
            return RobotStatus.Failed
        if(RobotStatus.check(self.drop(MagnetGroups.outer_AB)) != RobotStatus.Done):
            return RobotStatus.Failed
            
    elif(zone == Zone.BC):
        if RobotStatus.check(self.arm_position(ArmToAx.C, ArmPosition.right)) != RobotStatus.Done:
            return RobotStatus.Failed
        sleep(1)
        if RobotStatus.check(self.arm_height(ArmToAx.C, ArmHeight.down)) != RobotStatus.Done:
            return RobotStatus.Failed
        if RobotStatus.check(self.actuators.pumps_on([0])) != RobotStatus.Done:
            return RobotStatus.Failed
        sleep(1)
        if RobotStatus.check(self.arm_position(ArmToAx.C, ArmPosition.left)) != RobotStatus.Done:
            return RobotStatus.Failed
        if RobotStatus.check(self.arm_height(ArmToAx.C, ArmHeight.up)) != RobotStatus.Done:
            return RobotStatus.Failed
        sleep(1)
        if(RobotStatus.check(self.actuators.move_elevator(1, ElevatorPosition.third_approach)) != RobotStatus.Done):
            return RobotStatus.Failed
        sleep(3)
        if(RobotStatus.check(self.actuators.arm_position(ArmToAx.C, ArmPosition.right)) != RobotStatus.Done):
            return RobotStatus.Failed
        sleep(1)
        #if(RobotStatus.check(self.actuators.arm_height(ArmToAx.A, ArmHeight.down)) != RobotStatus.Done):
        #    return RobotStatus.Failed
        if(RobotStatus.check(self.actuators.pumps_off([0])) != RobotStatus.Done):
            return RobotStatus.Failed
        sleep(1)
        if(RobotStatus.check(self.arm_position(ArmToAx.C, ArmPosition.center)) != RobotStatus.Done):
            return RobotStatus.Failed
        sleep(1)
        if(RobotStatus.check(self.move_elevator(1,ElevatorPosition.second_place)) != RobotStatus.Done):
            return RobotStatus.Failed
        sleep(1)
        if(RobotStatus.check(self.drop(MagnetGroups.elevator_BC)) != RobotStatus.Done):
            return RobotStatus.Failed
        if(RobotStatus.check(self.drop(MagnetGroups.outer_BC)) != RobotStatus.Done):
            return RobotStatus.Failed
    elif(zone == Zone.CA):
        if RobotStatus.check(self.arm_position(ArmToAx.A, ArmPosition.right)) != RobotStatus.Done:
            return RobotStatus.Failed
        sleep(1)
        if RobotStatus.check(self.arm_height(ArmToAx.A, ArmHeight.down)) != RobotStatus.Done:
            return RobotStatus.Failed
        if RobotStatus.check(self.actuators.pumps_on([1])) != RobotStatus.Done:
            return RobotStatus.Failed
        sleep(1)
        if RobotStatus.check(self.arm_position(ArmToAx.A, ArmPosition.left)) != RobotStatus.Done:
            return RobotStatus.Failed
        if RobotStatus.check(self.arm_height(ArmToAx.A, ArmHeight.up)) != RobotStatus.Done:
            return RobotStatus.Failed
        sleep(1)
        if(RobotStatus.check(self.actuators.move_elevator(2, ElevatorPosition.third_approach)) != RobotStatus.Done):
            return RobotStatus.Failed
        sleep(3)
        if(RobotStatus.check(self.actuators.arm_position(ArmToAx.A, ArmPosition.right)) != RobotStatus.Done):
            return RobotStatus.Failed
        sleep(1)
        #if(RobotStatus.check(self.actuators.arm_height(ArmToAx.A, ArmHeight.down)) != RobotStatus.Done):
        #    return RobotStatus.Failed
        if(RobotStatus.check(self.actuators.pumps_off([1])) != RobotStatus.Done):
            return RobotStatus.Failed
        sleep(1)
        if(RobotStatus.check(self.arm_position(ArmToAx.A, ArmPosition.center)) != RobotStatus.Done):
            return RobotStatus.Failed
        sleep(1)
        if(RobotStatus.check(self.move_elevator(0,ElevatorPosition.second_place)) != RobotStatus.Done):
            return RobotStatus.Failed
        sleep(1)
        if(RobotStatus.check(self.drop(MagnetGroups.elevator_CA)) != RobotStatus.Done):
            return RobotStatus.Failed
        if(RobotStatus.check(self.drop(MagnetGroups.outer_CA)) != RobotStatus.Done):
            return RobotStatus.Failed
'''