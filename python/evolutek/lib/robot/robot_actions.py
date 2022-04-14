from evolutek.lib.robot.robot_trajman import RecalSensor
from evolutek.lib.settings import ROBOT
from evolutek.lib.status import RobotStatus
from evolutek.lib.utils.color import Color
from evolutek.lib.utils.task import async_task
from evolutek.lib.utils.wrappers import if_enabled

from time import sleep
from math import pi


@if_enabled
def statuette(self):
    # self.free()
    # self.unfree()
    self.actuators.pumps_get(ids='4', async_task=False)
    self.set_head_config(arm=2, config=0, async_task=False)
    self.set_elevator_config(arm=2, config=2, async_task=False)
    print('Please poot the statuette')
    self.actuators.pumps_get(ids='2', async_task=False)
    self.set_elevator_config(arm=2, config=5, async_task=False)
    sleep(0.5)
    self.actuators.pumps_drop(ids='4', async_task=False)
    self.set_head_config(arm=2, config=2, async_task=False)
    self.set_elevator_config(arm=2, config=2, async_task=False)
    status = self.goto_avoid(120, 225, async_task=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached:
        return RobotStatus.return_status(RobotStatus.get_status(status))
    self.actuators.pumps_drop(ids='2', async_task=False)
    status = self.goto_avoid(250, 225)
    if RobotStatus.get_status(status) != RobotStatus.Reached:
        return RobotStatus.return_status(RobotStatus.get_status(status))
    self.set_head_config(arm=2, config=0, async_task=False)
    self.set_elevator_config(arm=2, config=5, async_task=False)

    return RobotStatus.return_status(RobotStatus.Done)


def drop_carrying(self):
    """Drop the carrying statuette"""
    self.set_elevator_config(arm=2, config=2, async_task=False)  # Elevator to mid
    self.set_head_config(arm=2, config=0, async_task=False)   # Head Closed
    self.pumps_get(ids="2", async_task=False)   # Pump the pump 2
    sleep(0.5)
    self.set_elevator_config(arm=2, config=5, async_task=False)  # Elevator to store statuette
    sleep(1)
    self.set_head_config(arm=2, config=1, async_task=False)  # Head Down
    self.set_elevator_config(arm=2, config=6, async_task=False)  # Elevator to mid
    sleep(0.5)
    self.pumps_drop(ids="2", async_task=False)  # Drop the pumps
    sleep(0.5)
    self.set_elevator_speed(arm=2, speed=100, async_task=False)
    self.set_elevator_config(arm=2, config=5, async_task=False)  # Elevator to mid
    sleep(0.5)
    self.set_elevator_speed(arm=2, speed=1023, async_task=False)
    self.stop_evs(ids="2", async_task=False)

def move_side_arms(status, self):
    """Move the side arms to the right position
    -head     : move the head of the arms
    -elevator_down : move the elevation of the arms down"""

    if (status == "head"):
        self.pumps_get(ids="1", async_task=False)  # Pump the pump 1
        self.pumps_get(ids="3", async_task=False)  # Pump the pump 3
        self.set_head_config(arm=1, config=1, async_task=False)  # Head down
        self.set_head_config(arm=3, config=1, async_task=False)  # Head down
    elif (status == "elevator_down"):
        self.set_elevator_config(arm=1, config=2, async_task=False)  # Head mid
        self.set_elevator_config(arm=3, config=2, async_task=False)  # Head mid
    elif (status == "elevator_up"):
        self.set_elevator_config(arm=1, config=0, async_task=False)  # Head up
        self.set_elevator_config(arm=3, config=0, async_task=False)  # Head up
    else:
        print("Error: wrong status")
    print(f"Done action : {status}")


@if_enabled
def indiana_jones(self):
    default_x = 1550
    default_y = 450
    default_angle = (5 * pi) / 4

    self.bumper_open(async_task=False)
    drop_carrying(self)  # Drop the carry statuette
    self.set_elevator_config(arm=2, config=5, async_task=False)  # Elevator to store statuette
    self.set_head_config(arm=2, config=2, async_task=False)  # Head to mid
    self.set_elevator_config(arm=2, config=3, async_task=False)  # Elevator to mid
    self.pumps_get(ids="2", async_task=False)  # Pump the pump 2
    sleep(1)
    self.goth(theta=-pi/4)
    self.move_trsl(acc=200, dec=200, dest=150, maxspeed=500, sens=1)  # Advance to 95
    sleep(0.5)
    status = self.goto_avoid(x=default_x, y=default_y, async_task=False)
    #if RobotStatus.get_status(status) != RobotStatus.Reached:
     #   return RobotStatus.return_status(RobotStatus.get_status(status))
    self.set_elevator_config(arm=2, config=5, async_task=False)  # Elevator to store statuette
    self.pumps_get(ids="4", async_task=False)  # Pump the pump 4
    self.set_elevator_config(arm=2, config=5, async_task=False)
    self.set_head_config(arm=2, config=0, async_task=False)  # Head up
    sleep(0.3)
    self.pumps_drop(ids="2", async_task=False)
    sleep(0.1)
    self.set_elevator_config(arm=2, config=3, async_task=False)  # Elevator to mid
    sleep(0.2)
    self.set_head_config(arm=2, config=1, async_task=False)  # Head down
    self.set_elevator_config(arm=2, config=0, async_task=False)  # Elevator to closed
    self.move_trsl(acc=240, dec=200, dest=120, maxspeed=500, sens=1)  # Advance to 120
    self.pumps_get(ids="2", async_task=False)  # Pump the pump 2
    self.set_elevator_config(arm=2, config=3, async_task=False)  # Elevator to gallery
    self.set_elevator_config(arm=2, config=0, async_task=False)  # Elevator to closed
    self.snowplow_open(async_task=False)
    self.move_trsl(acc=200, dec=200, dest=100, maxspeed=400, sens=1)  # Advance to 100
    self.pumps_drop(ids="2", async_task=False)  # Drop the pump 2
    move_side_arms("head", self)
    move_side_arms("elevator_down", self)  # Activate arm movement func down
    move_side_arms("elevator_up", self)  # Activate arm movement func up
    status = self.goto_avoid(x=default_x, y=default_y, async_task=False)
    #if RobotStatus.get_status(status) != RobotStatus.Reached:
     #   return RobotStatus.return_status(RobotStatus.get_status(status))
    self.snowplow_close(async_task=False)
    self.bumper_close(async_task=False)
    print("Finished !")

@if_enabled
def reverse_pattern(self):
    # Partie Speedy
    self.set_elevator_config(arm=1, config=0, async_task=False)
    self.set_elevator_config(arm=3, config=0, async_task=False)
    self.set_elevator_config(arm=2, config=0, async_task=False)
    self.goto_avoid(1910, 1130, async_task=False)
    self.move_trsl(10, 150, 150, 100, 1)
    sleep(0.5)
    self.set_elevator_config(arm=1, config=4, async_task=False)
    self.set_elevator_config(arm=3, config=4, async_task=False)
    Pattern = self.get_pattern()
    self.set_elevator_config(arm=1, config=0, async_task=False)
    self.set_elevator_config(arm=3, config=0, async_task=False)
    self.move_trsl(10, 150, 150, 100, 0)
    sleep(0.5)
    self.goto_avoid(1800, 1130, async_task=False)

    # Partie Jaro
    y = 1777.5
    if(Pattern == 1 or Pattern == 4):
        y = 1592.5
    self.goto_avoid(1830, y, async_task=False)

    # Partie reza
    pattern = Pattern - 1
    patterns = [
            [True, True, False, False, True, True, False],
            [False, True, True, True, False, False, True],
            [True, True, False, True, False, False, True],
            [False, True, True, False, True, True, False]
            ]
    if pattern in [0, 3]:
        plot = 5
    else:
        plot = 6
    while self.get_position(async_task=False)['y'] > 680:
        if patterns[pattern][plot]:
            self.left_arm_open(async_task=False)
            self.left_arm_close(async_task=False)
        plot -= 1
        self.goto_avoid(1830, self.get_position()['y']-185, async_task=False)

    if patterns[pattern][plot]:
        self.left_arm_open(async_task=False)
        self.left_arm_close(async_task=False)

@if_enabled
def lift_sample(self):
    self.goto_avoid(340, 1975, async_task=False)
    self.set_elevator_config(arm=2, config=2, async_task=False)
    self.set_elevator_config(arm=2, config=0, async_task=False)
    self.goto_avoid(340, 1620, async_task=False)
    # self.actuators.pumps_drop(ids='2')

