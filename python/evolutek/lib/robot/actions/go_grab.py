from evolutek.lib.robot.robot_actions_imports import *
from random import choice

MIN_X = 600
MAX_X = 1400
MIN_Y = 600
MAX_Y = 2400

ROSE = 0
JAUNE = 1
MARRON = 2

# Format: ((x, y), couleur)
CAKES = [((225, 450 + 125), ROSE), ((225, 450 + 125 + 200), JAUNE), ((225, 3000 - 450 - 125 - 200), JAUNE), ((225, 3000 - 450 - 125), ROSE),  # x petits
        ((1000 - 275, 1125), MARRON), ((1000 - 275, 3000 - 1125), MARRON),  # x moyens -
        ((1000 + 275, 1125), MARRON), ((1000 + 275, 3000 - 1125), MARRON),  # x moyens +
        ((2000 - 225, 450 + 125), ROSE), ((2000 - 225, 450 + 125 + 200), JAUNE), ((2000 - 225, 3000 - 450 - 125 - 200), JAUNE), ((2000 - 225, 3000 - 450 - 125), ROSE)]  # x grands

# Format: ((xmin, xmax), (ymin, ymax))
ZONES = [((0, 450), (450+125+200+125, 450+125+200+125+450)), ((0, 450), (3000-450, 3000)), 
        ((450+50, 450+50+450), (0, 450))
        ((2000-450, 2000), (0, 450)), ((1500+150), (, 1500+150+450))]


@if_enabled
@async_task
def roam_cakes(self):
    for cake in CAKES:
        status = self.goto_avoid(x=cake[0][0], y=cake[0][1], async_task=False, timeout=10)
        if RobotStatus.get_status(status) != RobotStatus.Reached:
            return RobotStatus.return_status(RobotStatus.get_status(status))
        sleep(5)
    return RobotStatus.return_status(RobotStatus.Done, score=0)


@if_enabled
@async_task
def roam_zones(self):
    for zone in ZONES:
        status = self.goto_avoid(x=(zone[0][0] + zone[0][1]) // 2, y=(zone[1][0] + zone[1][1]) // 2, async_task=False, timeout=10)
        if RobotStatus.get_status(status) != RobotStatus.Reached:
            return RobotStatus.return_status(RobotStatus.get_status(status))
        sleep(5)
    return RobotStatus.return_status(RobotStatus.Done, score=0)


@if_enabled
@async_task
def go_grab_one(self):
    cake = choice(CAKES)
    
    # Points d'intérêt
    robot_point = Point(dict=self.trajman.get_position())
    dest_point = Point(x=cake[0][0], y=cake[0][1])
    
    # Aller devant le point
    status = self.goth(robot_point.compute_angle(dest_point), async_task=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached:
        return RobotStatus.return_status(RobotStatus.get_status(status))
        
    go_to_point = robot_point.compute_offset_point(dest_point, -250)
    status = self.goto_avoid(x=go_to_point.x, y=go_to_point.y, async_task=False, timeout=10)
    if RobotStatus.get_status(status) != RobotStatus.Reached:
        return RobotStatus.return_status(RobotStatus.get_status(status))
    sleep(5)
    
    # Se préparer
    self.elevator_up(async_task=False)
    sleep(1)
    
    # Aller sur le point
    go_to_point = robot_point.compute_offset_point(dest_point, -90)
    status = self.goto_avoid(x=go_to_point.x, y=go_to_point.y, async_task=False, timeout=10)
    if RobotStatus.get_status(status) != RobotStatus.Reached:
        return RobotStatus.return_status(RobotStatus.get_status(status))
    sleep(5)
    
    # Attraper
    self.grab_stack(async_task=False)
    sleep(1)
    
    return RobotStatus.return_status(RobotStatus.Done, score=0)


@if_enabled
@async_task
def go_grab_some(self):
    for x in range(randint(len(CAKES))):
        status = self.go_grab_one(async_task=False)
        if RobotStatus.get_status(status) != RobotStatus.Reached:
            return RobotStatus.return_status(RobotStatus.get_status(status))
    return RobotStatus.return_status(RobotStatus.Done, score=0)


@if_enabled
@async_task
def go_grab_one_and_come_back(self):
    status = self.go_grab_one(async_task=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached:
        return RobotStatus.return_status(RobotStatus.get_status(status))
        
    zone = choice(ZONES)
    status = self.goto_avoid(x=(zone[0][0] + zone[0][1]) // 2, y=(zone[1][0] + zone[1][1]) // 2, async_task=False, timeout=10)
    if RobotStatus.get_status(status) != RobotStatus.Reached:
        return RobotStatus.return_status(RobotStatus.get_status(status))    

    return RobotStatus.return_status(RobotStatus.Done, score=0)
