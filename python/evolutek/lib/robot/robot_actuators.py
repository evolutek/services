from enum import Enum
from evolutek.lib.status import RobotStatus
from evolutek.lib.utils.color import Color
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

    return self.actuators.pumps_get(_ids)

@if_enabled
@async_task
def pumps_drop(self, ids, use_ev=True, mirror=True):
    if isinstance(ids, str):
        ids = ids.split(",")

    if isinstance(mirror, str):
        mirror = mirror == 'true'

    _ids = []
    for id in ids:
        _ids.append(self.mirror_pump_id(int(id)) if mirror else int(id))

    return self.actuators.pumps_drop(_ids, use_ev)

@if_enabled
@async_task
def stop_evs(self, ids, mirror=True):
    if isinstance(ids, str):
        ids = ids.split(",")

    if isinstance(mirror, str):
        mirror = mirror == 'true'

    _ids = []
    for id in ids:
        _ids.append(self.mirror_pump_id(int(id)) if mirror else int(id))

    return self.actuators.stop_evs(_ids)

#############
# FRONT ARM #
#############

@if_enabled
@async_task
def snowplow_open(self):
    status1 = RobotStatus.get_status(self.actuators.servo_set_angle(0, 0))
    status2 = RobotStatus.get_status(self.actuators.servo_set_angle(15, 120))
    return RobotStatus.return_status(RobotStatus.Done if status1 == status2 == RobotStatus.Done else RobotStatus.Failed)

@if_enabled
@async_task
def snowplow_close_left(self):
    status1 = RobotStatus.get_status(self.actuators.servo_set_angle(15, 0))
    return RobotStatus.return_status(RobotStatus.Done if status1 == RobotStatus.Done else RobotStatus.Failed)
@if_enabled
@async_task
def snowplow_close_right(self):
    status1 = RobotStatus.get_status(self.actuators.servo_set_angle(0, 120))
    return RobotStatus.return_status(RobotStatus.Done if status1 == RobotStatus.Done else RobotStatus.Failed)

@if_enabled
@async_task
def snowplow_open_left(self):
    status1 = RobotStatus.get_status(self.actuators.servo_set_angle(15, 120))
    return RobotStatus.return_status(RobotStatus.Done if status1 == RobotStatus.Done else RobotStatus.Failed)

@if_enabled
@async_task
def snowplow_open_right(self):
    status1 = RobotStatus.get_status(self.actuators.servo_set_angle(0, 0))
    return RobotStatus.return_status(RobotStatus.Done if status1 == RobotStatus.Done else RobotStatus.Failed)

@if_enabled
@async_task
def snowplow_close(self):
    status1 = RobotStatus.get_status(self.actuators.servo_set_angle(0, 120))
    status2 = RobotStatus.get_status(self.actuators.servo_set_angle(15, 0))
    return RobotStatus.return_status(RobotStatus.Done if status1 == status2 == RobotStatus.Done else RobotStatus.Failed)

@if_enabled
@async_task
def bumper_open(self):
    status1 = RobotStatus.get_status(self.actuators.servo_set_angle(1, 0))
    status2 = RobotStatus.get_status(self.actuators.servo_set_angle(14, 98))
    return RobotStatus.return_status(RobotStatus.Done if status1 == status2 == RobotStatus.Done else RobotStatus.Failed)

@if_enabled
@async_task
def bumper_close(self):
    status1 = RobotStatus.get_status(self.actuators.servo_set_angle(1, 98))
    status2 = RobotStatus.get_status(self.actuators.servo_set_angle(14, 0))
    return RobotStatus.return_status(RobotStatus.Done if status1 == status2 == RobotStatus.Done else RobotStatus.Failed)

#############
# SIDE ARMS #
#############

# Left Arm Close
@if_enabled
@async_task
def left_arm_close(self):
    return self.actuators.ax_move(8, 512)

# Left Arm Open
@if_enabled
@async_task
def left_arm_open(self):
    return self.actuators.ax_move(8, 755)

# Right Arm Close
@if_enabled
@async_task
def right_arm_close(self):
    return self.actuators.ax_move(7, 512)

