from evolutek.lib.robot.robot_actions_imports import *
from random import choice

MIN_X = 600
MAX_X = 1400
MIN_Y = 600
MAX_Y = 2400


# Format: ((x, y), couleur)
CAKES = [
    ((225, 450 + 125), Color.Pink),                         # 2
    ((225, 450 + 125 + 200), Color.Yellow),                 # 2
    ((225, 3000 - 450 - 125 - 200), Color.Yellow),          # 1
    ((225, 3000 - 450 - 125), Color.Pink),                  # 1
    ((1000 - 275, 1125), Color.Marron),                     # 2
    ((1000 - 275, 3000 - 1125), Color.Marron),              # 1
    ((1000 + 275, 1125), Color.Marron),                     # 3
    ((1000 + 275, 3000 - 1125), Color.Marron),              # 4
    ((2000 - 225, 450 + 125), Color.Pink),                  # 3
    ((2000 - 225, 450 + 125 + 200), Color.Yellow),          # 3
    ((2000 - 225, 3000 - 450 - 125 - 200), Color.Yellow),   # 4
    ((2000 - 225, 3000 - 450 - 125), Color.Pink)            # 4
]  # x grands

# Format: ((xmin, xmax), (ymin, ymax))
ZONES = [
    ((0, 450), (450+125+200+125, 450+125+200+125+450)),
    ((0, 450), (3000-450, 3000)),
    ((450+50, 450+50+450), (0, 450)),
    ((2000-450, 2000), (1500+150, 1500+150+450)),
    ((2000-450, 2000), (0, 450))
]


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
    #sleep(5)
    
    # Se préparer
    self.elevator_up(async_task=False)
    sleep(1)
    
    # Aller sur le point
    go_to_point = robot_point.compute_offset_point(dest_point, -90)
    status = self.goto_avoid(x=go_to_point.x, y=go_to_point.y, async_task=False, timeout=10)
    if RobotStatus.get_status(status) != RobotStatus.Reached:
        return RobotStatus.return_status(RobotStatus.get_status(status))
    #sleep(5)
    
    # Attraper
    self.grab_stack(async_task=False)
    #sleep(1)
    
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
def go_drop_one(self):
    zone = choice(ZONES)
    robot_point = Point(dict=self.trajman.get_position())
    drop_zone = Point(x=(zone[0][0] + zone[0][1]) // 2, y=(zone[1][0] + zone[1][1]) // 2)
    dest_point = robot_point.compute_offset_point(drop_zone, -110)
    status = self.goth(robot_point.compute_angle(dest_point), async_task=False)
    
    # On va en zone
    status = self.goto_avoid(x=dest_point.x, y=dest_point.y async_task=False, timeout=10)
    if RobotStatus.get_status(status) != RobotStatus.Reached:
        return RobotStatus.return_status(RobotStatus.get_status(status))    
    
    # On drop la pile
    self.clamp_open(async_task=False)
    sleep(0.5)

    # On recule pour manoeuvrer 
    go_to_point = robot_point.compute_offset_point(drop_zone, -250)
    status = self.goto_avoid(x=go_to_point.x, y=go_to_point.y, async_task=False, timeout=10)
    if RobotStatus.get_status(status) != RobotStatus.Reached:
        return RobotStatus.return_status(RobotStatus.get_status(status))
    #sleep(5)

    return RobotStatus.return_status(RobotStatus.Done, score=0)
