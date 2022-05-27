from evolutek.lib.robot.robot_actions_imports import *

@if_enabled
@async_task
def disguise(self, enable=True):
    #if enable: return RobotStatus.check(self.disguise_on(), score=5)
    #return RobotStatus.check(self.disguise_off())
    return RobotStatus.return_status(RobotStatus.Done) # TODO
