from enum import Enum
from evolutek.lib.status import RobotStatus
from evolutek.lib.utils.task import async_task
from evolutek.lib.utils.wrappers import if_enabled

#########
# PUMPS #
#########

def mirror_pump_id(self, id):
    if not self.side:
        if id in [1,3]:
            id = 4 - id
    return id

@if_enabled
@async_task
def pumps_get(self, ids, mirror=True):
    if isinstance(ids, str):
        ids = ids.split(",")

    if isinstance(mirror, str):
        mirror = mirror == 'true'

    _ids = []
    for id in ids:
        _ids.append(self.mirror_pump_id(int(id)) if mirror else int(id))
    if 1 in _ids: _ids.append(3)
    if 4 in _ids: _ids.append(5)

    return self.actuators.pumps_get(_ids)

@if_enabled
@async_task
def pumps_drop(self, ids, mirror=True):
    if isinstance(ids, str):
        ids = ids.split(",")

    if isinstance(mirror, str):
        mirror = mirror == 'true'

    _ids = []
    for id in ids:
        _ids.append(self.mirror_pump_id(int(id)) if mirror else int(id))
    if 1 in _ids: _ids.append(3)
    if 4 in _ids: _ids.append(5)

    return self.actuators.pumps_drop(_ids)

#############
# FRONT ARM #
#############

@if_enabled
@use_queue
def snowplow_open(self):
    self.actuators.servo_set_angle(0, 0)
    self.actuators.servo_set_angle(15, 120)

@if_enabled
@use_queue
def snowplow_close(self):
    self.actuators.servo_set_angle(0, 120)
    self.actuators.servo_set_angle(15, 0)

@if_enabled
@use_queue
def bumper_open(self):
    self.actuators.servo_set_angle(1, 0)
    self.actuators.servo_set_angle(14, 98)

@if_enabled
@use_queue
def bumper_close(self):
    self.actuators.servo_set_angle(1, 98)
    self.actuators.servo_set_angle(14, 0)

# Front Arm Close
@if_enabled
@use_queue
def front_arm_close(self):
    self.actuators.ax_set_speed(1, 256)
    res = self.actuators.ax_move(1, 512)
    self.actuators.pumps_drop([3,5])
    return res

# Front Arm Open
@if_enabled
@use_queue
def front_arm_open(self):
    self.actuators.ax_set_speed(1, 800)
    return self.actuators.ax_move(7, 290)

#############
# SIDE ARMS #
#############

# Left Arm Close
@if_enabled
@use_queue
def left_arm_close(self):
    return self.actuators.ax_move(8, 512)

# Left Arm Open
@if_enabled
@use_queue
def left_arm_open(self):
    return self.actuators.ax_move(8, 755)

# Right Arm Close
@if_enabled
@use_queue
def right_arm_close(self):
    return self.actuators.ax_move(7, 512)

# Right Arm Open
@if_enabled
@use_queue
def right_arm_open(self):
    return self.actuators.ax_move(3, 512)

##############
# FRONT ARMS #
##############

class FrontArmsEnum(Enum):
    Right = 1
    Center = 2
    Left = 3

    @staticmethod
    def get_arm(arm_number):
        if isinstance(arm_number, FrontArmsEnum):
            return arm_number
        if isinstance(arm_number, str):
            arm_number = int(arm_number)
        try:
            return FrontArmsEnum(arm_number)
        except:
            return None

    def get_head_id(self):
        return self.value * 2 - 1

    def get_elevator_id(self):
        return self.value * 2

class HeadSpeed(Enum):
    Default = 1023
    With Statuette = 512
    WithSample = 255

    @staticmethod
    def get_speed(speed):
        if isinstance(speed, HeadSpeed):
            return speed
        if isinstance(speed, str):
            speed = int(speed)
        try:
            return HeadSpeed(speed)
        except:
            return None

