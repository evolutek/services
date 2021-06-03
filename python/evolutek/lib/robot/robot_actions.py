from evolutek.lib.status import RobotStatus
from evolutek.lib.utils.wrappers import if_enabled
from time import sleep

# TODO : check for abort and match end

#########
# REEFS #
#########

@if_enabled
def get_reef(self):

    # TODO : Recal ?

    self.left_cup_holder.open()
    self.right_cup_holder.open()
    self.actuators.pumps_get([6, 7, 8, 9])

    sleep(0.25)

    if self.move_trsl(300, 300, 300, 300, 0) != RobotStatus.Reached:
        return RobotStatus.Failed

    sleep(1)

    self.left_cup_holder_close()
    self.right_cup_holder_close()

    sleep(0.25)
    if self.move_trsl(300, 300, 300, 300, 1)  != RobotStatus.Reached:
        return RobotStatus.Failed

    return RobotStatus.Done
