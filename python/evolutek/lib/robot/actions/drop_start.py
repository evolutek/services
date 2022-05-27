from evolutek.lib.robot.robot_actions_imports import *


@if_enabled
@async_task
def drop_start(self):
    print("\n\n\n1")
    self.goto_avoid(380,225, async_task=False)
    print("\n\n\n2")
    self.goth(theta=0, async_task=False)
    print("\n\n\n3")

    scor = 0
    print("\n\n\n4")
    sensors = self.actuators.proximity_sensors.read_all_sensors()
    print("\n\n\n5")
    scor += sensors[0] + sensors[2]
    print("\n\n\n6")


    self.pumps_drop(ids="1", async_task=False)
    print("\n\n\n7")
    self.pumps_drop(ids="3", async_task=False)
    print("\n\n\n8")

    return RobotStatus.return_status(RobotStatus.Done, score=scor)