# Right Arm Open
@if_enabled
@async_task
def right_arm_open(self):
    return self.actuators.ax_move(7, 290)

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
    WithStatuette = 512
    WithSample = 255
    VeryLow = 127

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
    Pickup = 4
    StoreStatuette = 5

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
        HeadConfig.Galery : 512
    },
    FrontArmsEnum.Center : {
        HeadConfig.Closed : 150,
        HeadConfig.Down : 768,
        HeadConfig.Mid : 460,
        HeadConfig.Galery : 512,
        HeadConfig.Pickup : 170,
        HeadConfig.StoreStatuette : 125
    },
    FrontArmsEnum.Left : {
        HeadConfig.Closed : 150,
        HeadConfig.Down : 768,
        HeadConfig.Mid : 460,
        HeadConfig.Galery : 512
    }
}

class ElevatorSpeed(Enum):
    Default = 1023
    WithStatuette = 512
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
    Down = 1
    Mid = 2
    GaleryLow = 3
    ExcavationSquares = 4
    StoreStatuette = 5
    LowMid=6

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
        ElevatorConfig.Mid : 537,
        ElevatorConfig.GaleryLow : 581,
        ElevatorConfig.ExcavationSquares : 440,
    },
    FrontArmsEnum.Center : {
        ElevatorConfig.Closed : 405,
        ElevatorConfig.Down : 815,
        ElevatorConfig.Mid : 639,
        ElevatorConfig.LowMid: 680,
        ElevatorConfig.GaleryLow : 750,
        ElevatorConfig.StoreStatuette : 509,
    },
    FrontArmsEnum.Left : {
        ElevatorConfig.Closed : 835,
        ElevatorConfig.Down : 220,
        ElevatorConfig.Mid : 486,
        ElevatorConfig.GaleryLow : 361,
        ElevatorConfig.ExcavationSquares : 600,
    }
}

@if_enabled
@async_task
def set_head_speed(self, arm, speed):
    arm = FrontArmsEnum.get_arm(arm)
    speed = HeadSpeed.get_speed(speed)

    if arm is None or speed is None:
        return RobotStatus.return_status(RobotStatus.Failed)

    return self.actuators.ax_set_speed(arm.get_head_id(), speed.value)

@if_enabled
@async_task
def set_head_config(self, arm, config):
    arm = FrontArmsEnum.get_arm(arm)
    config = HeadConfig.get_config(config)

    if arm is None or config is None:
        return RobotStatus.return_status(RobotStatus.Failed)

    return self.actuators.ax_move(arm.get_head_id(), HEADS[arm][config])

@if_enabled
@async_task
def set_elevator_speed(self, arm, speed):
    arm = FrontArmsEnum.get_arm(arm)
    speed = ElevatorSpeed.get_speed(speed)

    if arm is None or speed is None:
        return RobotStatus.return_status(RobotStatus.Failed)

    return self.actuators.ax_set_speed(arm.get_elevator_id(), speed.value)

@if_enabled
@async_task
def set_elevator_config(self, arm, config):
    arm = FrontArmsEnum.get_arm(arm)
    config = ElevatorConfig.get_config(config)

    if arm is None or config is None:
        return RobotStatus.return_status(RobotStatus.Failed)

    return self.actuators.ax_move(arm.get_elevator_id(), ELEVATORS[arm][config])

def get_pattern(self):
    measurement = self.actuators.read_sensors_pattern()
    result = [ Color[r] for r in measurement ]
    list_of_pattern = []
    color = Color.Yellow if self.side else Color.Purple
    if not self.side: result = result[::-1]

    if result[0] == Color.Red:
        list_of_pattern.append(667.5)
        list_of_pattern.append(852.5)
        #list_of_pattern[2] = False
    elif result[0] == color:
        #list_of_pattern[0] = False
        list_of_pattern.append(852.5)
        list_of_pattern.append(1037.5)

    if result[1] != Color.Unknown:
        if result[1] == color:
            list_of_pattern.append(1222.5)
            #list_of_pattern[4] = False
            #list_of_pattern[5] = False
            list_of_pattern.append(1777.5)
        else:
            #list_of_pattern[3] = False
            list_of_pattern.append(1407.5)
            list_of_pattern.append(1592.5)
            #list_of_pattern[6] = False
    else:
        # First is already down
        list_of_pattern.append(1407.5)
        list_of_pattern.append(1592.5)
        list_of_pattern.append(1777.5)


    return list_of_pattern

