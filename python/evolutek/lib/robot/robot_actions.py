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
    # self.trajman.free()
    # self.trajman.unfree()
    self.actuators.pumps_get(ids='4')
    self.set_head_config(arm=2, config=0)
    self.set_elevator_config(arm=2, config=2)
    print('Please poot the statuette')
    self.actuators.pumps_get(ids='2')
    self.set_elevator_config(arm=2, config=5)
    sleep(0.5)
    self.actuators.pumps_drop(ids='4')
    self.set_head_config(arm=2, config=2)
    self.set_elevator_config(arm=2, config=2)
    status = self.goto_avoid(120, 225)
    if RobotStatus.get_status(status) != RobotStatus.Reached:
        return RobotStatus.return_status(RobotStatus.get_status(status))
    self.actuators.pumps_drop(ids='2')
    status = self.goto_avoid(250, 225)
    if RobotStatus.get_status(status) != RobotStatus.Reached:
        return RobotStatus.return_status(RobotStatus.get_status(status))
    self.set_head_config(arm=2, config=0)
    self.set_elevator_config(arm=2, config=5)

    return RobotStatus.return_status(RobotStatus.Done)


def drop_carrying(self):
    """Drop the carrying statuette"""
    self.set_elevator_config(arm=2, config=2)  # Elevator to mid
    self.set_head_config(arm=2, config=0)  # Head Closed
    self.pumps_get(ids="2")  # Pump the pump 2
    self.set_elevator_config(arm=2, config=5)  # Elevator to store statuette
    self.set_head_config(arm=2, config=1)  # Head Down
    self.set_elevator_config(arm=2, config=3)  # Elevator to mid
    self.pumps_drop(ids="2")  # Drop the pumps
    

def move_side_arms(status, self):
    """Move the side arms to the right position
    -head     : move the head of the arms
    -elevator_down : move the elevation of the arms down"""

    if (status == "head"):
        self.pumps_get(ids="1")  # Pump the pump 1
        self.pumps_get(ids="3")  # Pump the pump 3
        self.set_head_config(arm=1, config=1)  # Head down
        self.set_head_config(arm=3, config=1)  # Head down
    elif (status == "elevator_down"):
        self.set_elevator_config(arm=1, config=2)  # Head mid
        self.set_elevator_config(arm=3, config=2)  # Head mid
    elif (status == "elevator_up"):
        self.set_elevator_config(arm=1, config=0)  # Head up
        self.set_elevator_config(arm=3, config=0)  # Head up
    else:
        print("Error: wrong status")
    print(f"Done action : {status}")


@if_enabled
def indiana_jones(self):
    default_x = 1550
    default_y = 450
    default_angle = (5 * pi) / 4
    self.bumper_open()
    drop_carrying(self)  # Drop the carry statuette
    self.set_elevator_config(arm=2, config=5)  # Elevator to store statuette
    self.set_head_config(arm=2, config=2)  # Head to mid
    self.set_elevator_config(arm=2, config=3)  # Elevator to mid
    self.pumps_get(ids="2")  # Pump the pump 2
    self.trajman.move_trsl(acc=200, dec=200, dest=95, maxspeed=500, sens=1)  # Advance to 95
    status = self.goto_avoid(x=default_x, y=default_y)
    if RobotStatus.get_status(status) != RobotStatus.Reached:
        return RobotStatus.return_status(RobotStatus.get_status(status))
    self.set_elevator_config(arm=2, config=5)  # Elevator to store statuette
    self.pumps_get(ids="4")  # Pump the pump 4
    self.set_head_config(arm=2, config=0)  # Head up
    # self.pumps_drop(ids = "2") # Drop the pumps
    self.set_elevator_config(arm=2, config=3)  # Elevator to mid
    self.set_head_config(arm=2, config=1)  # Head down
    self.set_elevator_config(arm=2, config=0)  # Elevator to closed
    self.trajman.move_trsl(acc=200, dec=200, dest=100, maxspeed=500, sens=1)  # Advance to 100
    self.pumps_get(ids="2")  # Pump the pump 2
    self.set_elevator_config(arm=2, config=3)  # Elevator to gallery
    self.set_elevator_config(arm=2, config=0)  # Elevator to closed
    self.snowplow_open()
    self.trajman.move_trsl(acc=200, dec=200, dest=90, maxspeed=400, sens=1)  # Advance to 90
    self.pumps_drop(ids="2")  # Drop the pump 2
    move_side_arms("head", self)
    move_side_arms("elevator_down", self)  # Activate arm movement func down
    move_side_arms("elevator_up", self)  # Activate arm movement func up
    status = self.goto_avoid(x=default_x, y=default_y)
    if RobotStatus.get_status(status) != RobotStatus.Reached:
        return RobotStatus.return_status(RobotStatus.get_status(status))
    self.snowplow_close()
    self.bumper_close()
    print("Finished !")

@if_enabled
def reverse_pattern(self):
    # Partie Speedy
    self.set_elevator_config(arm=1, config=0)
    self.set_elevator_config(arm=3, config=0)
    self.set_elevator_config(arm=2, config=0)
    self.goto(1910, 1130)
    self.trajman.move_trsl(10, 150, 150, 100, 1)
    sleep(0.5)
    self.set_elevator_config(arm=1, config=4)
    self.set_elevator_config(arm=3, config=4)
    Pattern = self.get_pattern()
    self.set_elevator_config(arm=1, config=0)
    self.set_elevator_config(arm=3, config=0)
    self.trajman.move_trsl(10, 150, 150, 100, 0)
    sleep(0.5)
    self.goto(1800, 1130)
    
    # Partie Jaro
    y = 1777.5
    if(Pattern == 1 or Pattern == 4):
        y = 1592.5
    self.goto(1830, y)

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
    while self.trajman.get_position()['y'] > 680:
        if patterns[pattern][plot]:
            self.left_arm_open()    
            self.left_arm_close()
        plot -= 1
        self.goto(1830, self.trajman.get_position()['y']-185)
    
    if patterns[pattern][plot]:
        self.left_arm_open()
        self.left_arm_close()

@if_enabled
def lift_sample(self):
    self.goto(340, 1975)
    self.set_elevator_config(arm=2, config=2)
    self.set_elevator_config(arm=2, config=0)
    self.goto(340, 1620)
    # self.actuators.pumps_drop(ids='2')
