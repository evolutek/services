from evolutek.lib.robot.robot_actions_imports import *

@if_enabled
@async_task
def broom_square(self):
    #Go next to the square
    self.goto_avoid(x = 1000, y = 1340, async_task = False)
    self.goth(theta = 0, async_task = False)
    #Go in front of the square
    self.goto_avoid(x = 1360, y = 1340, async_task = False)
    self.goth(theta = -pi/2, async_task = False)
    #Open Snowplow
    self.snowplow_open(async_task = False)
    #Set speed to slow
    self.trajman.set_trsl_max_speed(200)
    #Advance to push the samples
    self.goto_avoid(x = 1360, y = 510, async_task = False)
    #self.goth(theta = -pi/2, async_task = False)
    #Set speed back to mid
    self.trajman.set_trsl_max_speed(400)
    #Go in front of the shelter
    self.goto_avoid(x = 1490, y = 510, async_task = False)
    input("\nPute\n")
    self.goth(theta = -pi / 4, async_task = False)
    input()
    self.goto_avoid(x = 1430, y = 450, async_task = False)
    input()
    self.bumper_open(async_task = False)
    input()
    self.goto_avoid(x = 1490, y = 510, async_task = False)
    #self.goth(theta  = 5 * pi /4, async_task = False)

    #Set speed back to normal
    self.trajman.set_trsl_max_speed(600)
