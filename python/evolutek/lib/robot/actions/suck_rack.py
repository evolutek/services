from evolutek.lib.robot.robot_actions_imports import *


@if_enabled
@async_task
def suck_rack(self, left=True, forward=True):
    status = []
    init_pos = self.trajman.get_position()
    quantity = 7 if 500 < init_pos["y"] < 1500 else 10
    forward_value = 30 if forward else -30

    if left:
        self.extend_left_vacuum()
    else:
        self.extend_right_vacuum()

    for i in range(quantity):
        self.turbine_on()
        sleep(0.5)
        self.turbine_off()
        self.forward(forward_value)
        self.cherry_count += 1
        sleep(1)

    if left:
        self.retract_left_vacuum()
    else:
        self.retract_right_vacuum()

    return check_status(*status, score=0)