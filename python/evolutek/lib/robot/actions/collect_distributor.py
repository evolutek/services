from evolutek.lib.robot.robot_actions_imports import *


@if_enabled
@async_task
def collect_distributor(self):
    self.goto_avoid(1250, 270, async_task=False)
    self.goth(-pi/2, async_task=False)

    # Step 1
    self.actuators.ax_move(FrontArmsEnum.Center.get_head_id(), 550)
    self.actuators.ax_move(FrontArmsEnum.Center.get_elevator_id(), 730)
    sleep(1)

    # Forward
    self.goto_avoid(1250, 200, async_task=False) # Forward

    # Grap sample
    self.pumps_get(ids="2", async_task=False)

    # Step 2
    self.actuators.ax_move(FrontArmsEnum.Center.get_head_id(), 512)
    self.actuators.ax_move(FrontArmsEnum.Center.get_elevator_id(), 815)

    # Backward simultanously with step 2
    self.goto_avoid(1250, 210, async_task=False)

    # Disable pump
    self.pumps_drop(ids="2", use_ev=False, async_task=False)

    # Continue to backward
    self.goto_avoid(1250, 270, async_task=False)



"""
Step 1:
3 : 550
4 : 730

Step 2:
3 : 512
4 : 815


"""