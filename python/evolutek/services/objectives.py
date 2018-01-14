#from cellaserv import CellaservProxy
from math import pi

class Objective:

    def __init__(self, _x = None, _y = None, _speed = None, _theta = None, _action = None):
        self.x = _x
        self.y = _y
        self.speed = _speed
        self.theta = _theta
        self.action = _action

    def __str__(self):
        if not self.action:
            return "move: x=" + str(self.x) + " y=" + str(self.y)\
                    + " speed=" + str(self.speed) + " theta=" + str(self.theta)
        else:
            return "action"

class Objectives:

    def __init__(self, color = "green"):
        self.objectives = []
        #self.actuators = CellaserProxy().actuactors['pal']
        if color == "green":
            print("Set Green Objectives")
            self.set_green()
        else:
            print("Set Orange Objectives")
            self.set_orange()

    def print_objectives(self):
        for objective in self.objectives:
            print(str(objective))

    def add_move(self, x, y, speed = None, theta = None):
        objective = Objective(_x = x, _y = y, _speed = speed, _theta = theta)
        self.objectives.append(objective)

    def add_action(self, action):
        objective = Objective(_action = action)
        self.objectives.append(objective)

    def is_empty(self):
        return self.objectives == []

    def pop_objective(self):
        return self.objectives.pop()

    def push_objective(self, objective):
        self.objectives.insert(0, objective)

    """ Objectives """

    def set_green(self):
        self.add_move(1500, 1000)

    def set_orange(self):
        self.add_move(1500, 1000)
