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

def pumps_get(self, ids, mirror=True):
    if isinstance(ids, str):
            ids = ids.split(",")

    if isinstance(mirror, str):
        mirror = mirror == 'true'

    _ids = []
    for id in ids:
        _ids.append(self.mirror_pump_id(int(id)) if mirror else int(id))

    return self.actuators.pumps_get(_ids)

def pumps_drop(self, ids, mirror=True):
    if isinstance(ids, str):
            ids = ids.split(",")

    if isinstance(mirror, str):
        mirror = mirror == 'true'

    _ids = []
    for id in ids:
        _ids.append(self.mirror_pump_id(int(id)) if mirror else int(id))

    return self.actuators.pumps_drop(_ids)

#########
# FLAGS #
#########

# Raise Flags
@if_enabled
@use_queue
def flags_raise(self):
    return self.actuators.ax_move(6, 820)

# Close flags
@if_enabled
@use_queue
def flags_low(self):
    return self.actuators.ax_move(6, 512)

#############
# FRONT ARM #
#############

# Front Arm Close
@if_enabled
@use_queue
def front_arm_close(self):
    return self.actuators.ax_move(1, 512)

# Front Arm Open
@if_enabled
@use_queue
def front_arm_open(self):
    return self.actuators.ax_move(1, 820)
#############
# SIDE ARMS #
#############

# Left Arm Close
@if_enabled
@use_queue
def left_arm_close(self):
    return self.actuators.ax_move(2, 820)

# Left Arm Open
@if_enabled
@use_queue
def left_arm_open(self):
    return self.actuators.ax_move(2, 512)

# Left Arm Push Windsock
@if_enabled
@use_queue
def left_arm_push(self):
    return self.actuators.ax_move(2, 444)

# Right Arm Close
@if_enabled
@use_queue
def right_arm_close(self):
    return self.actuators.ax_move(3, 204)

# Right Arm Open
@if_enabled
@use_queue
def right_arm_open(self):
    return self.actuators.ax_move(3, 512)

# Right Arm Push Windsock
@if_enabled
@use_queue
def right_arm_push(self):
    return self.actuators.ax_move(3, 580)

###############
# CUP HOLDERS #
###############

# Left CH Close
@if_enabled
@use_queue
def left_cup_holder_close(self):
    self.actuators.ax_set_speed(4, 256)
    return self.actuators.ax_move(4, 820)

# Left CH Open
@if_enabled
@use_queue
def left_cup_holder_open(self):
    self.actuators.ax_set_speed(4, 800)
    return self.actuators.ax_move(4, 512)

# Left CH Drop
@if_enabled
@use_queue
def left_cup_holder_drop(self):
    self.actuators.ax_set_speed(4, 800)
    return self.actuators.ax_move(4, 490)

# Right CH Close
@if_enabled
@use_queue
def right_cup_holder_close(self):
    self.actuators.ax_set_speed(5, 256)
    return self.actuators.ax_move(5, 820)

# Right CH Open
@if_enabled
@use_queue
def right_cup_holder_open(self):
    self.actuators.ax_set_speed(5, 800)
    return self.actuators.ax_move(5, 512)

# Right CH Drop
@if_enabled
@use_queue
def right_cup_holder_drop(self):
    self.actuators.ax_set_speed(5, 800)
    return self.actuators.ax_move(5, 490)
