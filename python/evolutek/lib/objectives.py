from math import pi
import queue

class Task:

    def __init__(self, x, y, color, theta=None, speed=None, action=None, \
        action_param=None, not_avoid=False):
        self.x = x
        self.y = y if color == 'orange' else 3000 - y
        self.theta = theta if color == 'orange'else theta + pi
        self.action = action
        self.action_param = action_param
        self.speed = speed
        self.not_avoid = not_avoid

class Objective:

    def __init__(self, destination, tasks, ending=None):
        self.destination = destination
        self.tasks = tasks
        self.ending = ending if ending else destiantion

def push_cubes1(color):
    res = queue.Queue()
    res.put(Task(600,  2550, color))
    res.put(Task(350,  2550, color, not_avoid=True))
    return res

def push_cubes2(color):
    res = queue.Queue()
    res.put(Task(600,  2150, color))
    res.put(Task(350,  2160, color, not_avoid=True))
    return res

def push_button(color, actuators):
    res = queue.Queue()
    res.put(Task(350,  1930, color, theta=pi, not_avoid=True, func_ptr=actuators.move_arm, func_param=68))
    res.put(Task(240,  1930, color, not_avoid=True, speed=500))
    res.put(Task(245,  1930, color, not_avoid=True, func_ptr=actuators.move_arm, func_param=0, speed=500))
    return res

def get_strat(color, actuators):
    res = queue.Queue()
    res.put(Objective('bee', push_cubes1(color), 'construction'))
    res.put(Objective('distrib1', push_cubes2(color), 'interrupteur'))
    #res.put(Objective('interrupteur', push_button(color, actuators)))
    return res
