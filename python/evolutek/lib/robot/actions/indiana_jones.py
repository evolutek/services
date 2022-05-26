from evolutek.lib.robot.robot_actions_imports import *


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
    self.set_elevator_config(arm=2, config=5, async_task=False)  # Elevator to store statuette
    self.set_head_config(arm=2, config=2, async_task=False)  # Head to mid
    self.set_elevator_config(arm=2, config=3, async_task=False)  # Elevator to mid
    self.pumps_get(ids="2", async_task=False)  # Pump the pump 2
    sleep(1)
    self.goth(theta=-pi/4, async_task=False)
    self.move_trsl(acc=200, dec=200, dest=100, maxspeed=500, sens=1)  # Advance to 100
    sleep(0.5)
    status = self.goto_avoid(x=default_x, y=default_y, async_task=False)
    #if RobotStatus.get_status(status) != RobotStatus.Reached:
    #   return RobotStatus.return_status(RobotStatus.get_status(status))
    self.set_elevator_config(arm=2, config=5, async_task=False)  # Elevator to store statuette
    self.pumps_get(ids="4", async_task=False)  # Pump the pump 4
    self.set_elevator_config(arm=2, config=5, async_task=False)
    self.set_head_config(arm=2, config=0, async_task=False)  # Head up
    sleep(1)
    self.pumps_drop(ids="2", async_task=False)
    sleep(0.1)
    self.set_elevator_config(arm=2, config=3, async_task=False)  # Elevator to mid
    sleep(0.2)
    self.set_head_config(arm=2, config=1, async_task=False)  # Head down
    sleep(1)
    self.set_elevator_config(arm=2, config=0, async_task=False)  # Elevator to closed
    sleep(0.2)
    self.pumps_get(ids="2", async_task=False)  # Pump the pump 2
    self.move_trsl(acc=240, dec=200, dest=100, maxspeed=500, sens=1)  # Advance to 120
    sleep(0.5)
    self.set_elevator_config(arm=2, config=3, async_task=False)  # Elevator to gallery
    sleep(0.5)
    self.set_elevator_config(arm=2, config=0, async_task=False)  # Elevator to closed
    self.snowplow_open(async_task=False)
    sleep(1)
    self.move_trsl(acc=200, dec=200, dest=100, maxspeed=400, sens=1)  # Advance to 100
    sleep(1)
    self.pumps_drop(ids="2", async_task=False)  # Drop the pump 2
    sleep(1)
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