from evolutek.lib.robot.robot_actions_imports import *
from random import choice

MIN_X = 600
MAX_X = 1400
MIN_Y = 600
MAX_Y = 2400

class Stack:

    def __init__(self, x, y, color):
        self.pos = Point(x, y)
        self.color = color

    def __str__(self):
        return ("Stack at pos (%d, %d) with color %s" % (self.pos.x, self.pos.y, self.color.name))

# Format: ((x, y), couleur)
STACKS = [
    Stack(Point(225, 450 + 125), Color.Pink),                         # 2
    Stack(Point(225, 450 + 125 + 200), Color.Yellow),                 # 2
    Stack(Point(225, 3000 - 450 - 125 - 200), Color.Yellow),          # 1
    Stack(Point(225, 3000 - 450 - 125), Color.Pink),                  # 1
    Stack(Point(1000 - 275, 1125), Color.Marron),                     # 2
    Stack(Point(1000 - 275, 3000 - 1125), Color.Marron),              # 1
    Stack(Point(1000 + 275, 1125), Color.Marron),                     # 3
    Stack(Point(1000 + 275, 3000 - 1125), Color.Marron),              # 4
    Stack(Point(2000 - 225, 450 + 125), Color.Pink),                  # 3
    Stack(Point(2000 - 225, 450 + 125 + 200), Color.Yellow),          # 3
    Stack(Point(2000 - 225, 3000 - 450 - 125 - 200), Color.Yellow),   # 4
    Stack(Point(2000 - 225, 3000 - 450 - 125), Color.Pink)            # 4
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
def roam_stacks(self):
    for stack in STACKS:
        print('[ROBOT] Going on stack: %s' % str(stack))
        status = self.goto_avoid(**stack.pos, async_task=False, timeout=10)
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
def go_grab_one_stack(self):
    stack = choice(STACKS)
    print('[ROBOT] Going to grab stack: %s' % str(stack))
    
    # Points d'intérêt
    robot_point = Point(dict=self.trajman.get_position())
    
    # Aller devant le point
    status = self.goth(robot_point.compute_angle(stack.pos), async_task=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached:
        return RobotStatus.return_status(RobotStatus.get_status(status))
        
    go_to_point = robot_point.compute_offset_point(stack.pos, -250)
    status = self.goto_avoid(x=go_to_point.x, y=go_to_point.y, async_task=False, timeout=10)
    if RobotStatus.get_status(status) != RobotStatus.Reached:
        return RobotStatus.return_status(RobotStatus.get_status(status))
    #sleep(5)
    
    # Se préparer
    self.elevator_up(async_task=False)
    sleep(1)
    
    # Aller sur le point
    go_to_point = robot_point.compute_offset_point(stack.pos, -90)
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
def go_grab_some_stack(self):
    for x in range(randint(len(STACKS))):
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
