from evolutek.lib.robot.robot_actions_imports import *

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

def get_stack_pos(robot, id, color_name):
    color = Color.get_by_name(color_name)
    for stack in STACKS:
        if stack.id == int(id) and stack.color == color:
            if not robot.side:
                return Point(dict=robot.mirror_pos(stack.pos.x, stack.pos.y))
            return stack.pos
    return None

@if_enabled
@async_task
def stack_and_grab(self, id = 1, color_name = "Pink"):
    DEC = 200

    stack_pos = get_stack_pos(self, id, color_name)
    robot_pos = Point(dict=self.trajman.get_position())
    status = []

    search_offset = -120
    offset = -50

    if (len(self.cakes_stack) <= 0):
        status.append(self.clamp_open(async_task=False))
        sleep(0.3)
    if (self.elevator_status != "Low"):
        status.append(self.elevator_move("Low", async_task=False))
        sleep(0.4)

    if (len(self.cakes_stack) > 0):
        status.append(self.elevator_move("High", async_task=False))
        sleep(0.3)

    status.append(self.goth(robot_pos.compute_angle(stack_pos), async_task=False, mirror=False))

    go_to_point = robot_pos.compute_offset_point(stack_pos, search_offset)
    status.append(self.goto_avoid_extend(x=go_to_point.x, y=go_to_point.y, async_task=False, mirror=False, dec=400))
    print(f"Has stack in front : {self.actuators.proximity_sensor_read(id=1)}")
    if (not self.actuators.proximity_sensor_read(id=1)):
        return RobotStatus.check(*status)
    go_to_point = robot_pos.compute_offset_point(stack_pos, offset)
    status.append(self.goto_avoid_extend(x=go_to_point.x, y=go_to_point.y, async_task=False, mirror=False, dec=200, acc=200))
    #sleep(0.5)

    if (len(self.cakes_stack) > 0):
        # Recule
        status.append(self.clamp_open(async_task=False))
        sleep(0.5)
        go_to_point = robot_pos.compute_offset_point(stack_pos, -150)
        status.append(self.goto_avoid(x=go_to_point.x, y=go_to_point.y, mirror=False, async_task=False))
        status.append(self.elevator_move("Low", async_task=False))
        sleep(0.5)
        go_to_point = robot_pos.compute_offset_point(stack_pos, offset)
        status.append(self.goto_avoid_extend(x=go_to_point.x, y=go_to_point.y, async_task=False, mirror=False, dec=200, acc=200))
        sleep(0.5)

    status.append(self.clamp_close(async_task=False))
    sleep(0.5)

    status.append(self.clamp_open_half(async_task=False))
    sleep(0.2)

    status.append(self.move_trsl(15, 200, 200, 300, 1))
    
    status.append(self.clamp_close(async_task=False))
    sleep(0.2)

    for _ in range(3):
        self.cakes_stack.append(color_name)

    return RobotStatus.check(*status)
