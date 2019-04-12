from math import pi, sqrt
#import pygraphviz as pgv
import json
from collections import namedtuple

"""
class Node:

    def __init__(self, goal, parents, children, done):
        self.goal = goal
        self.parents = parents
        self.children = children
        self.done = done
"""

class Action:

    def __init__(self, fct, args={}, avoid=True, trsl_speed=None, rot_speed=None, mirror=False):
        self.fct = fct

        if 'theta' in args:
            args['theta'] = eval(args['theta'])

        # mirror
        if mirror and 'y' in args:
            args['y'] = 3000 - y
        if mirror and 'theta' in args:
            args['theta'] = 0 - args['theta']

        self.args = args
        self.avoid = avoid
        self.trsl_speed = trsl_speed
        self.rot_speed = rot_speed

    def make(self):
        if not self.args is None:
            self.fct(**self.args)
        self.fct()

    def __str__(self):
        return str(self.fct)

class Goal:

    def __init__(self, x, y, theta=None, actions=None, score=0, robot_proximity=False, priority=0, time=0, mirror=False):
        self.x = x

        #mirror
        self.y = y if not mirror else 3000 - y
        self.theta = theta
        if isinstance(theta, str):
            self.theta = eval(theta)
        if not theta is None and mirror:
            self.theta = 0 - self.theta

        self.actions = [] if actions is None else actions
        self.score = score
        self.robot_proximity = robot_proximity
        self.priority = priority
        self.done = False
        self.last_action = None

    def __str__(self):
        actions = ""
        for action in self.actions:
            actions += "->%s\n" % str(action)
        return "x: %f\ny: %f\ntheta: %s\nscore: %d\nactions:\n%s"\
            % (self.x, self.y, str(self.theta), self.score, actions)

""" STRATS FOR TESTS """
##TODO: RM
def get_simple_strategy():
    l = []
    l.append(Goal(1325, 225))
    l.append(Goal(1325, 500, theta=pi))
    l.append(Goal(750, 450))
    l.append(Goal(750, 650))
    l.append(Goal(450, 750))
    l.append(Goal(450, 250))
    l.append(Goal(750, 1350))
    l.append(Goal(1250, 1350))
    l.append(Goal(1050, 1000))
    l.append(Goal(550, 400))
    return l

def test_avoid_strategy():
    l = []
    for i in range(100):
        l.append(Goal(600, 1250))
        l.append(Goal(600, 225))

    return l

def palet_strategy(cs, mirror=False):
    l = []
    l.append(Goal(1270, 600, theta=0, mirror=mirror, actions=[
        Action(cs.actuators['pal'].get_palet)
    ]))
    l.append(Goal(1270, 900, theta=0, mirror=mirror, actions=[
        Action(cs.actuators['pal'].get_palet)
    ]))
    l.append(Goal(1270, 225, theta=0, mirror=mirror, actions=[]))
    l.append(Goal(1730, 225, theta=0, mirror=mirror, actions=[
        Action(cs.actuators['pal'].get_palet)
    ]))

    return l

##TODO: add name
class Goals:

    def __init__(self, file, mirror, cs):

        """Robot starting position"""
        self.start_x = 600
        self.start_y = 225
        self.theta = 0

        self.goals = []
        self.current = 0

        self.file = "/etc/conf.d/goals_files/" + file
        self.cs = cs

        self.reset(mirror)

        #self.graph = {}
        #self.add_node('Start', done=True)

    def __str__(self):
        s = ""
        for goal in self.goals:
            s += "goal:\n%s" % str(goal)
        return s

    def parse(self, mirror=False):
        with open(self.file, 'r') as goal_file:
            data = goal_file.read()

        goals = json.loads(data)

        # Parse start point
        try:
            self.start_x = goals['start']['x']
            self.start_y = goals['start']['y']
            self.theta = goals['start']['theta']
            if isinstance(self.theta, str):
                self.theta = eval(self.theta)
        except Exception as e:
            print('Failed to parse start point: %s' % str(e))
            return False
        if mirror:
            self.start_y = 3000 - self.start_y
            self.theta = 0 - self.theta

        # Parse goals
        result = []
        for goal in goals['goals']:

            # Check if goal is correct
            if not 'x' in goal or not 'y' in goal:
                print('Error in parsing goal: Missing coords')
                return False

            # Parse actions
            actions = []
            if 'actions' in goal:
                for action_name in goal['actions']:
                    if action_name not in goals['actions']:
                        print('Failed to get action: Missing action')
                        return False
                    action = dict(goals['actions'][action_name])
                    print(goals['actions'])
                    if not 'fct' in action:
                        print('Error in parsing action in goal: Missing fct')
                        return False

                    # Get instance of fct via CellaservProxy (cs.service['id'].fct)
                    try:
                        fct = getattr(getattr(self.cs, action['service'])[action['id']], action['fct'])
                    except Exception as e:
                        print('Failed to get fct: %s' % str(e))
                    del action['service']
                    del action['id']
                    del action['fct']
                    actions.append(Action(fct, **action))

            goal['actions'] = actions
            result.append(Goal(**goal, mirror=mirror))

        self.goals = result

        #print(self)

        return True

    def reset(self, mirror):
        print(self.parse(mirror))
        #self.goals = get_simple_strategy()
        #self.goals = test_avoid_strategy()
        #self.goals = palet_strategy(self.cs, mirror)
        self.current = 0

    """
    def add_node(self, name, parents=None, children=None, goal=None, done=False):
        if parents is None:
            parents = []
        if children is None:
            children = []
        node = Node(goal, parents, children, done)
        self.graph[name] = node
        for parent in parents:
            self.graph[parent].children.append(name)
        for child in children:
            self.graph[child].parents.append(name)

    def export_dot_file(self):
        g = pgv.AGraph()
        for name, node in self.graph.items():
            g.add_node(name, fillcolor='green' if node.done else 'white', style='filled')
            for child in node.children:
                g.add_edge(name, child)
        with open('graph.dot', 'w') as file:
            file.write(str(g))

    def get_available_goals(self):
        l = []
        # Return available goals in the graph
        return l
    """

    def get_goal(self):
        if self.current >= len(self.goals):
            return None
        return self.goals[self.current]

    def finish_goal(self):
        print("[GOAL] Finished goal " + str(self.current))
        self.current += 1

""" FOR STATIC TESTS """
##TODO: RM
class fake_actuators:
    def __init__(self):
        self.get_palet = 'get_palet'
        self.open_arms = 'open_arms'
        self.close_arms = 'close_arms'

class fake_cs:
    def __init__(self):
        self.actuators = fake_actuators()

if __name__ == "__main__":
    goals = Goals('get_palet.json', True, fake_cs())
    #goals.add_node('First', ['Start'])
    #goals.export_dot_file()
    #print(goals.get_available_goals())
