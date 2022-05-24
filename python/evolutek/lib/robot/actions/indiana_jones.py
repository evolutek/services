from evolutek.lib.robot.robot_actions_imports import *
from evolutek.lib.utils.boolean import get_boolean


def drop_carrying(self):
    """Drop the carrying statuette"""
    has_dropped = pickup_statuette(self)
    self.set_head_config(arm=FrontArmsEnum.Center, config=HeadConfig.Down, async_task=False)  # Head Down
    self.set_elevator_config(arm=FrontArmsEnum.Center, config=ElevatorConfig.Mid, async_task=False)  # Elevator to mid
    sleep(0.5)
    self.pumps_drop(ids="2", async_task=False)  # Drop the pumps
    sleep(0.5)
    self.set_elevator_speed(arm=FrontArmsEnum.Center, speed=20, async_task=False)
    self.set_elevator_config(arm=FrontArmsEnum.Center, config=ElevatorConfig.StoreStatuette, async_task=False)  # Elevator to mid
    sleep(0.5)
    self.set_elevator_speed(arm=FrontArmsEnum.Center, speed=ElevatorSpeed.Default, async_task=False)
    self.stop_evs(ids="2", async_task=False)
    return has_dropped

def move_side_arms(status, self):
    """Move the side arms to the right position
    -head     : move the head of the arms
    -elevator_down : move the elevation of the arms down"""

    if (status == "head"):
        self.pumps_get(ids="1", async_task=False)  # Pump the pump 1
        self.pumps_get(ids="3", async_task=False)  # Pump the pump 3
        self.set_head_config(arm=FrontArmsEnum.Right, config=HeadConfig.Down, async_task=False)  # Head down
        self.set_head_config(arm=FrontArmsEnum.Left, config=HeadConfig.Down, async_task=False)  # Head down
    elif (status == "elevator_down"):
        self.set_elevator_config(arm=FrontArmsEnum.Right, config=ElevatorConfig.Mid, async_task=False)  # Head mid
        self.set_elevator_config(arm=FrontArmsEnum.Left, config=ElevatorConfig.Mid, async_task=False)  # Head mid
    elif (status == "elevator_up"):
        self.set_elevator_config(arm=FrontArmsEnum.Right, config=ElevatorConfig.Closed, async_task=False)  # Head up
        self.set_elevator_config(arm=FrontArmsEnum.Left, config=ElevatorConfig.Closed, async_task=False)  # Head up
    else:
        print("Error: wrong status")
    print(f"Done action : {status}")


@if_enabled
@async_task
def indiana_jones(self):
    def cleanup():
        print("\n\n\n\n\nCLEANUP\n\n\n\n\n")
        self.bumper_close(async_task=False)
        self.set_elevator_config(arm=FrontArmsEnum.Center, config=ElevatorConfig.Closed, async_task=False)
        self.set_head_config(arm=FrontArmsEnum.Center, config=HeadConfig.Closed, async_task=False)
        self.set_elevator_config(arm=FrontArmsEnum.Right, config=ElevatorConfig.Closed, async_task=False)
        sleep(0.1)
        self.set_head_config(arm=FrontArmsEnum.Right, config=HeadConfig.Closed, async_task=False)
        self.set_elevator_config(arm=FrontArmsEnum.Left, config=ElevatorConfig.Closed, async_task=False)
        self.set_head_config(arm=FrontArmsEnum.Left, config=HeadConfig.Closed, async_task=False)
        self.pumps_drop(ids="1", async_task=False)
        self.pumps_drop(ids="2", async_task=False)
        self.pumps_drop(ids="3", async_task=False)
        self.pumps_drop(ids="4", async_task=False)
        self.set_head_speed(arm=FrontArmsEnum.Center, speed=HeadSpeed.Default, async_task=False)
        self.snowplow_close(async_task=False)
    default_x = 1550
    default_y = 450
    default_angle = (5 * pi) / 4
    score = 0

    """

    TODO:
    Compter les points correctement

    """

    self.bumper_open(async_task=False)
    has_dropped = drop_carrying(self)  # Drop the carry statuette
    self.set_elevator_config(arm=FrontArmsEnum.Center, config=ElevatorConfig.StoreStatuette, async_task=False)  # Elevator to store statuette
    self.set_head_config(arm=FrontArmsEnum.Center, config=HeadConfig.Mid, async_task=False)  # Head to mid
    self.set_elevator_config(arm=FrontArmsEnum.Center, config=ElevatorConfig.GaleryLow, async_task=False)  # Elevator to mid
    self.pumps_get(ids="2", async_task=False)  # Pump the pump 2
    sleep(1)
    status = self.goto_avoid(x=1620, y=375, async_task=False, timeout=10)
    if RobotStatus.get_status(status) != RobotStatus.Reached:
        cleanup()
        return RobotStatus.return_status(RobotStatus.get_status(status))
    sleep(0.5)
    status = self.goto_avoid(x=default_x, y=default_y, async_task=False, timeout=10)
    if RobotStatus.get_status(status) != RobotStatus.Reached:
        cleanup()
        return RobotStatus.return_status(RobotStatus.get_status(status))
    score += (5 if get_boolean(self.actuators.proximity_sensor_read(id = 2)) else 0)
    self.set_head_speed(arm=FrontArmsEnum.Center, speed=HeadSpeed.VeryLow, async_task=False) # Reduce speed
    self.pumps_get(ids="4", async_task=False)  # Pump the pump 4
    self.set_elevator_config(arm=FrontArmsEnum.Center, config=ElevatorConfig.StoreStatuette, async_task=False)
    self.set_head_config(arm=FrontArmsEnum.Center, config=HeadConfig.StoreStatuette, async_task=False)  # Head up
    sleep(1.5)
    self.set_head_speed(arm=FrontArmsEnum.Center, speed=HeadSpeed.Default, async_task=False) # Reduce speed
    score += (10 if get_boolean(self.actuators.proximity_sensor_read(id = 2)) else 0)
    self.pumps_drop(ids="2", async_task=False)
    sleep(0.1)
    self.set_elevator_config(arm=FrontArmsEnum.Center, config=ElevatorConfig.GaleryLow, async_task=False)  # Elevator to mid
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
    status = self.goto_avoid(x=1400, y=600, async_task=False, timeout=10)
    if RobotStatus.get_status(status) != RobotStatus.Reached:
        cleanup()
        return RobotStatus.return_status(RobotStatus.get_status(status))
    self.snowplow_close(async_task=False)
    self.bumper_close(async_task=False)

    return RobotStatus.return_status(RobotStatus.Done, score = score)
