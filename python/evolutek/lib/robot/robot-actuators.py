from evolutek.lib.settings import ROBOT
from evolutek.lib.utils.wrappers import event_waiter, if_enabled

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
    self.actuators.ax_move(6, 820)

# Close flags
@if_enabled
def flags_low(self):
    self.actuators.ax_move(6, 512)

#############
# SIDE ARMS #
#############

# Left Arm Close
@if_enabled
def left_arm_close(self):
    self.actuators.ax_move(2, 820)

# Left Arm Open
@if_enabled
def left_arm_open(self):
    self.actuators.ax_move(2, 512)

# Left Arm Push Windsock
@if_enabled
def left_arm_push(self):
    self.actuators.ax_move(2, 444)

# Right Arm Close
@if_enabled
def right_arm_close(self):
    self.actuators.ax_move(3, 204)

# Right Arm Open
@if_enabled
def right_arm_open(self):
    self.actuators.ax_move(3, 512)

# Right Arm Push Windsock
@if_enabled
def right_arm_push(self):
    self.actuators.ax_move(3, 580)

###############
# CUP HOLDERS #
###############

# Left CH Close
@if_enabled
def left_cup_holder_close(self):
    self.actuators.ax_set_speed(4, 256)
    self.actuators.ax_move(4, 820)

# Left CH Open
@if_enabled
def left_cup_holder_open(self):
    self.actuators.ax_set_speed(4, 800)
    self.actuators.ax_move(4, 512)

# Left CH Drop
@if_enabled
def left_cup_holder_drop(self):
    self.actuators.ax_set_speed(4, 800)
    self.actuators.ax_move(4, 490)

# Right CH Close
@if_enabled
def right_cup_holder_close(self):
    self.actuators.ax_set_speed(5, 256)
    self.actuators.ax_move(5, 820)

# Right CH Open
@if_enabled
def right_cup_holder_open(self):
    self.actuators.ax_set_speed(5, 800)
    self.actuators.ax_move(5, 512)

# Right CH Drop
@if_enabled
def right_cup_holder_drop(self):
    self.actuators.ax_set_speed(5, 800)
    self.actuators.ax_move(5, 490)

