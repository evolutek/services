from evolutek.lib.status import RobotStatus
from evolutek.lib.utils.wrappers import event_waiter, if_enabled
from time import sleep

#########
# REEFS #
#########

def get_reef(self):

    # Recal ?

    self.left_cup_holder.open()
    self.right_cup_holder.open()
    self.actuators.pumps_get([6, 7, 8, 9])

    sleep(0.25)

    self.move_trsl(300, 300, 300, 300, 0)

    sleep(1)

    self.left_cup_holder_close()
    self.right_cup_holder_close()

    sleep(0.25)
    self.move_trsl(300, 300, 300, 300, 1)

    return RobotStatus.Done
