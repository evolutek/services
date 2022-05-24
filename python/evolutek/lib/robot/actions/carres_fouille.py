from evolutek.lib.robot.robot_actions_imports import *
from evolutek.lib.utils.boolean import get_boolean

@if_enabled
@async_task
def broom_square(self):
    #Go next to the square
    self.goto_avoid(x = 1000, y = 1340, async_task = False)
    self.goth(theta = 0, async_task = False)
    #Go in front of the square
    self.goto_avoid(x = 1360, y = 1340, async_task = False)
    self.goth(theta = -pi/2, async_task = False)
    #Open Snowplow
    self.snowplow_open(async_task = False)
    #Set speed to slow
    self.trajman.set_trsl_max_speed(200)
    #Advance to push the samples
    self.goto_avoid(x = 1360, y = 510, async_task = False)
    #Set middle head to down
    self.set_head_config(arm = 2, config = HeadConfig.Down, async_task = False)
    #Set elevator to down
    self.set_elevator_config(arm = 2, config = ElevatorConfig.Mid, async_task = False)
    sleep(1)
    #Check proximity sensor -> if good continue
    #                       -> if not : fuck
    # if (get_boolean(self.actuators.proximity_sensor_read(id = 2))):
    #     self.pumps_get(ids = "2", async_task = False)
    # else:
    #     return
    self.pumps_get(ids = "2", async_task = False)
    # Set elevator to close
    self.set_elevator_config(arm = 2, config = 0, async_task = False)
    # Set head to pickup
    self.set_head_config(arm = 2, config = 4, async_task = False)
    # Go to indiana pos
    self.goto_avoid(x = 1550, y = 450, asyn_task = False)
    self.goth(theta = -pi / 4, async_task = False)


    #Set speed back to normal
    self.trajman.set_trsl_max_speed(600)
