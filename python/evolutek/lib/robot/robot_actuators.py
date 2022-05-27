from enum import Enum
from evolutek.lib.status import RobotStatus
from evolutek.lib.utils.color import Color
from evolutek.lib.utils.task import async_task
from evolutek.lib.utils.wrappers import if_enabled
from time import sleep
from evolutek.lib.actuators.i2c_acts import I2CActsHandler, I2CActType, ESCVariation
from evolutek.lib.actuators.ax12 import AX12Controller

def check_status(*args):
    for stat in args:
        if stat != RobotStatus.Done:
            return RobotStatus.return_status(RobotStatus.Failed)
    return RobotStatus.return_status(RobotStatus.Done)

@if_enabled
@async_task
def canon_on(self):
    status1 = RobotStatus.get_status(self.actuators.esc_set_speed(9, 0.45))
    status2 = RobotStatus.get_status(self.actuators.esc_set_speed(10, 0.45))
    return check_status(status1, status2)

@if_enabled
@async_task
def canon_off(self):
    status1 = RobotStatus.get_status(self.actuators.esc_set_speed(9, 0))
    status2 = RobotStatus.get_status(self.actuators.esc_set_speed(10, 0))
    return check_status(status1, status2)

@if_enabled
@async_task
def turbine_on(self):
    return RobotStatus.return_status(RobotStatus.get_status(self.actuators.esc_set_speed(8, 0.2)))

@if_enabled
@async_task
def turbine_off(self):
    return RobotStatus.return_status(RobotStatus.get_status(self.actuators.esc_set_speed(8, 0)))

@if_enabled
@async_task
def extend_left_vacuum(self):
    return RobotStatus.return_status(RobotStatus.get_status(self.actuators.servo_set_angle(2, 80)))

@if_enabled
@async_task
def retract_left_vacuum(self):
    return RobotStatus.return_status(RobotStatus.get_status(self.actuators.servo_set_angle(2, 25)))

@if_enabled
@async_task
def extend_right_vacuum(self):
    return RobotStatus.return_status(RobotStatus.get_status(self.actuators.servo_set_angle(3, 120)))

@if_enabled
@async_task
def retract_right_vacuum(self):
    return RobotStatus.return_status(RobotStatus.get_status(self.actuators.servo_set_angle(3, 175)))

@if_enabled
@async_task
def clamp_open(self):
    status1 = RobotStatus.get_status(self.actuators.servo_set_angle(0, 15))
    status2 = RobotStatus.get_status(self.actuators.servo_set_angle(1, 165))
    return check_status(status1, status2)

@if_enabled
@async_task
def clamp_open_half(self):
    status1 = RobotStatus.get_status(self.actuators.servo_set_angle(0, 30))
    status2 = RobotStatus.get_status(self.actuators.servo_set_angle(1, 150))
    return check_status(status1, status2)

@if_enabled
@async_task
def clamp_close(self):
    status1 = RobotStatus.get_status(self.actuators.servo_set_angle(0, 40))
    status2 = RobotStatus.get_status(self.actuators.servo_set_angle(1, 140))
    return check_status(status1, status2)

@if_enabled
@async_task
def push_canon(self):
    return RobotStatus.return_status(RobotStatus.get_status(self.actuators.servo_set_angle(4, 180)))

@if_enabled
@async_task
def push_tank(self):
    return RobotStatus.return_status(RobotStatus.get_status(self.actuators.servo_set_angle(4, 55)))

@if_enabled
@async_task
def push_isol(self):
    return RobotStatus.return_status(RobotStatus.get_status(self.actuators.servo_set_angle(4, 150)))

'''class ElevatorPosition(Enum):
    Low = (750, 180)
    GetSecond = (655, 305)
    DropSecond = (635, 325)
    GetThird = (605, 355)
    DropThird = (585, 375)
    GetFourth = (555, 405)
    High = (520, 450)

    @staticmethod
    def get_position(position):
        if isinstance(position, ElevatorPositions):
            return position
        try:
            return ElevatorPosition.__members__[positon]
        except:
            return None'''

ElevatorPosition = {
    "Low" : (717, 246),
    "GetSecond" : (632, 330),
    "DropSecond" : (572, 387),
    "GetThird" : (537, 423),
    "DropThird" : (479, 478),
    "GetFourth" : (427, 531),
    "High" : (193, 773)
}

@if_enabled
@async_task
def elevator_move(self, positon):
    position = ElevatorPosition[positon]
    status1 = RobotStatus.get_status(self.actuators.ax_move(1, position[0]))
    status2 = RobotStatus.get_status(self.actuators.ax_move(2, position[1]))
    return check_status(status1, status2) 
