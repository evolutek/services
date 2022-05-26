from evolutek.lib.robot.robot_action_imports import *


@if_enabled
@async_task
def collect_middle(self):

    #grab palets
        #set elevator to mid
    self.set_elevator_config(arm=1, config=2, async_task=False)
    self.set_elevator_config(arm=2, config=2, async_task=False)
    self.set_elevator_config(arm=3, config=2, async_task=False)
        #set head to down
    self.set_head_config(arm=1,  config=1, async_task=False)
    self.set_head_config(arm=2, config=1, async_task=False)
    self.set_head_config(arm=3, config=1, async_task=False)
        #move to palets with snowplow
    self.goto_avoid(700,730,theta=pi/2, async_task=False)
    self.snowplow_open(async_task=False)
    self.goto_avoid(700,1000,theta=pi/2, async_task=False)
    sleep(0.2)
        #set elevator to down
    self.set_elevator_config(arm=1, config=3, async_task=False)
    self.set_elevator_config(arm=2, config=3, async_task=False)
    self.set_elevator_config(arm=3, config=3, async_task=False)
    sleep(0.2)
        #activated pump
    self.pumps_get(ids="1", async_task=False)
    self.pumps_get(ids="2", async_task=False)
    self.pumps_get(ids="3", async_task=False)
        #close snowplot
    self.snowplow_close(async_task=False)
        #set elevator to galery (low)
    self.set_elevator_config(arm=1, config=3, async_task=False)
    self.set_elevator_config(arm=2, config=3, async_task=False)
    self.set_elevator_config(arm=3, config=3, async_task=False)
        #set head to galery
    self.set_head_config(arm=1,  config=3, async_task=False)
    self.set_head_config(arm=2, config=3, async_task=False)
    self.set_head_config(arm=3, config=3, async_task=False)

    #drop palets to galery
        #go to galery
    self.goto_avoid(200, 810, theta=pi, async_task=False)
    sleep(0.2)
    self.goto_avoid(102, 810, theta=pi, async_task=False)
        #drop into
    self.pumps_drop(ids="1", async_task=False)
    self.pumps_drop(ids="2", async_task=False)
    self.pumps_drop(ids="3", async_task=False)
        #go back
    self.goto_avoid(200, 810, theta=pi, async_task=False)
    sleep(0.2)


    return RobotStatus.return_status(RobotStatus.Done)


