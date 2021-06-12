from evolutek.lib.status import RobotStatus
from evolutek.lib.utils.wrappers import if_enabled, use_queue

#########
# PUMPS #
#########

def mirror_pump_id(self, id):
    if not self.side:
        if id < 6:
            id = (5 - id)
        else:
            id = 6 + (9 - id)
    return id

#########
# FLAGS #
#########

# Raise Flags
@if_enabled
@use_queue
def flags_raise(self):
    return RobotStatus.get_status(self.actuators.ax_move(6, 820)).value

# Close flags
@if_enabled
@use_queue
def flags_low(self):
    return RobotStatus.get_status(self.actuators.ax_move(6, 512)).value

#############
# FRONT ARM #
#############

# Front Arm Close
@if_enabled
@use_queue
def front_arm_close(self):
    return RobotStatus.get_status(self.actuators.ax_move(1, 512)).value

# Front Arm Open
@if_enabled
@use_queue
def front_arm_open(self):
    return RobotStatus.get_status(self.actuators.ax_move(1, 820)).value
#############
# SIDE ARMS #
#############

# Left Arm Close
@if_enabled
@use_queue
def left_arm_close(self):
    return RobotStatus.get_status(self.actuators.ax_move(2, 820)).value

# Left Arm Open
@if_enabled
@use_queue
def left_arm_open(self):
    return RobotStatus.get_status(self.actuators.ax_move(2, 512)).value

# Left Arm Push Windsock
@if_enabled
@use_queue
def left_arm_push(self):
    return RobotStatus.get_status(self.actuators.ax_move(2, 444)).value

# Right Arm Close
@if_enabled
@use_queue
def right_arm_close(self):
    return RobotStatus.get_status(self.actuators.ax_move(3, 204)).value

# Right Arm Open
@if_enabled
@use_queue
def right_arm_open(self):
    return RobotStatus.get_status(self.actuators.ax_move(3, 512)).value

# Right Arm Push Windsock
@if_enabled
@use_queue
def right_arm_push(self):
    return RobotStatus.get_status(self.actuators.ax_move(3, 580)).value

###############
# CUP HOLDERS #
###############

# Left CH Close
@if_enabled
@use_queue
def left_cup_holder_close(self):
    self.actuators.ax_set_speed(4, 256)
    return RobotStatus.get_status(self.actuators.ax_move(4, 820)).value

# Left CH Open
@if_enabled
@use_queue
def left_cup_holder_open(self):
    self.actuators.ax_set_speed(4, 800)
    return RobotStatus.get_status(self.actuators.ax_move(4, 512)).value

# Left CH Drop
@if_enabled
@use_queue
def left_cup_holder_drop(self):
    self.actuators.ax_set_speed(4, 800)
    return RobotStatus.get_status(self.actuators.ax_move(4, 490)).value

# Right CH Close
@if_enabled
@use_queue
def right_cup_holder_close(self):
    self.actuators.ax_set_speed(5, 256)
    return RobotStatus.get_status(self.actuators.ax_move(5, 820)).value

# Right CH Open
@if_enabled
@use_queue
def right_cup_holder_open(self):
    self.actuators.ax_set_speed(5, 800)
    return RobotStatus.get_status(self.actuators.ax_move(5, 512)).value

# Right CH Drop
@if_enabled
@use_queue
def right_cup_holder_drop(self):
    self.actuators.ax_set_speed(5, 800)
    return RobotStatus.get_status(self.actuators.ax_move(5, 490)).value
