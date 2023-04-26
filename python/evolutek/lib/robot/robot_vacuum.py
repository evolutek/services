from robot_actions_imports import *

@if_enabled
@async_task
def turbine_on(self):
    return RobotStatus.return_status(RobotStatus.get_status(self.actuators.esc_set_speed(8, 0.1)))

@if_enabled
@async_task
def turbine_off(self):
    return RobotStatus.return_status(RobotStatus.get_status(self.actuators.esc_set_speed(8, 0)))

@if_enabled
@async_task
def extend_left_vacuum(self):
    return RobotStatus.return_status(RobotStatus.get_status(self.actuators.servo_set_angle(10, 83.6)))

@if_enabled
@async_task
def retract_left_vacuum(self):
    return RobotStatus.return_status(RobotStatus.get_status(self.actuators.servo_set_angle(10, 19.3)))

@if_enabled
@async_task
def extend_right_vacuum(self):
    return RobotStatus.return_status(RobotStatus.get_status(self.actuators.servo_set_angle(11, 96.4)))

@if_enabled
@async_task
def retract_right_vacuum(self):
    return RobotStatus.return_status(RobotStatus.get_status(self.actuators.servo_set_angle(11, 160.7)))
