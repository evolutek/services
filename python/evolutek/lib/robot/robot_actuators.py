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
def move_elevator(self, id, position: ElevatorPosition)
    id = int(id)

    if(isinstance(position, str)):
        position = ElevatorPosition[position]

    return RobotStatus.check(self.actuators.stepper_goto(id, position.value[id]))

#############
#  MAGNETS  #
#############

class MagnetGroups(Enum):
    outer_AB = [0,3]
    elevator_AB = [1,2]
    outer_BC = [4,7]
    elevator_BC = [5,6]
    outer_CA = [8,11]
    elevator_CA = [9,10]

@if_enabled
@async_task
def grab(self, group: MagnetGroups):
    if(isinstance(group, str)):
        group = MagnetGroups[group]

    magnet(group, grab)

@if_enabled
@async_task
def drop(self, group: MagnetGroups):
    if(isinstance(group, str)):
        group = MagnetGroups[group]

    magnet(group, MagnetPosition.drop)

#############
#   TIPS    #
#############

class TipPositions(Enum):
    stow = [0,0,0,0,0,0]
    grab = [0,0,0,0,0,0]
    inside = [0,0,0,0,0,0]

@if_enabled
@async_task
def tip(self, group, position : TipPositions) :
    group = int(group)
    
    if(isinstance(position, str)):
        position = TipPositions[position]

    status1 = self.actuators.ax_move(self, group*2, position.value[group*2])
    status2 = self.actuators.ax_move(self, group*2 + 1, position.value[group*2 +1])

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
class ArmToAx(enum):
    A = [0,0]
    C = [0,0]

class ArmPosition(Enum):
    left = {ArmToAx.A.value[0] : 0, ArmToAx.C.value[0] : 0}
    center = {ArmToAx.A.value[0] : 0, ArmToAx.C.value[0] : 0}
    right = {ArmToAx.A.value[0] : 0, ArmToAx.C.value[0] : 0}

class ArmHeight(Enum):
    up = {ArmToAx.A.value[1] : 0, ArmToAx.C.value[1] : 0}
    down = {ArmToAx.A.value[1] : 0, ArmToAx.C.value[1] : 0}

def arm_height(self, arm : ArmToAx, height : ArmHeight):
    
    if(isinstance(arm, str)):
        arm = ArmToAx[arm]

    if(isinstance(height, str)):
        height = ArmHeight[height]

    return RobotStatus.check(self.actuators.ax_move(self, arm.value[1], height.value[arm.value[1]]))

def arm_position(self, arm : ArmToAx, position : ArmPosition):

    if(isinstance(arm, str)):
        arm = ArmToAx[arm]

    if(isinstance(height, str)):
        position = ArmPosition[position]

    return RobotStatus.check(self.actuators.ax_move(self, arm.value[0], position.value[arm.value[0]]))




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