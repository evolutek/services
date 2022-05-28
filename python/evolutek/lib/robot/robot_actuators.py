from enum import Enum
from evolutek.lib.status import RobotStatus
from evolutek.lib.utils.color import Color
from evolutek.lib.utils.task import async_task
from evolutek.lib.utils.wrappers import if_enabled
from time import sleep
from evolutek.lib.actuators.i2c_acts import I2CActsHandler, I2CActType, ESCVariation
from evolutek.lib.actuators.ax12 import AX12Controller

@if_enabled
@async_task
def canon_on(self, power=100):
    power = float(power)
    speed = min(0.6, max(0.1, 0.3 * power / 100))
    status1 = self.actuators.esc_set_speed(9, speed)
    status2 = self.actuators.esc_set_speed(10, speed)
    return RobotStatus.check(status1, status2)

@if_enabled
@async_task#
def canon_off(self):
    status1 = self.actuators.esc_set_speed(9, 0)
    status2 = self.actuators.esc_set_speed(10, 0)
    return RobotStatus.check(status1, status2)

@if_enabled
@async_task
def turbine_on(self):
    return RobotStatus.check(self.actuators.esc_set_speed(8, 0.16 if self.service_name == "pal" else 0.19))

@if_enabled
@async_task
def turbine_off(self):
    return RobotStatus.check(self.actuators.esc_set_speed(8, 0))

@if_enabled
@async_task
def extend_left_vacuum(self):
    return RobotStatus.check(self.actuators.servo_set_angle(2, 90))

@if_enabled
@async_task
def retract_left_vacuum(self):
    return RobotStatus.check(self.actuators.servo_set_angle(2, 25))

@if_enabled
@async_task
def extend_right_vacuum(self):
    return RobotStatus.check(self.actuators.servo_set_angle(3, 90 if self.service_name == "pmi" else 86))

@if_enabled
@async_task
def retract_right_vacuum(self):
    return RobotStatus.check(self.actuators.servo_set_angle(3, 175))

@if_enabled
@async_task
def clamp_open(self):
    status1 = self.actuators.servo_set_angle(0, 15)
    status2 = self.actuators.servo_set_angle(1, 165)
    return RobotStatus.check(status1, status2)

@if_enabled
@async_task
def clamp_open_half(self):
    status1 = self.actuators.servo_set_angle(0, 30)
    status2 = self.actuators.servo_set_angle(1, 150)
    return RobotStatus.check(status1, status2)

@if_enabled
@async_task
def clamp_untight(self):
    status1 = self.actuators.servo_set_angle(0, 34)
    status2 = self.actuators.servo_set_angle(1, 146)
    return RobotStatus.check(status1, status2)

@if_enabled
@async_task
def clamp_close(self):
    status1 = self.actuators.servo_set_angle(0, 40)
    status2 = self.actuators.servo_set_angle(1, 140)
    return RobotStatus.check(status1, status2)

@if_enabled
@async_task
def push_canon(self):
    return RobotStatus.check(self.actuators.servo_set_angle(4, 180))

@if_enabled
@async_task
def push_tank(self):
    return RobotStatus.check(self.actuators.servo_set_angle(4, 50))

# @if_enabled
# @async_task
# def drop_slow(self):
#     self.actuators.servo_set_angle(4, 180)
#     sleep(0.4)
#     for i in range(180, 50, -1):
#         self.actuators.servo_set_angle(4, i)
#         sleep(0.015)
#     return RobotStatus.check(self.actuators.servo_set_angle(4, 50))

@if_enabled
@async_task
def push_isol(self):
    self.push_canon(async_task=False)
    sleep(0.4)
    return RobotStatus.check(self.actuators.servo_set_angle(4, 155 if self.service_name == "pmi" else 168))

@if_enabled
@async_task
def disguise_on(self):
    return RobotStatus.check(self.actuators.orange_led_strip_set(True))

@if_enabled
@async_task
def disguise_off(self):
    return RobotStatus.check(self.actuators.orange_led_strip_set(False))

ElevatorPosition = {
    "Low" : (717, 246),
    "GetSecond" : (624, 338),
    "DropSecond" : (572, 387),
    "GetThird" : (530, 430),
    "DropThird" : (479, 478),
    "GetFourth" : (420, 538),
    "High" : (193, 773)
}

@if_enabled
@async_task
def elevator_move(self, positon):
    position = ElevatorPosition[positon]
    status1 = self.actuators.ax_move(1, position[0])
    status2 = self.actuators.ax_move(2, position[1])
    self.elevator_status = positon
    return RobotStatus.check(status1, status2)
