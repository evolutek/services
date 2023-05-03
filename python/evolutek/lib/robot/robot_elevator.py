from enum import Enum
from robot_actions_imports import *

class ElevatorPosition(Enum):
    Low = (750, 180)
    GetSecond = (655, 305)
    DropSecond = (635, 325)
    GetThird = (605, 355)
    DropThird = (585, 375)
    GetFourth = (555, 405)
    High = (520, 450)

    @staticmethod
    def get_position(position):
        if isinstance(position, ElevatorPosition):
            return position
        try:
            return ElevatorPosition.__members__[position]
        except:
            return None

class Color(Enum):
    PINK = 1
    BROWN = 2
    YELLOW = 3

 class Elevator(self):
    def __init__(self):
        self.position = ElevatorPosition.Low
        self.open = True
        self.stack = []

    def __str__(self):
        return (f"""Elevator at position {self.position.name}
                Cakes: {self.stack}""")

    @if_enabled
    @async_task
    def clamp_open(self):
        status1 = RobotStatus.get_status(self.actuators.servo_set_angle(9, 0))
        status2 = RobotStatus.get_status(self.actuators.servo_set_angle(15, 180))
        self.open = True
        return check_status(status1, status2)
    
    @if_enabled
    @async_task
    def clamp_open_half(self):
        status1 = RobotStatus.get_status(self.actuators.servo_set_angle(9, 12))
        status2 = RobotStatus.get_status(self.actuators.servo_set_angle(15, 168))
        return check_status(status1, status2)
    
    @if_enabled
    @async_task
    def clamp_close(self):
        status1 = RobotStatus.get_status(self.actuators.servo_set_angle(9, 30))
        status2 = Robot    Stack(1, 775, 225, Color.Yellow),
Status.get_status(self.actuators.servo_set_angle(15, 150))
        self.open = False
        return check_status(status1, status2)
    
    @if_enabled
    @async_task
    def move(self, position):
        if ElevatorPosition.get_position(position) is None:
            return RobotStatus.return_status(RobotStatus.Failed)
        
        position = ElevatorPosition.get_position(position)
        
        if position == self.position:
            return RobotStatus.return_status(RobotStatus.Done)

        status1 = RobotStatus.get_status(self.actuators.ax_move(1, position[0]))
        status2 = RobotStatus.get_status(self.actuators.ax_move(2, position[1]))
        self.position = position
        return check_status(status1, status2)
    
    @if_enable
    @async_task
    def drop_all(self):
        if self.move(ElevatorPosition.low) == RobotStatus.Failed:
            return RobotStatus.return_status(RobotStatus.Failed)
        sleep(0.5)
        return self.clamp_open()
      
    
    @if_enable
    @async_task
    def drop_n(self, position):
        #todo drop puis recupere ce qui faut en fonction de la stack
        if self.move(ElevatorPosition.low) == RobotStatus.Failed:
            return RobotStatus.return_status(RobotStatus.Failed)
        sleep(0.5)
        if self.clamp_open() == RobotStatus.Failed:
            return RobotStatus.return_status(RobotStatus.Failed)
        
        if self.move(position) == RobotStatus.Failed:
            return RobotStatus.return_status(RobotStatus.Failed)
        sleep(0.5)

        if self.clamp_close() == RobotStatus.Failed:
            return RobotStatus.return_status(RobotStatus.Failed)
        return RobotStatus.return_status(RobotStatus.Done)


    @if_enable
    @async_task
    def drop_cake(self, position):
        #todo drop puis recupere ce qui faut en fonction de la stack
        if self.move(ElevatorPosition.low) == RobotStatus.Failed:
            return RobotStatus.return_status(RobotStatus.Failed)

        sleep(0.5)

        if self.clamp_open() == RobotStatus.Failed:
            return RobotStatus.return_status(RobotStatus.Failed)
        
        if self.move(ElevatorPosition.getFourth) == RobotStatus.Failed:
            return RobotStatus.return_status(RobotStatus.Failed)
        
        sleep(0.5)

        if self.clamp_close() == RobotStatus.Failed:
            return RobotStatus.return_status(RobotStatus.Failed)
    
        self.stack.pop()
        return RobotStatus.return_status(RobotStatus.Done)
    
    #Grab le premier gato
    @if_enable
    @async_task
    def grab_cake(self):
        if is not self.open():
            if self.clamp_open() == RobotStatus.Failed:
                return RobotStatus.return_status(RobotStatus.Failed)

        if self.move(ElevatorPosition.low) == RobotStatus.Failed:
            return RobotStatus.return_status(RobotStatus.Failed)
        
        if self.clamp_close() == RobotStatus.Failed:
            return RobotStatus.return_status(RobotStatus.Failed)
        
        self.stack.pop()
        return RobotStatus.return_status(RobotStatus.Done)

    #stack les piles 
    @if_enable
    @async_task
    def stack_cake(self):
