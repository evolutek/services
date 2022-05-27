from evolutek.lib.robot.robot_actions_imports import *


@if_enabled
@async_task
def collect_middle(self):
    flip = 1 #put 2 if flip else 1
    #grab palets
    self.set_elevator_config(arm=1, config=ElevatorConfig.Mid, async_task=False)
    self.set_elevator_config(arm=2, config=ElevatorConfig.Mid, async_task=False)
    self.set_elevator_config(arm=3, config=ElevatorConfig.Mid, async_task=False)
    self.set_head_config(arm=1, config=HeadConfig.Down, async_task=False)
    self.set_head_config(arm=2, config=HeadConfig.Down, async_task=False)
    self.set_head_config(arm=3, config=HeadConfig.Down, async_task=False)

        #move to palets with snowplow
    self.goth(theta=pi/2, async_task=False)
    self.goto_avoid(675,600, async_task=False, timeout=10)
    self.goth(theta=pi/2, async_task=False)
    self.snowplow_open(async_task=False)
    self.goto_avoid(675,850, async_task=False, timeout=10)
    sleep(0.2)
        #set elevator to down
    self.set_elevator_config(arm=1, config=ElevatorConfig.Down, async_task=False)
    self.set_elevator_config(arm=2, config=ElevatorConfig.Down, async_task=False)
    self.set_elevator_config(arm=3, config=ElevatorConfig.Down, async_task=False)
    sleep(0.2)
        #activated pump
    self.pumps_get(ids="1", async_task=False)
    self.pumps_get(ids="2", async_task=False)
    self.pumps_get(ids="3", async_task=False)
    sleep(1)

    self.set_elevator_config(arm=1, config=ElevatorConfig.Mid, async_task=False)
    self.set_elevator_config(arm=2, config=ElevatorConfig.Mid, async_task=False)
    self.set_elevator_config(arm=3, config=ElevatorConfig.Mid, async_task=False)
    self.set_head_config(arm=1, config=HeadConfig.Galery, async_task=False)
    self.set_head_config(arm=2, config=HeadConfig.Galery, async_task=False)
    self.set_head_config(arm=3, config=HeadConfig.Galery, async_task=False)

    #drop palets to galery
        #go to galery
    self.goto_avoid(320, 810, async_task=False, timeout=10)
    self.snowplow_close(async_task=False)

    self.goth(theta=pi, async_task=False)
    self.goto_avoid(190, 810, async_task=False, timeout=10)
        #score
    score = 0
    for e in self.actuators.proximity_sensor_read():
        score += e*flip*3
        #drop into
    self.pumps_drop(ids="1", async_task=False)
    self.pumps_drop(ids="2", async_task=False)
    self.pumps_drop(ids="3", async_task=False)
        #go back
    self.goto_avoid(320, 810, async_task=False, timeout=10)

        #reset arms
    self.set_elevator_config(arm=1, config=ElevatorConfig.Mid, async_task=False)
    self.set_elevator_config(arm=2, config=ElevatorConfig.Mid, async_task=False)
    self.set_elevator_config(arm=3, config=ElevatorConfig.Mid, async_task=False)
    self.set_head_config(arm=1, config=HeadConfig.Down, async_task=False)
    self.set_head_config(arm=2, config=HeadConfig.Down, async_task=False)
    self.set_head_config(arm=3, config=HeadConfig.Down, async_task=False)

    return RobotStatus.return_status(RobotStatus.Done,score=score)