class HeadConfig(Enum):
    Closed = 0
    Down = 1
    Mid = 2
    Galery = 3
    Store = 4

    @staticmethod
    def get_config(config):
        if isinstance(config, HeadConfig):
            return config
        if isinstance(config, str):
            config = int(config)
        try:
            return HeadConfig(config)
        except:
            return None

HEADS = {
    FrontArmsEnum.Right : {
        HeadConfig.Closed : 870,
        HeadConfig.Down : 250,
        HeadConfig.Mid : 565,
        HeadConfig.Galery : 441
    },
    FrontArmsEnum.Center : {
        HeadConfig.Closed : 150,
        HeadConfig.Down : 768,
        HeadConfig.Mid : 460,
        HeadConfig.Galery : 574,
        HeadConfig.Store : 760
    },
    FrontArmsEnum.Left : {
        HeadConfig.Closed : 150,
        HeadConfig.Down : 768,
        HeadConfig.Mid : 460,
        HeadConfig.Galery : 574
    }
}

class ElevatorSpeed(Enum):
    Default = 1023
    With Statuette = 512
    WithSample = 255

    @staticmethod
    def get_speed(speed):
        if isinstance(speed, ElevatorSpeed):
            return speed
        if isinstance(speed, str):
            speed = int(speed)
        try:
            return ElevatorSpeed(speed)
        except:
            return None

class ElevatorConfig(Enum):
    Closed = 0
    Floor = 1
    Mid = 2
    GaleryLow = 3
    ExcavationSquares = 4

    @staticmethod
    def get_config(config):
        if isinstance(config, ElevatorConfig):
            return config
        if isinstance(config, str):
            config = int(config)
        try:
            return ElevatorConfig(config)
        except:
            return None

ELEVATORS = {
    FrontArmsEnum.Right : {
        ElevatorConfig.Closed : 187,
        ElevatorConfig.Down : 768,
        ElevatorConfig.Mid : 518,
        ElevatorConfig.GaleryLow : 581,
        ElevatorConfig.ExcavationSquares : 420
    },
    FrontArmsEnum.Center : {
        ElevatorConfig.Closed : 405,
        ElevatorConfig.Down : 815,
        ElevatorConfig.Mid : 632,
        ElevatorConfig.GaleryLow : 707
    },
    FrontArmsEnum.Left : {
        ElevatorConfig.Closed : 835,
        ElevatorConfig.Down : 220,
        ElevatorConfig.Mid : 421,
        ElevatorConfig.GaleryLow : 361,
        ElevatorConfig.ExcavationSquares : 540
    }
}

@if_enabled
@use_queue
def set_head_speed(arm, speed):
    arm = FrontArmsEnum.get_arm(arm)
    speed = HeadSpeed.get_speed(speed)

    if arm is None or speed is None:
        return RobotStatus.return_status(RobotStatus.Failed)

    return self.actuators.ax_set_speed(arm.get_head_id(), speed.value)

@if_enabled
@use_queue
def set_head_config(arm, config):
    arm = FrontArmsEnum.get_arm(arm)
    config = HeadConfig.get_config(config)

    if arm is None or config is None:
        return RobotStatus.return_status(RobotStatus.Failed)

    return self.actuators.ax_move(arm.get_head_id(), HEADS[arm][config])

@if_enabled
@use_queue
def set_elevator_speed(arm, speed):
    arm = FrontArmsEnum.get_arm(arm)
    speed = ElevatorConfig.get_speed(speed)

    if arm is None or speed is None:
        return RobotStatus.return_status(RobotStatus.Failed)

    return self.actuators.ax_set_speed(arm.get_elevator_id(), speed.value)

@if_enabled
@use_queue
def set_elevator_config(arm, config):
    arm = FrontArmsEnum.get_arm(arm)
    config = ElevatorConfig.get_config(config)

    if arm is None or config is None:
        return RobotStatus.return_status(RobotStatus.Failed)

    return self.actuators.ax_move(arm.get_head_id(), ELEVATORS[arm][config])
