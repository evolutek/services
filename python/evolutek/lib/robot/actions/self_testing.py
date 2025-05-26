from evolutek.lib.robot.robot_actions_imports import *
from evolutek.lib.robot.robot_actuators import ArmPositions, ClawPositions
from evolutek.lib.indicators.lightning_mode import *

from random import *

@if_enabled
@async_task
def initial_position(self):
    # for side in range(3):    
    #     if RobotStatus.get_status(self.move_claw(side, ClawPositions.CLOSE, async_task=False)) != RobotStatus.Done:
    #         return RobotStatus.return_status(RobotStatus.Failed)
    #     if RobotStatus.get_status(self.move_arm(side, ArmPositions.LOW, async_task=False)) != RobotStatus.Done:
    #         return RobotStatus.return_status(RobotStatus.Failed)

    if RobotStatus.get_status(self.move_claw(1, ClawPositions.CLOSE, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)
    if RobotStatus.get_status(self.move_arm(1, ArmPositions.LOW, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)
    if RobotStatus.get_status(self.move_claw(2, ClawPositions.CLOSE, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)
    if RobotStatus.get_status(self.move_arm(2, ArmPositions.LOW, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)
    if RobotStatus.get_status(self.move_claw(3, ClawPositions.CLOSE, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)
    if RobotStatus.get_status(self.move_arm(3, ArmPositions.LOW, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)


    sleep(1)
    return RobotStatus.return_status(RobotStatus.Done)
    

@if_enabled
@async_task
def promo_video(self):
  
  self.actuators.rgb_led_strip_set_mode(LightningMode.Error.value)
  
  for i in range(100):
    print('Promo Video : ', i, '/100')
    if RobotStatus.get_status(self.actuators.servo_set_angle(randint(1,3), randint(15,150))) != RobotStatus.Done:
      return RobotStatus.return_status(RobotStatus.Failed)
    if RobotStatus.get_status(self.actuators.ax_move(randint(1,3), randint(200,590))) != RobotStatus.Done:
      return RobotStatus.return_status(RobotStatus.Failed)
    sleep(0.4)

  return RobotStatus.return_status(RobotStatus.Done)