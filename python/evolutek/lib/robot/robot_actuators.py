from enum import Enum
from evolutek.lib.status import RobotStatus
from evolutek.lib.utils.color import Color
from evolutek.lib.utils.task import async_task
from evolutek.lib.utils.wrappers import if_enabled
from time import sleep
from evolutek.lib.actuators.i2c_acts import I2CActsHandler, I2CActType, ESCVariation
from evolutek.lib.actuators.ax12 import AX12Controller
from evolutek.lib.indicators.lightning_mode import *

#############
# ELEVATORS #
#############

class ElevatorPosition(Enum):
    down = [0,0,0]
    second_approach = [0,0,0]
    second_place = [0,0,0]
    third_approach = [0,0,0]
    third_place = [0,0,0]

@if_enabled
@async_task
def move_elevator(self, id, position: ElevatorPosition):
    id = int(id)

    if(isinstance(position, str)):
        position = ElevatorPosition[position]

    return RobotStatus.check(self.actuators.stepper_goto(id, position.value[id]))

#############
#  MAGNETS  #
#############

servo_to_pca = [17,19,18,23,22,21,20,3,2,1,0,16]

class ServoPositions(Enum):
  grab = [40,50,160,145,30,20,160,160,40,20,170,165]
  drop = [160,170,50,20,160,150,40,30,170,170,40,50]

@if_enabled
@async_task
def magnet(self, ids: list[int], position: ServoPositions):
  print(ids, type(ids))
  if isinstance(position, str):
    position = ServoPositions[position]
  
  if isinstance(ids, str):
    ids = [int(i) for i in ids.split(',')]
     
  status = []
  for i in ids:
    status.append(self.actuators.servo_set_angle(servo_to_pca[i], position.value[i]))
  
  return RobotStatus.check(*status)



class MagnetGroups(Enum):
    outer_AB = [0,3]
    elevator_AB = [1,2]
    outer_BC = [4,7]
    elevator_BC = [5,6]
    outer_CA = [8,11]
    elevator_CA = [9,10]
    all = [0,1,2,3,4,5,6,7,8,9,10,11]

@if_enabled
@async_task
def grab(self, group: MagnetGroups):
    if(isinstance(group, str)):
        group = MagnetGroups[group]

    return RobotStatus.check(self.magnet(ids=group.value, position=ServoPositions.grab, async_task=False))

@if_enabled
@async_task
def drop(self, group: MagnetGroups):
    if(isinstance(group, str)):
        group = MagnetGroups[group]

    return RobotStatus.check(self.magnet(ids=group.value, position=ServoPositions.drop, async_task=False))

#############
#   TIPS    #
#############

class TipPositions(Enum):
    stow = [400,910,400,910,400,910]
    grab = [575,750,575,750,575,750]
    inside = [850,470,850,470,850,470]

@if_enabled
@async_task
def tip(self, group, position : TipPositions) :
    group = int(group)
    
    if(isinstance(position, str)):
        position = TipPositions[position]

    status1 = self.actuators.ax_move(group*2 +1, position.value[group*2])
    status2 = self.actuators.ax_move(group*2 +2, position.value[group*2 +1])

    return RobotStatus.check(status1, status2)


#############
#  SENSORS  #
#############

sensor_to_mcp = [0,0,0,0,0,0,0,0,0,0,0,0] # Note, les ids 12 et 13 (avec premier id 0) sont ceux des pompes respectivement 0 et 1

@async_task
def sensor(self, id) :
    id = int(id)

    return self.actuators.proximity_sensor_read(self, sensor_to_mcp[id])

#############
#   ARMS    #
#############

# Ids des ax de chaque bras (premiere valeur pour le latéral, deuxieme pour le vertical)
class ArmToAx(Enum):
    A = [7,8]
    C = [9,10]

class ArmPosition(Enum):
    left = {ArmToAx.A.value[0] : 775, ArmToAx.C.value[0] : 710}
    center = {ArmToAx.A.value[0] : 575, ArmToAx.C.value[0] : 505}
    right = {ArmToAx.A.value[0] : 375, ArmToAx.C.value[0] : 300}

