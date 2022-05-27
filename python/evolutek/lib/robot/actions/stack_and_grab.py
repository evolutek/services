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

def get_stack_pos(id, color_name):
    color = Color.get_by_name(color_name)
    for stack in STACKS:
        if stack.id == int(id) and stack.color == color:
            return stack.pos
    return None

@if_enabled
@async_task
def stack_and_grab(self, id = 1, color_name = "Pink"):
    stack_pos = get_stack_pos(id, color_name)
    robot_pos = Point(dict=self.trajman.get_position())

    if (len(HOLDING) > 0):
        status = RobotStatus.get_status(self.elevator_move("High", async_task=False))
        print(status)
    else:
        status = self.clamp_open(async_task=False)
        print(status)
        sleep(0.3)
        status = RobotStatus.get_status(self.elevator_move("Low", async_task=False))
        print(status)

    sleep(0.5)
    status = RobotStatus.get_status(self.goth(robot_pos.compute_angle(stack_pos), async_task=False, mirror=False))
    print(status)
    sleep(0.5)

    if (len(HOLDING) > 0):
        go_to_point = robot_pos.compute_offset_point(stack_pos, -30)
        status = self.goto_avoid(x=go_to_point.x, y=go_to_point.y, async_task=False, mirror=False, timeout=10)
        print(status)
        sleep(0.5)
        status = self.clamp_open(async_task=False)
        sleep(0.5)

        #recule
        go_to_point = robot_pos.compute_offset_point(stack_pos, -80)
        status = self.goto_avoid(x=go_to_point.x, y=go_to_point.y, mirror=False, async_task=False, timeout=10)
        if RobotStatus.get_status(status) != RobotStatus.Reached:
            return RobotStatus.return_status(RobotStatus.get_status(status))
        sleep(0.5)
        status = self.elevator_move("Low", async_task=False)

    sleep(0.5)
    go_to_point = robot_pos.compute_offset_point(stack_pos, -20)
    status = self.goto_avoid(x=go_to_point.x, y=go_to_point.y, async_task=False, mirror=False, timeout=10)
    if RobotStatus.get_status(status) != RobotStatus.Reached:
        return RobotStatus.return_status(RobotStatus.get_status(status))
    sleep(0.5)
    status = self.clamp_close(async_task=False)
    sleep(0.5)
    for i in range (3):
        self.HOLDING.append(color_name)

    print(f"HOLDING : {HOLDING}")
    return RobotStatus.return_status(RobotStatus.Done, score=3)

def grab_first_stacks(self, first_id = 1, first_color_name = "Pink"):
    # THIS METHOD WILL BE REMOVED EVENTUALLY
    # DONT USE THIS IN A MATCH
    stack_and_grab(self, first_id, "Pink", async_task=False)
    stack_and_grab(self, first_id, "Yellow", async_task=False)
    return stack_and_grab(self, first_id, "Brown", async_task=False)

def back_to_base(self):
    robot_pos = Point(dict=self.trajman.get_position())
    base_pos = Point(dict=self.mirror_pos(275, 225))

    status = RobotStatus.get_status(self.goth(robot_pos.compute_angle(base_pos), async_task=False))
    print(status)

    go_to_point = robot_pos.compute_offset_point(base_pos, 50)
    status = self.goto_avoid(x=go_to_point.x, y=go_to_point.y, mirror=False, async_task=False, timeout=10)
    if RobotStatus.get_status(status) != RobotStatus.Reached:
        return RobotStatus.return_status(RobotStatus.Failed)
    sleep(0.5)

    status = RobotStatus.get_status(self.goth(0, async_task=False))
    print(status)
    sleep(0.5)

    return RobotStatus.return_status(RobotStatus.Done)