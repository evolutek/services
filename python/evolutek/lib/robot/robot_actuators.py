from evolutek.lib.status import RobotStatus
from evolutek.lib.utils.wrappers import if_enabled

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
def flags_raise(self):
    status = RobotStatus.get_status(self.actuators.ax_move(6, 820))
    if status != RobotStatus.Done
        return RobotStatus.Failed
    return RobotStatus.Done

# Close flags
@if_enabled
def flags_low(self):
    status = RobotStatus.get_status(self.actuators.ax_move(6, 512))
    if status != RobotStatus.Done
        return RobotStatus.Failed
    return RobotStatus.Done

#############
# SIDE ARMS #
#############

# Left Arm Close
@if_enabled
def left_arm_close(self):
    status = RobotStatus.get_status(self.actuators.ax_move(2, 820))
    if status != RobotStatus.Done
        return RobotStatus.Failed
    return RobotStatus.Done

# Left Arm Open
@if_enabled
def left_arm_open(self):
    status = RobotStatus.get_status(self.actuators.ax_move(2, 512))
    if status != RobotStatus.Done
        return RobotStatus.Failed
    return RobotStatus.Done

# Left Arm Push Windsock
@if_enabled
def left_arm_push(self):
    status = RobotStatus.get_status(self.actuators.ax_move(2, 444))
    if status != RobotStatus.Done
        return RobotStatus.Failed
    return RobotStatus.Done

# Right Arm Close
@if_enabled
def right_arm_close(self):
    status = RobotStatus.get_status(self.actuators.ax_move(3, 204))
    if status != RobotStatus.Done
        return RobotStatus.Failed
    return RobotStatus.Done

# Right Arm Open
@if_enabled
def right_arm_open(self):
    status = RobotStatus.get_status(self.actuators.ax_move(3, 512))
    if status != RobotStatus.Done
        return RobotStatus.Failed
    return RobotStatus.Done

# Right Arm Push Windsock
@if_enabled
def right_arm_push(self):
    status = RobotStatus.get_status(self.actuators.ax_move(3, 580))
    if status != RobotStatus.Done
        return RobotStatus.Failed
    return RobotStatus.Done

###############
# CUP HOLDERS #
###############

# Left CH Close
@if_enabled
def left_cup_holder_close(self):
    self.actuators.ax_set_speed(4, 256)
    status = RobotStatus.get_status(self.actuators.ax_move(4, 820))
    if status != RobotStatus.Done
        return RobotStatus.Failed
    return RobotStatus.Done

# Left CH Open
@if_enabled
def left_cup_holder_open(self):
    self.actuators.ax_set_speed(4, 800)
    status = RobotStatus.get_status(self.actuators.ax_move(4, 512))
    if status != RobotStatus.Done
        return RobotStatus.Failed
    return RobotStatus.Done

# Left CH Drop
@if_enabled
def left_cup_holder_drop(self):
    self.actuators.ax_set_speed(4, 800)
    status = RobotStatus.get_status(self.actuators.ax_move(4, 490))
    if status != RobotStatus.Done
        return RobotStatus.Failed
    return RobotStatus.Done

# Right CH Close
@if_enabled
def right_cup_holder_close(self):
    self.actuators.ax_set_speed(5, 256)
    status = RobotStatus.get_status(self.actuators.ax_move(5, 820))
    if status != RobotStatus.Done
        return RobotStatus.Failed
    return RobotStatus.Done

# Right CH Open
@if_enabled
def right_cup_holder_open(self):
    self.actuators.ax_set_speed(5, 800)
    status = RobotStatus.get_status(self.actuators.ax_move(5, 512))
    if status != RobotStatus.Done
        return RobotStatus.Failed
    return RobotStatus.Done

# Right CH Drop
@if_enabled
def right_cup_holder_drop(self):
    self.actuators.ax_set_speed(5, 800)
    status = RobotStatus.get_status(self.actuators.ax_move(5, 490))
    if status != RobotStatus.Done
        return RobotStatus.Failed
    return RobotStatus.Done
