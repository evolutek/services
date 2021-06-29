from evolutek.lib.status import RobotStatus
from evolutek.lib.utils.wrappers import if_enabled, use_queue
from time import sleep

#########
# REEFS #
#########

@if_enabled
@use_queue
def get_reef(self):

    self.left_cup_holder_open(use_queue=False)
    self.right_cup_holder_open(use_queue=False)
    self.actuators.pumps_get([7, 8, 9, 10])

    sleep(0.25)

    self.trajman.move_trsl(300, 300, 300, 300, 0)
    self.recal(0)

    sleep(1)

    self.left_cup_holder_close(use_queue=False)
    self.right_cup_holder_close(use_queue=False)

    status = self.check_abort()
    if status != RobotStatus.Ok:
        return RobotStatus.return_status(status)

    sleep(0.25)

    status = RobotStatus.get_status(self.move_trsl(300, 300, 300, 300, 1))
    if status != RobotStatus.Reached:
        return RobotStatus.return_status(status)

    return RobotStatus.return_status(RobotStatus.Done)


@if_enabled
@use_queue
def start_lighthouse(self):
    self.left_cup_holder_open(use_queue=False) if self.side else self.right_cup_holder_open(use_queue=False)
    sleep(0.25)
    status = self.check_abort()

    if status != RobotStatus.Ok:
        self.left_cup_holder_close(use_queue=False) if self.side else self.right_cup_holder_close(use_queue=False)
        return RobotStatus.return_status(status)

    status = RobotStatus.get_status(self.goto_avoid(x=180, y=2875, use_queue=False))

    if status != RobotStatus.Reached:
        self.left_cup_holder_close(use_queue=False) if self.side else self.right_cup_holder_close(use_queue=False)
        return RobotStatus.return_status(status)

    status = self.get_status(self.goto_avoid(x=200, y=2600, use_queue=False))

    if status != RobotStatus.Reached:
        self.left_cup_holder_close(use_queue=False) if self.side else self.right_cup_holder_close(use_queue=False)
        return RobotStatus.return_status(status)

    self.left_cup_holder_close(use_queue=False) if self.side else self.right_cup_holder_close(use_queue=False)

    return RobotStatus.return_status(RobotStatus.Done)


@if_enabled
@use_queue
def push_windsocks(self):

    self.right_arm_open(use_queue=False) if self.side else self.left_arm_open(use_queue=False)

    sleep(0.25)

    status = self.check_abort()
    if status != RobotStatus.Ok:
        self.right_arm_close(use_queue=False) if self.side else self.left_arm_close(use_queue=False)
        return RobotStatus.return_status(status)

    # TODO : Change deltas of CM ?

    status = RobotStatus.get_status(self.goto_avoid(x=1825, y=720, use_queue=False))
    if status != RobotStatus.Reached:
        self.right_arm_close(use_queue=False) if self.side else self.left_arm_close(use_queue=False)
        return RobotStatus.return_status(status)

    if self.side:
        self.right_arm_push(use_queue=False)
        sleep(0.25)
        self.right_arm_close(use_queue=False)
    else:
        self.left_arm_push(use_queue=False)
        sleep(0.25)
        self.left_arm_close(use_queue=False)

    return RobotStatus.return_status(RobotStatus.Done)
