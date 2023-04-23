from evolutek.lib.robot.robot_actions_imports import *
from random import choice

MIN_X = 600
MAX_X = 1400
MIN_Y = 600
MAX_Y = 2400

class Stack:
    def __init__(self, id, x, y, color):
        self.id = id
        self.pos = Point(x, y)
        self.color = color

    def __str__(self):
        return ("Stack %d at pos (%d, %d) with color %s" % (self.id, self.pos.x, self.pos.y, self.color.name))
    
    def to_dict(self):
        return {'x':self.pos.x, 'y':self.pos.y}
STACKS = [
    Stack(1, 575, 225, Color.Pink),
    Stack(1, 775, 225, Color.Yellow),
    Stack(1, 1125, 725, Color.Brown),
    Stack(2, 2425, 225, Color.Pink),
    Stack(2, 2225, 225, Color.Yellow),
    Stack(2, 1875, 725, Color.Brown),
    Stack(3, 2425, 1775, Color.Pink),
    Stack(3, 2225, 1775, Color.Yellow),
    Stack(3, 1875, 1275, Color.Brown),
    Stack(4, 575, 1775, Color.Pink),
    Stack(4, 775, 1775, Color.Yellow),
    Stack(4, 1125, 1275, Color.Brown)
]

class Zone:
    def __init__(self, id, x1, x2, y1, y2):
        self.id = id
        self.p1 = Point(x1, y1)
        self.p2 = Point(x2, y2)
        self.center = self.p1.average(self.p2)

    def __str__(self):
        return ("Zone %s with center (%d, %d)" % (self.id, self.center.x, self.center.y))

ZONES = [
    Zone('A', 0, 450, 0, 450),
    Zone('B', 1650, 2100, 0, 450),
    Zone('C', 2550, 3000, 500, 950),
    Zone('E', 900, 1350, 1550, 2000),
    Zone('D', 2550, 3000, 1550, 2000)
]

def check_status(*args, score=0):
    for stat in args:
        if stat != RobotStatus.Done:
            return RobotStatus.return_status(RobotStatus.Failed)
    return RobotStatus.return_status(RobotStatus.Done, score=score)

@if_enabled
@async_task
def roam_stacks(self):
    for stack in STACKS:
        print('[ROBOT] Going on stack: %s' % str(stack))
        status = self.goto_avoid(**stack.to_dict(), async_task=False, timeout=10)
        if RobotStatus.get_status(status) != RobotStatus.Reached:
            return RobotStatus.return_status(RobotStatus.get_status(status))
        sleep(5)
    return RobotStatus.return_status(RobotStatus.Done, score=0)


@if_enabled
@async_task
def roam_zones(self):
    for zone in ZONES:
        print('[ROBOT] Going on zone: %s' % str(zone))
        status = self.goto_avoid(**zone.center.to_dict(), async_task=False, timeout=10)
        if RobotStatus.get_status(status) != RobotStatus.Reached:
            return RobotStatus.return_status(RobotStatus.get_status(status))
        sleep(5)
    return RobotStatus.return_status(RobotStatus.Done, score=0)


def get_stack_pos(id, color_name):
    color = Color.get_by_name(color_name)
    for stack in STACKS:
        if stack.id == int(id) and stack.color == color:
            return stack.pos
    return None

@if_enabled
@async_task
def go_grab_one_stack(self, id, color_name):
    stack_pos = get_stack_pos(id, color_name)
    stack_pos = Point(dict=self.mirror_pos(stack_pos.x, stack_pos.y))

    # Points d'intérêt
    robot_point = Point(dict=self.trajman.get_position())

    # Aller devant le point
    status = self.goth(robot_point.compute_angle(stack_pos), async_task=False, mirror=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached:
        return RobotStatus.return_status(RobotStatus.get_status(status))

    go_to_point = robot_point.compute_offset_point(stack_pos, -250)
    status = self.goto_avoid(x=go_to_point.x, y=go_to_point.y, mirror=False, async_task=False, timeout=10)
    if RobotStatus.get_status(status) != RobotStatus.Reached:
        return RobotStatus.return_status(RobotStatus.get_status(status))
    #sleep(5)

    # Se préparer
    if RobotStatus.get_status(self.elevator_move("GetFourth", async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)
    sleep(1)

    # Aller sur le point
    go_to_point = robot_point.compute_offset_point(stack_pos, -80)
    status = self.goto_avoid(x=go_to_point.x, y=go_to_point.y, mirror=False, async_task=False, timeout=10)
    if RobotStatus.get_status(status) != RobotStatus.Reached:
        return RobotStatus.return_status(RobotStatus.get_status(status))
    #sleep(5)

    # Attraper
    status1 = RobotStatus.get_status(self.clamp_open_half(async_task=False))
    sleep(0.5)
    status2 = RobotStatus.get_status(self.clamp_open(async_task=False))
    sleep(0.5)

    go_to_point = robot_point.compute_offset_point(stack_pos, -90)
    status = self.goto_avoid(x=go_to_point.x, y=go_to_point.y, mirror=False, async_task=False, timeout=10)
    if RobotStatus.get_status(status) != RobotStatus.Reached:
        return RobotStatus.return_status(RobotStatus.get_status(status))

    status3 = RobotStatus.get_status(self.elevator_move("Low", async_task=False))
    sleep(1)

    go_to_point = robot_point.compute_offset_point(stack_pos, -75)
    status = self.goto_avoid(x=go_to_point.x, y=go_to_point.y, mirror=False, async_task=False, timeout=10)
    if RobotStatus.get_status(status) != RobotStatus.Reached:
        return RobotStatus.return_status(RobotStatus.get_status(status))

    status4 = RobotStatus.get_status(self.clamp_close(async_task=False))
    sleep(0.5)
    return check_status(status1, status2, status3, status4)


@if_enabled
@async_task
def go_drop_all(self):
    zone_pos = Point(dict=self.mirror_pos(275, 225))

    robot_point = Point(dict=self.trajman.get_position())
    dest_point = robot_point.compute_offset_point(zone_pos, -110)
    status = self.goth(robot_point.compute_angle(dest_point), async_task=False, mirror=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached:
        return RobotStatus.return_status(RobotStatus.get_status(status))

    # On va en zone
    status = self.goto_avoid(x=dest_point.x, y=dest_point.y, async_task=False, mirror=False, timeout=10)
    if RobotStatus.get_status(status) != RobotStatus.Reached:
        return RobotStatus.return_status(RobotStatus.get_status(status))    

    status = RobotStatus.get_status(self.elevator_move("Low", async_task=False))
    sleep(1)

    # On drop la pile
    self.clamp_open(async_task=False)
    sleep(0.5)

    # On recule pour manoeuvrer 
    go_to_point = robot_point.compute_offset_point(zone_pos, -225)
    status = self.goto_avoid(x=go_to_point.x, y=go_to_point.y, mirror=False, async_task=False, timeout=10)
    if RobotStatus.get_status(status) != RobotStatus.Reached:
        return RobotStatus.return_status(RobotStatus.get_status(status))
    #sleep(5)

    return RobotStatus.return_status(RobotStatus.Done, score=3)
