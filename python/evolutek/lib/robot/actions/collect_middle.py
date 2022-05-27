from evolutek.lib.robot.robot_actions_imports import *
from evolutek.lib.utils.boolean import get_boolean


def cleanup(self):
    self.set_elevator_config(arm=FrontArmsEnum.Left,   config=ElevatorConfig.Mid, async_task=False)
    self.set_elevator_config(arm=FrontArmsEnum.Center, config=ElevatorConfig.Mid, async_task=False)
    self.set_elevator_config(arm=FrontArmsEnum.Right,  config=ElevatorConfig.Mid, async_task=False)
    self.set_head_config(arm=FrontArmsEnum.Left,   config=HeadConfig.Closed, async_task=False)
    self.set_head_config(arm=FrontArmsEnum.Center, config=HeadConfig.Closed, async_task=False)
    self.set_head_config(arm=FrontArmsEnum.Right,  config=HeadConfig.Closed, async_task=False)
    self.set_elevator_speed(arm=FrontArmsEnum.Left, speed=ElevatorSpeed.Default, async_task=False)
    self.set_elevator_speed(arm=FrontArmsEnum.Center, speed=ElevatorSpeed.Default, async_task=False)
    self.set_elevator_speed(arm=FrontArmsEnum.Right, speed=ElevatorSpeed.Default, async_task=False)
    self.set_head_speed(arm=FrontArmsEnum.Left, speed=HeadSpeed.Default, async_task=False)
    self.set_head_speed(arm=FrontArmsEnum.Center, speed=HeadSpeed.Default, async_task=False)
    self.set_head_speed(arm=FrontArmsEnum.Right, speed=HeadSpeed.Default, async_task=False)
    sleep(0.5)


@if_enabled
@async_task
def collect_middle(self):
    score = 0
    flip = 1 #put 2 if flip else 1

    # Grab palets
    self.set_elevator_config(arm=FrontArmsEnum.Left,   config=ElevatorConfig.Mid, async_task=False)
    self.set_elevator_config(arm=FrontArmsEnum.Center, config=ElevatorConfig.Mid, async_task=False)
    self.set_elevator_config(arm=FrontArmsEnum.Right,  config=ElevatorConfig.Mid, async_task=False)
    self.set_head_config(arm=FrontArmsEnum.Left,   config=HeadConfig.Down, async_task=False)
    self.set_head_config(arm=FrontArmsEnum.Center, config=HeadConfig.Down, async_task=False)
    self.set_head_config(arm=FrontArmsEnum.Right,  config=HeadConfig.Down, async_task=False)

    # Move to palets with snowplow
    status = RobotStatus.get_status(self.goth(theta=pi/2, async_task=False))
    if status == RobotStatus.Reached:
        status = RobotStatus.get_status(self.goto_avoid(675, 640, async_task=False, timeout=10))
        if status == RobotStatus.Reached:
            status = RobotStatus.get_status(self.goth(theta=pi/2, async_task=False))
            if status == RobotStatus.Reached:
                self.snowplow_open(async_task=False)
                speed = self.trajman.get_speeds()['trmax']
                self.trajman.set_trsl_max_speed(80)
                status = RobotStatus.get_status(self.goto_avoid(675, 820, async_task=False, timeout=10))
                if status == RobotStatus.Reached:
                    self.goto_avoid(675, 815, async_task=False)
                self.trajman.set_trsl_max_speed(speed)
                sleep(0.2)
    
    if status != RobotStatus.Reached:
        cleanup(self)
        return RobotStatus.return_status(status, score=score)

    # Set elevator to down
    self.set_elevator_config(arm=FrontArmsEnum.Left,   config=ElevatorConfig.Down, async_task=False)
    self.set_elevator_config(arm=FrontArmsEnum.Center, config=ElevatorConfig.Down, async_task=False)
    self.set_elevator_config(arm=FrontArmsEnum.Right,  config=ElevatorConfig.Down, async_task=False)
    sleep(0.2)
    
    # Activated pump
    self.pumps_get(ids="1,2,3", async_task=False)
    sleep(1)

    # Change speed of elevator and head
    self.set_elevator_speed(arm=FrontArmsEnum.Left, speed=ElevatorSpeed.WithSample, async_task=False)
    self.set_elevator_speed(arm=FrontArmsEnum.Center, speed=ElevatorSpeed.WithSample, async_task=False)
    self.set_elevator_speed(arm=FrontArmsEnum.Right, speed=ElevatorSpeed.WithSample, async_task=False)
    self.set_head_speed(arm=FrontArmsEnum.Left, speed=HeadSpeed.WithSample, async_task=False)
    self.set_head_speed(arm=FrontArmsEnum.Center, speed=HeadSpeed.WithSample, async_task=False)
    self.set_head_speed(arm=FrontArmsEnum.Right, speed=HeadSpeed.WithSample, async_task=False)

    # Set arms in the correct position for placing
    self.set_elevator_config(arm=FrontArmsEnum.Left,   config=ElevatorConfig.GaleryLow, async_task=False)
    self.set_elevator_config(arm=FrontArmsEnum.Center, config=ElevatorConfig.GaleryLow, async_task=False)
    self.set_elevator_config(arm=FrontArmsEnum.Right,  config=ElevatorConfig.GaleryLow, async_task=False)
    sleep(0.5)
    self.set_elevator_config(arm=FrontArmsEnum.Left,   config=ElevatorConfig.Mid, async_task=False)
    self.set_elevator_config(arm=FrontArmsEnum.Center, config=ElevatorConfig.Mid, async_task=False)
    self.set_elevator_config(arm=FrontArmsEnum.Right,  config=ElevatorConfig.Mid, async_task=False)
    self.set_head_config(arm=FrontArmsEnum.Left,   config=HeadConfig.Galery, async_task=False)
    self.set_head_config(arm=FrontArmsEnum.Center, config=HeadConfig.Galery, async_task=False)
    self.set_head_config(arm=FrontArmsEnum.Right,  config=HeadConfig.Galery, async_task=False)
    sleep(1)

    # Check score
    score += (3 if get_boolean(self.actuators.proximity_sensor_read(id = 1)) else 0) * flip
    score += (3 if get_boolean(self.actuators.proximity_sensor_read(id = 2)) else 0) * flip
    score += (3 if get_boolean(self.actuators.proximity_sensor_read(id = 3)) else 0) * flip
    
    # Close snowplow
    self.snowplow_close(async_task=False)

    # Go to galery
    self.goto_avoid(250, 920, async_task=False)
    self.goth(pi, async_task=False)
    self.goto_avoid(190, 920, async_task=False, timeout=10)
    if status != RobotStatus.Reached:
        cleanup(self)
        return RobotStatus.return_status(status, score=score)

    # Drop palets to galery
    self.pumps_drop(ids="1,2,3", async_task=False)

    # Go back
    self.goto_avoid(320, 920, async_task=False, timeout=10)
    if status != RobotStatus.Reached:
        cleanup(self)
        return RobotStatus.return_status(status, score=score)

    # Cleanup
    cleanup(self)

    return RobotStatus.return_status(RobotStatus.Done,score=score)


