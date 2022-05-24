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
    self.robot.set_head_config(arm=2, config=0)
    self.robot.set_elevator_config(arm=2, config=2)
    print('Please poot the statuette')
    self.actuators.pumps_get(ids='2')
    self.robot.set_elevator_config(arm=2, config=5)
    sleep(0.5)
    self.actuators.pumps_drop(ids='4')
    self.robot.set_head_config(arm=2, config=2)
    self.robot.set_elevator_config(arm=2, config=2)
    status = self.robot.goto_avoid(120, 225)
    if RobotStatus.get_status(status) != RobotStatus.Reached:
        return RobotStatus.return_status(RobotStatus.get_status(status))
    self.actuators.pumps_drop(ids='2')
    status = self.robot.goto_avoid(250, 225)
    if RobotStatus.get_status(status) != RobotStatus.Reached:
        return RobotStatus.return_status(RobotStatus.get_status(status))
    self.robot.set_head_config(arm=2, config=0)
    self.robot.set_elevator_config(arm=2, config=5)

    return RobotStatus.return_status(RobotStatus.Done)


@if_enabled
def indiana_jones(self):
    default_x = 1550
    default_y = 450
    default_angle = (5 * pi) / 4

    def init_bot():
        """Initialize the bot and return the proxy object"""

        self.trajman.free()
        self.robot.set_pos(x=default_x, y=default_y, theta=default_angle)
        self.trajman.unfree()
        print("\n\nReseting positions...\n\n")
        sleep(0.5)
        self.robot.reset()
        print("Initalization done !")
        return self

    def move_side_arms(status, self):
        """Move the side arms to the right position
        -head     : move the head of the arms
        -elevator_down : move the elevation of the arms down"""

        print("Moving side arms...")
        if (status == "head"):
            self.robot.pumps_get(ids="1")  # Pump the pump 1
            sleep(0.5)
            self.robot.pumps_get(ids="3")  # Pump the pump 3
            sleep(0.5)
            self.robot.set_head_config(arm=1, config=1)  # Head down
            sleep(0.5)
            self.robot.set_head_config(arm=3, config=1)  # Head down
        elif (status == "elevator_down"):
            self.robot.set_elevator_config(arm=1, config=2)  # Head mid
            sleep(0.5)
            self.robot.set_elevator_config(arm=3, config=2)  # Head mid
        elif (status == "elevator_up"):
            self.robot.set_elevator_config(arm=1, config=0)  # Head up
            sleep(0.5)
            self.robot.set_elevator_config(arm=3, config=0)  # Head up
        else:
            print("Error: wrong status")
            exit(84)
        print(f"Done action : {status}")

    def drop_carrying(self):
        """Drop the carrying statuette"""
        self.robot.set_elevator_config(arm=2, config=2)  # Elevator to mid
        sleep(0.5)
        self.robot.set_head_config(arm=2, config=0)  # Head Closed
        sleep(0.5)
        self.robot.pumps_get(ids="2")  # Pump the pump 2
        sleep(0.5)
        self.robot.set_elevator_config(arm=2, config=5)  # Elevator to store statuette
        sleep(0.5)
        self.robot.set_head_config(arm=2, config=1)  # Head Down
        sleep(0.5)
        self.robot.set_elevator_config(arm=2, config=3)  # Elevator to mid
        sleep(0.5)
        self.robot.pumps_drop(ids="2")  # Drop the pumps
        print("Drop carrying : Done")

    def run_movement():
        # self = init_bot()

        self.robot.bumper_open()
        sleep(0.5)
        drop_carrying(self)  # Drop the carry statuette
        sleep(0.5)
        self.robot.set_elevator_config(arm=2, config=5)  # Elevator to store statuette
        sleep(0.5)
        self.robot.set_head_config(arm=2, config=2)  # Head to mid
        sleep(0.5)
        self.robot.set_elevator_config(arm=2, config=3)  # Elevator to mid
        sleep(0.5)
        self.robot.pumps_get(ids="2")  # Pump the pump 2
        sleep(0.5)
        self.trajman.move_trsl(acc=200, dec=200, dest=95, maxspeed=500, sens=1)  # Advance to 95
        sleep(0.5)
        status = self.robot.goto_avoid(x=default_x, y=default_y)
        if RobotStatus.get_status(status) != RobotStatus.Reached:
            return RobotStatus.return_status(RobotStatus.get_status(status))
        sleep(0.5)
        self.robot.set_elevator_config(arm=2, config=5)  # Elevator to store statuette
        sleep(0.5)
        self.robot.pumps_get(ids="4")  # Pump the pump 4
        sleep(0.5)
        self.robot.set_head_config(arm=2, config=0)  # Head up
        sleep(0.5)
        # self.robot.pumps_drop(ids = "2") # Drop the pumps
        sleep(0.5)
        self.robot.set_elevator_config(arm=2, config=3)  # Elevator to mid
        sleep(0.5)
        self.robot.set_head_config(arm=2, config=1)  # Head down
        sleep(0.5)
        self.robot.set_elevator_config(arm=2, config=0)  # Elevator to closed
        sleep(0.5)
        self.trajman.move_trsl(acc=200, dec=200, dest=100, maxspeed=500, sens=1)  # Advance to 100
        sleep(0.5)
        self.robot.pumps_get(ids="2")  # Pump the pump 2
        sleep(0.5)
        self.robot.set_elevator_config(arm=2, config=3)  # Elevator to gallery
        sleep(0.5)
        self.robot.set_elevator_config(arm=2, config=0)  # Elevator to closed
        sleep(0.5)
        self.robot.snowplow_open()
        sleep(0.5)
        self.trajman.move_trsl(acc=200, dec=200, dest=90, maxspeed=400, sens=1)  # Advance to 90
        sleep(0.5)
        self.robot.pumps_drop(ids="2")  # Drop the pump 2
        sleep(0.5)
        move_side_arms("head", self)
        sleep(0.5)
        move_side_arms("elevator_down", self)  # Activate arm movement func down
        sleep(0.5)
        move_side_arms("elevator_up", self)  # Activate arm movement func up
        sleep(0.5)
        status = self.robot.goto_avoid(x=default_x, y=default_y)
        if RobotStatus.get_status(status) != RobotStatus.Reached:
            return RobotStatus.return_status(RobotStatus.get_status(status))
        sleep(0.5)
        self.robot.snowplow_close()
        sleep(0.5)
        self.robot.bumper_close()
        sleep(0.5)
        print("Finished !")