class ArmHeight(Enum):
    up = {ArmToAx.A.value[1] : 375, ArmToAx.C.value[1] : 325}
    down = {ArmToAx.A.value[1] : 640, ArmToAx.C.value[1] : 575}

def arm_height(self, arm : ArmToAx, height : ArmHeight):
    
    if(isinstance(arm, str)):
        arm = ArmToAx[arm]

    if(isinstance(height, str)):
        height = ArmHeight[height]

    return RobotStatus.check(self.actuators.ax_move(arm.value[1], height.value[arm.value[1]]))

def arm_position(self, arm : ArmToAx, position : ArmPosition):

    if(isinstance(arm, str)):
        arm = ArmToAx[arm]

    if(isinstance(position, str)):
        position = ArmPosition[position]
        
    self.actuators.ax_set_speed(arm.value[0], 200)

    return RobotStatus.check(self.actuators.ax_move(arm.value[0], position.value[arm.value[0]]))

def arm_grab(self, arm : ArmToAx):
    if(isinstance(arm, str)):
        arm = ArmToAx[arm]
        
    if(arm == ArmToAx.A):   
        return RobotStatus.check(self.actuators.pumps_on([1]))
    else:
        return RobotStatus.check(self.actuators.pumps_on([0]))
    
def arm_drop(self, arm : ArmToAx):
    if(isinstance(arm, str)):
        arm = ArmToAx[arm]
        
    if(arm == ArmToAx.A):   
        return RobotStatus.check(self.actuators.pumps_off([1]))
    else:
        return RobotStatus.check(self.actuators.pumps_off([0]))
  

'''
class PumpsArmId(Enum):
    FRONT = 9
    #BACK = ?

class PumpsArmPosition(Enum):
    COLLAPSED       = {PumpsArmId.FRONT: 20}
    EXPANDED        = {PumpsArmId.FRONT: 105}
    ALMOST_EXPANDED = {PumpsArmId.FRONT: 90}
    #MORE_EXPANDED   = {PumpsArmId.FRONT: 110}

@if_enabled
@async_task
def move_pumps_arm(self, id: PumpsArmId, position: PumpsArmPosition):
    if isinstance(id, str):
        id = PumpsArmId[id]

    if isinstance(position, str):
        position = PumpsArmPosition[position]

    angles = position.value[id]

    status = RobotStatus.check(self.actuators.servo_set_angle(
        id.value,
        position.value[id]
    ))

    if RobotStatus.get_status(status) != RobotStatus.Done:
        return status

    #sleep(1)

    return RobotStatus.return_status(RobotStatus.Done)
'''
"""
class ArmPosition(Enum):
    OPEN = [45, 45]
    CLOSE = [0, 0]


@if_enabled
@async_task
def move_elevator(self, position: ArmPosition):
    # TODO: Use correct servo id
    status1 = self.actuators.servo_set_angle(1, position[0])
    status2 = self.actuators.servo_set_angle(2, position[1])
    return RobotStatus.check(status1, status2)


# TODO: Use correct angles
# This a list of angle with one angle per clamp,
# so here there list of length 3, so there is 3 clamps
class ClampsPosition(Enum):
    OPEN = [45, 45, 45]
    CLOSE = [0, 0, 0]

# Map clamps to their servo id
CLAMP_ID_TO_SERVO_ID = [2, 3, 4]

@if_enabled
@async_task
def move_clamps(self, clamp_ids: list[int], position: ClampsPosition):
    status = []
    for clamp_id in clamp_ids:
        status.append(self.actuators.servo_set_angle(CLAMP_ID_TO_SERVO_ID[clamp_id], position[clamp_id]))
    return RobotStatus.check(*status   )


# Magnet id is 0, 1 or 2

@if_enabled
@async_task
def magnets_on(self, magnet_ids: list[int]):
    return RobotStatus.check(self.actuators.magnets_on(magnet_ids))

@if_enabled
@async_task
def magnets_off(self, magnet_ids: list[int]):
    return RobotStatus.check(self.actuators.magnets_off(magnet_ids))
"""