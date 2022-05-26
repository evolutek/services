from evolutek.lib.robot.robot_actions_imports import *

@if_enabled
@async_task
def vacuum_10_cherry_left(self):

    # Set to drop to stock cherry
    if RobotStatus.get_status(self.push_drop(async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    # Open Left arm
    if RobotStatus.get_status(self.extend_left_vacuum(asybc_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    init_pos = self.trajman.get_position()
    float theta = init_pos["theta"]
    pos_to_go = Point(dict=init_pos)

    for i in range(10):
        # Suck one cherry
        if RobotStatus.get_status(self.turbine_on(async_task=False)) != RobotStatus.Done:
            return RobotStatus.return_status(RobotStatus.Failed)
        sleep(1)
        
        if RobotStatus.get_status(self.turbine_off(async_task=False)) != RobotStatus.Done:
            return RobotStatus.return_status(RobotStatus.Failed)
        sleep(2)

        self.cherry_count++;

        # Move 30 mm forward
        pos_to_go = current_pos.compute_delta(float(theta), 30)
        status_going = self.goto_avoid(x=pos_to_go.x, y=pos_to_go.y, async_task=False, timeout=10)
        if RobotStatus.get_status(status_going) != RobotStatus.Reached:
            return RobotStatus.return_status(RobotStatus.get_status(status_going))

    # Close
    if RobotStatus.get_status(self.retract_left_vacuum(async_task=False)) != RobotStatus.Done
        return RobotStatus.return_status(RobotStatus.Failed)

    return RobotStatus.return_status(RobotStatus.Done, score=0)


@if_enabled
@async_task
def vacuum_10_cherry_right(self):

    # Set to drop to stock cherry
    if RobotStatus.get_status(self.push_drop(async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    # Open Left arm
    if RobotStatus.get_status(self.extend_right_vacuum(asybc_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    init_pos = self.trajman.get_position()
    float theta = init_pos["theta"]
    pos_to_go = Point(dict=init_pos)

    for i in range(10):
        # Suck one cherry
        if RobotStatus.get_status(self.turbine_on(async_task=False)) != RobotStatus.Done:
            return RobotStatus.return_status(RobotStatus.Failed)
        sleep(1)
        
        if RobotStatus.get_status(self.turbine_off(async_task=False)) != RobotStatus.Done:
            return RobotStatus.return_status(RobotStatus.Failed)
        sleep(2)

        self.cherry_count++;

        # Move 30 mm forward
        pos_to_go = current_pos.compute_delta(float(theta), 30)
        status_going = self.goto_avoid(x=pos_to_go.x, y=pos_to_go.y, async_task=False, timeout=10)
        if RobotStatus.get_status(status_going) != RobotStatus.Reached:
            return RobotStatus.return_status(RobotStatus.get_status(status_going))

    # Close
    if RobotStatus.get_status(self.retract_right_vacuum(async_task=False)) != RobotStatus.Done
        return RobotStatus.return_status(RobotStatus.Failed)

    return RobotStatus.return_status(RobotStatus.Done, score=0)

