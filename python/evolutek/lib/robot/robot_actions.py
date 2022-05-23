from evolutek.lib.robot.robot_trajman import RecalSensor
from evolutek.lib.settings import ROBOT
from evolutek.lib.status import RobotStatus
from evolutek.lib.utils.color import Color
from evolutek.lib.utils.task import async_task
from evolutek.lib.utils.wrappers import if_enabled
from evolutek.lib.robot.robot_actuators import ElevatorConfig, HeadConfig, FrontArmsEnum

from time import sleep
from math import pi

from python.evolutek.lib.robot.robot_actuators import FrontArmsEnum, HeadSpeed


def pickup_statuette(self):
    # Mid and prepare to pickup
    self.set_elevator_config(arm=2, config=ElevatorConfig.Mid, async_task=False)
    self.set_head_config(arm=2, config=HeadConfig.Pickup, async_task=False)
    self.pumps_get(ids="2", async_task=False)   # Pump the central arm pump
    sleep(0.5)
    # Pickup
    self.set_elevator_config(arm=2, config=ElevatorConfig.StoreStatuette, async_task=False)
    sleep(0.2)
    self.pumps_drop(ids="4", async_task=False)
    sleep(1)


@if_enabled
@async_task
def statuette(self):
    pickup_statuette(self)
    # Places it
    self.set_head_config(arm=2, config=2, async_task=False)
    self.set_elevator_config(arm=2, config=2, async_task=False)
    status = self.goto_avoid(140, 225, async_task=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached:
        return RobotStatus.return_status(RobotStatus.get_status(status))
    sleep(0.2)
    self.pumps_drop(ids='2', async_task=False)
    sleep(0.1)
    # Moves back
    status = self.goto_avoid(x=250, y=225, async_task=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached:
        return RobotStatus.return_status(RobotStatus.get_status(status))
    sleep(0.3)
    self.set_head_config(arm=2, config=0, async_task=False)
    self.set_elevator_config(arm=2, config=5, async_task=False)
    return RobotStatus.return_status(RobotStatus.Done)


def drop_carrying(self):
    """Drop the carrying statuette"""
    pickup_statuette(self)
    self.set_head_config(arm=2, config=1, async_task=False)  # Head Down
    self.set_elevator_config(arm=2, config=2, async_task=False)  # Elevator to mid
    sleep(0.5)
    self.pumps_drop(ids="2", async_task=False)  # Drop the pumps
    sleep(0.5)
    self.set_elevator_speed(arm=2, speed=20, async_task=False)
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
@async_task
def indiana_jones(self):
    default_x = 1550
    default_y = 450
    default_angle = (5 * pi) / 4

    """

    TODO:
    Valeur dans FrontArmsEnum.Center.Galery faire en sorte que
    ça rentre plus dans la galerie

    """

    self.bumper_open(async_task=False)
    drop_carrying(self)  # Drop the carry statuette
    self.set_elevator_config(arm=FrontArmsEnum.Center, config=ElevatorConfig.StoreStatuette, async_task=False)  # Elevator to store statuette
    self.set_head_config(arm=FrontArmsEnum.Center, config=HeadConfig.Mid, async_task=False)  # Head to mid
    self.set_elevator_config(arm=FrontArmsEnum.Center, config=ElevatorConfig.GaleryLow, async_task=False)  # Elevator to mid
    self.pumps_get(ids="2", async_task=False)  # Pump the pump 2
    sleep(1)
    self.goth(theta=-pi/4, async_task=False)
    self.move_trsl(acc=200, dec=200, dest=100, maxspeed=500, sens=1)  # Advance to 100
    sleep(0.5)
    status = self.goto_avoid(x=default_x, y=default_y, async_task=False)
    #if RobotStatus.get_status(status) != RobotStatus.Reached:
    #   return RobotStatus.return_status(RobotStatus.get_status(status))
    self.set_head_speed(arm=FrontArmsEnum.Center, speed=HeadSpeed.VeryLow, async_task=False) # Reduce speed
    self.set_elevator_config(arm=FrontArmsEnum.Center, config=ElevatorConfig.StoreStatuette, async_task=False)  # Elevator to store statuette
    self.pumps_get(ids="4", async_task=False)  # Pump the pump 4
    self.set_elevator_config(arm=FrontArmsEnum.Center, config=ElevatorConfig.StoreStatuette, async_task=False)
    self.set_head_config(arm=FrontArmsEnum.Center, config=HeadConfig.Closed, async_task=False)  # Head up
    sleep(1.5)
    self.pumps_drop(ids="2", async_task=False)
    sleep(0.1)
    self.set_elevator_config(arm=FrontArmsEnum.Center, config=ElevatorConfig.GaleryLow, async_task=False)  # Elevator to mid
    sleep(0.2)
    self.set_head_config(arm=FrontArmsEnum.Center, config=HeadConfig.Down, async_task=False)  # Head down
    sleep(1)
    self.set_elevator_config(arm=FrontArmsEnum.Center, config=ElevatorConfig.Closed, async_task=False)  # Elevator to closed
    sleep(0.2)
    self.pumps_get(ids="2", async_task=False)  # Pump the pump 2
    self.move_trsl(acc=240, dec=200, dest=100, maxspeed=500, sens=1)  # Advance to 120
    sleep(0.5)
    self.set_elevator_config(arm=FrontArmsEnum.Center, config=ElevatorConfig.GaleryLow, async_task=False)  # Elevator to gallery
    sleep(0.5)
    self.set_elevator_config(arm=FrontArmsEnum.Center, config=ElevatorConfig.Closed, async_task=False)  # Elevator to closed
    self.snowplow_open(async_task=False)
    sleep(1)
    self.move_trsl(acc=200, dec=200, dest=100, maxspeed=400, sens=1)  # Advance to 100
    sleep(1)
    self.pumps_drop(ids="2", async_task=False)  # Drop the pump 2
    move_side_arms("head", self)
    sleep(0.3)
    move_side_arms("elevator_down", self)  # Activate arm movement func down
    sleep(0.6)
    move_side_arms("elevator_up", self)  # Activate arm movement func up
    sleep(0.2)
    status = self.goto_avoid(x=1400, y=600, async_task=False)
    #if RobotStatus.get_status(status) != RobotStatus.Reached:
    #   return RobotStatus.return_status(RobotStatus.get_status(status))
    self.snowplow_close(async_task=False)
    self.bumper_close(async_task=False)

    return RobotStatus.return_status(RobotStatus.Done)

def open_arm(side, score, self):
    if (side):
        self.right_arm_open(async_task = False)
        sleep(1)
        self.right_arm_close(async_task = False)
    else:
        self.left_arm_open(async_task = False)
        sleep(1)
        self.left_arm_close(async_task = False)
    return (score + 5)

@if_enabled
@async_task
def reverse_pattern(self):
    # Partie Speedy
    self.set_elevator_config(arm=1, config=0, async_task=False)
    self.set_elevator_config(arm=3, config=0, async_task=False) 
    self.set_head_config(arm=2, config=2, async_task=False)
    self.set_elevator_config(arm=2, config=0, async_task=False)
    sleep(1)
    self.goto_avoid(1910, 1130, async_task=False)
    self.move_trsl(10, 150, 150, 100, 1)
    sleep(0.5)
    self.set_elevator_config(arm=1, config=4, async_task=False)
    self.set_elevator_config(arm=3, config=4, async_task=False)
    sleep(1)
    """
    Pattern = self.get_pattern()
    self.set_elevator_config(arm=1, config=0, async_task=False)
    sleep(1)
    self.set_elevator_config(arm=3, config=0, async_task=False)
    sleep(1)
    self.move_trsl(10, 150, 150, 100, 0)
    sleep(0.5)
    self.goto_avoid(1800, 1130, async_task=False)

    self.goth(-(pi/2), async_task=False)
    pattern = Pattern - 1

    # Partie Jaro
    y = 1777.5
    if (pattern in [0, 3] and self.side) or (pattern in [1, 2] and not self.side):
        y = 1592.5
    self.goto_avoid(1830, y, async_task=False)

    # Partie reza
    if self.side:
        patterns = [
                [True, True, False, False, True, True, False],
                [False, True, True, True, False, False, True],
                [True, True, False, True, False, False, True],
                [False, True, True, False, True, True, False]
            ]
    else:
        patterns = [
                [True, True, False, True, False, False, True],
                [False, True, True, False, True, True, False],
                [True, True, False, False, True, True, False],
                [False, True, True, True, False, False, True]
            ]

    if (pattern in [0, 3] and self.side) or (pattern in [1, 2] and not self.side):
        plot = 5
    else:
        plot = 6
"""
    arm_open = self.left_arm_open if self.side else self.right_arm_open
    arm_close = self.left_arm_close if self.side else self.right_arm_close

    # Default pos : 2530
    """
    while self.trajman.get_position()['y'] > 680:
        # if patterns[pattern][plot]:
        sleep(1)
        arm_open(async_task=False)
        sleep(1)
        arm_close(async_task=False)
        sleep(1)

        #plot -= 1
        pos = self.trajman.get_position()["y"] - 185
        self.goto_avoid(1830, pos, async_task=False)
    """
    coords = self.get_pattern()
    score = 5
    self.set_elevator_config(arm=1, config = 0, async_task=False)
    self.set_elevator_config(arm=3, config = 0, async_task=False)
    my_y = self.trajman.get_position()['y']
    sleep(0.5)
    if not self.side: my_y = 3000 - my_y
    self.goto_avoid(1650, my_y, async_task = False)
    self.set_elevator_config(arm=2, config = 2, async_task=False)
    self.set_head_config(arm=2, config=0, async_task=False)
    sleep(1)

    while(len(coords) != 0):
        self.goto_avoid(1830, coords[0], async_task=False)
        self.goth(1.57, async_task=False)
        score = open_arm(self.side, score, self)
        coords.pop(0)

    return RobotStatus.return_status(RobotStatus.Done, score=score)

    # #if patterns[pattern][plot]:
    #    sleep(1)
    #    arm_open(async_task=False)
    #    sleep(1)
    #    arm_close(async_task=False)

@if_enabled
@async_task
def lift_sample(self):
    self.goto_avoid(340, 1975, async_task=False)
    self.set_elevator_config(arm=2, config=2, async_task=False)
    self.set_elevator_config(arm=2, config=0, async_task=False)
    self.goto_avoid(340, 1620, async_task=False)
    # self.actuators.pumps_drop(ids='2')



def to_radians(degrees):
    return degrees / 180 * pi


def play_path(rbt, path):
    for i in range(len(path)):
        point = path[i]
        if point[0] == "goto":
            rbt.goto_avoid(*point[1:], async_task=False)
        elif point[0] == "turn":
            rbt.goth(to_radians(point[1]), async_task=False)
        else:
            raise Exception("Invalid instruction : " + point[0])


@if_enabled
@async_task
def place_under(self):
    # Start pos = (995, 1360)
    path = [
        ("goto", 1194, 1360),
        ("turn", -50)
    ]

    play_path(self, path)

    # Be ready to collect samples
    self.snowplow_open(async_task=False)
    sleep(0.5)

    # Decress speed to have a better samples transport
    self.trajman.set_trsl_max_speed(80)

    # Transport samples (with a specific path to currectly position them)
    path = [
        ("goto", 1460, 560)
    ]

    play_path(self, path)

    # Reset move speed
    self.trajman.set_trsl_max_speed(100)

    back_pos = (1550, 460)
    front_pos = (1650, 340)

    # Down heads
    self.set_head_config(arm=FrontArmsEnum.Left,  config=HeadConfig.Down, async_task=False)
    self.set_head_config(arm=FrontArmsEnum.Right, config=HeadConfig.Down, async_task=False)
    sleep(0.8)

    # Down arms
    self.set_elevator_config(arm=FrontArmsEnum.Left,  config=ElevatorConfig.Down, async_task=False)
    self.set_elevator_config(arm=FrontArmsEnum.Right, config=ElevatorConfig.Down, async_task=False)
    sleep(0.8)

    # Grab the two extern sample
    self.pumps_get(ids="1", async_task=False)
    self.pumps_get(ids="3", async_task=False)

    # Got to back pos
    self.goto_avoid(*back_pos, async_task=False)

    # Push the middle sample
    self.goto_avoid(*front_pos, async_task=False) # Forward
    self.goto_avoid(*back_pos, async_task=False) # Backward

    # Release the two extern sample
    self.pumps_drop(ids="1", async_task=False)
    self.pumps_drop(ids="3", async_task=False)
    sleep(0.5)

    # Up arms
    self.set_elevator_config(arm=FrontArmsEnum.Left,  config=ElevatorConfig.Closed, async_task=False)
    self.set_elevator_config(arm=FrontArmsEnum.Right, config=ElevatorConfig.Closed, async_task=False)
    sleep(0.8)

    # Up heads
    self.set_head_config(arm=FrontArmsEnum.Left,  config=HeadConfig.Closed, async_task=False)
    self.set_head_config(arm=FrontArmsEnum.Right, config=HeadConfig.Closed, async_task=False)
    sleep(0.8)

    # Centralize the two remaining sample
    self.goth(to_radians(-45 - 30), async_task=False)
    self.goth(to_radians(-45 + 30), async_task=False)
    self.goth(to_radians(-45), async_task=False)

    # Down bumpers
    self.goto_avoid(1450, 550, async_task=False)
    self.bumper_open(async_task=False)
    sleep(0.5)
    input()

    # Push remaining samples
    self.goto_avoid(*front_pos, async_task=False) # Forward
    self.goto_avoid(*back_pos, async_task=False) # Backward

    # Close snowplows
    self.snowplow_close(async_task=False)
    sleep(0.5)

    # Up bumpers
    self.bumper_close(async_task=False)
    sleep(0.5)

    return RobotStatus.return_status(RobotStatus.Done)

