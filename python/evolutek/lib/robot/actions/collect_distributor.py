from evolutek.lib.robot.robot_actions_imports import *


def get_sample(self, y):

    # Step 1
    self.actuators.ax_move(FrontArmsEnum.Center.get_head_id(), 550)
    self.actuators.ax_move(FrontArmsEnum.Center.get_elevator_id(), 730)
    sleep(1)

    # Grap sample
    self.pumps_get(ids="2", async_task=False)

    # Forward
    self.goto_avoid(1250, y, async_task=False) # Forward

    # Step 2
    self.actuators.ax_move(FrontArmsEnum.Center.get_head_id(), 515)
    self.actuators.ax_move(FrontArmsEnum.Center.get_elevator_id(), 815)

    # Backward simultanously with step 2
    speed = self.trajman.get_speeds()['trmax']
    self.trajman.set_trsl_max_speed(10)
    self.goto_avoid(1250, 300, async_task=False)
    self.trajman.set_trsl_max_speed(speed)

    # Disable pump
    self.pumps_drop(ids="2", use_ev=False, async_task=False)

    # Continue to backward
    self.set_head_config(arm=FrontArmsEnum.Center.get_head_id(), config=HeadConfig.Down, async_task=False)
    sleep(0.2)
    self.goto_avoid(1250, 350, async_task=False)


@if_enabled
@async_task
def collect_distributor(self):
    self.goto_avoid(1250, 270, async_task=False)
    self.goth(-pi/2, async_task=False)
    get_sample(self, 225)




"""
Step 1:
3 : 550
4 : 730

Step 2:
3 : 512
4 : 815


"""