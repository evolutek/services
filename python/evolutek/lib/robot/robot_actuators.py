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
def flags_raise(self, use_queue=True):

    def f():
        return RobotStatus.get_status(self.actuators.ax_move(6, 820))

    if not use_queue:
        return f()
    else:
        self.queue.run_action(f, [])

# Close flags
@if_enabled
def flags_low(self, use_queue=True):

    def f():
        return RobotStatus.get_status(self.actuators.ax_move(6, 512))

    if not use_queue:
        return f()
    else:
        self.queue.run_action(f, [])

#############
# SIDE ARMS #
#############

# Left Arm Close
@if_enabled
def left_arm_close(self, use_queue=True):

    def f():
        return RobotStatus.get_status(self.actuators.ax_move(2, 820))

    if not use_queue:
        return f()
    else:
        self.queue.run_action(f, [])

# Left Arm Open
@if_enabled
def left_arm_open(self, use_queue=True):

    def f():
        return RobotStatus.get_status(self.actuators.ax_move(2, 512))

    if not use_queue:
        return f()
    else:
        self.queue.run_action(f, [])

# Left Arm Push Windsock
@if_enabled
def left_arm_push(self, use_queue=True):

    def f():
        return RobotStatus.get_status(self.actuators.ax_move(2, 444))

    if not use_queue:
        return f()
    else:
        self.queue.run_action(f, [])

# Right Arm Close
@if_enabled
def right_arm_close(self, use_queue=True):

    def f():
        return RobotStatus.get_status(self.actuators.ax_move(3, 204))

    if not use_queue:
        return f()
    else:
        self.queue.run_action(f, [])

# Right Arm Open
@if_enabled
def right_arm_open(self, use_queue=True):

    def f():
        return RobotStatus.get_status(self.actuators.ax_move(3, 512))

    if not use_queue:
        return f()
    else:
        self.queue.run_action(f, [])

# Right Arm Push Windsock
@if_enabled
def right_arm_push(self, use_queue=True):

    def f():
        return RobotStatus.get_status(self.actuators.ax_move(3, 580))

    if not use_queue:
        return f()
    else:
        self.queue.run_action(f, [])

###############
# CUP HOLDERS #
###############

# Left CH Close
@if_enabled
def left_cup_holder_close(self, use_queue=True):

    def f():
        self.actuators.ax_set_speed(4, 256)
        return RobotStatus.get_status(self.actuators.ax_move(4, 820))

    if not use_queue:
        return f()
    else:
        self.queue.run_action(f, [])

# Left CH Open
@if_enabled
def left_cup_holder_open(self, use_queue=True):

    def f():
        self.actuators.ax_set_speed(4, 800)
        return RobotStatus.get_status(self.actuators.ax_move(4, 512))

    if not use_queue:
        return f()
    else:
        self.queue.run_action(f, [])

# Left CH Drop
@if_enabled
def left_cup_holder_drop(self, use_queue=True):
    self.actuators.ax_set_speed(4, 800)
    return RobotStatus.get_status(self.actuators.ax_move(4, 490))
    if status != RobotStatus.Done:
        return RobotStatus.Failed
    return RobotStatus.Done

# Right CH Close
@if_enabled
def right_cup_holder_close(self, use_queue=True):

    def f():
        self.actuators.ax_set_speed(5, 256)
        return RobotStatus.get_status(self.actuators.ax_move(5, 820))

    if not use_queue:
        return f()
    else:
        self.queue.run_action(f, [])

# Right CH Open
@if_enabled
def right_cup_holder_open(self, use_queue=True):

    def f():
        self.actuators.ax_set_speed(5, 800)
        return RobotStatus.get_status(self.actuators.ax_move(5, 512))

    if not use_queue:
        return f()
    else:
        self.queue.run_action(f, [])

# Right CH Drop
@if_enabled
def right_cup_holder_drop(self, use_queue=True):

    def f():
        self.actuators.ax_set_speed(5, 800)
        return RobotStatus.get_status(self.actuators.ax_move(5, 490))

    if not use_queue:
        return f()
    else:
        self.queue.run_action(f, [])
