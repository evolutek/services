from enum import Enum
from evolutek.lib.status import RobotStatus
from evolutek.lib.utils.color import Color
from evolutek.lib.utils.task import async_task
from evolutek.lib.utils.wrappers import if_enabled
from time import sleep
from evolutek.lib.actuators.i2c_acts import I2CActsHandler, I2CActType, ESCVariation
from evolutek.lib.actuators.ax12 import AX12Controller
from evolutek.lib.indicators.lightning_mode import *



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