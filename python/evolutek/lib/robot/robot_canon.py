from robot_actions_imports import *

@if_enabled
@async_task
def canon_on(self):
    status1 = RobotStatus.get_status(self.actuators.esc_set_speed(13, 0.35))
    status2 = RobotStatus.get_status(self.actuators.esc_set_speed(14, 0.35))
    return check_status(status1, status2)

@if_enabled
@async_task
def canon_off(self):
    status1 = RobotStatus.get_status(self.actuators.esc_set_speed(13, 0))
    status2 = RobotStatus.get_status(self.actuators.esc_set_speed(14, 0))
    return check_status(status1, status2)

@if_enabled
@async_task
def push_canon(self):
    return RobotStatus.return_status(RobotStatus.get_status(self.actuators.servo_set_angle(12, 180)))

@if_enabled
@async_task
def push_tank(self):
    return RobotStatus.return_status(RobotStatus.get_status(self.actuators.servo_set_angle(12, 51.4)))

@if_enabled
@async_task
def push_drop(self):
    return RobotStatus.return_status(RobotStatus.get_status(self.actuators.servo_set_angle(12, 172)))
