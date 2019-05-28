from enum import Enum
from math import pi, sqrt
#import pygraphviz as pgv
import json

from evolutek.lib.point import Point

class Avoid(Enum):
    Wait = 0
    Timeout = 1
    Skip = 2

"""
class Node:

    def __init__(self, goal, parents, children, done):
        self.goal = goal
        self.parents = parents
        self.children = children
        self.done = done
"""

""" CLASS """

class Action:

    def __init__(self, fct, args=None, avoid=True, avoid_strategy=Avoid.Wait, trsl_speed=None, rot_speed=None, score=0, mirror=False):
        self.fct = fct

        if args and 'theta' in args and isinstance(args['theta'], str):
            args['theta'] = eval(args['theta'])

        if isinstance(avoid_strategy, str):
            avoid_strategy = eval(avoid_strategy)

        # mirror
        if args and mirror and 'y' in args:
            args['y'] = 3000 - args['y']
        if args and mirror and 'theta' in args:
            args['theta'] = 0 - args['theta']

        self.args = args
        self.avoid = avoid
        self.avoid_strategy = avoid_strategy
        self.trsl_speed = trsl_speed
        self.rot_speed = rot_speed
        self.score = score

    def make(self):
        if not self.args is None:
            self.fct(**self.args)
        else:
            self.fct()

    def __str__(self):
        s = str(self.fct)
        s += '\n    -> args: ' + str(self.args)
        s += '\n    -> avoid: ' + str(self.avoid)
        s += '\n    -> avoid_strategy: ' + str(self.avoid_strategy)
        s += '\n    -> score: ' + str(self.score)
        return s

class Goal:

    def __init__(self, name, path, theta=None, actions=None, score=0, robot_proximity=False, priority=0, time=0, mirror=False):
        self.name = name
        self.path = []
        for point in path:
            self.path.append({"x" : point['x'], "y": 3000 - point['y'] if mirror else point['y']})
        #lcl_theta = path.theta
        #if isinstance(theta, str):
        #    lcl_theta = eval(theta)
        #if not theta is None and mirror:
        #    lcl_theta = 0 - lcl_theta
        #lcl_theta = path.y if not mirror else 3000 - path.y
        #self.path.append(Point(path.x, path.y, theta=lcl_theta))


        self.theta = theta
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
        return "---%s---\nscore: %d\nactions:\n%s"\
            % (self.name, self.score, actions)

""" STRATS FOR TESTS """
##TODO: RM
def get_simple_strategy():
    l = []
    l.append(Goal(Point(1325, 225)))
    l.append(Goal(Point(1325, 500, theta=pi)))
    l.append(Goal(Point(750, 450)))
    l.append(Goal(Point(750, 650)))
    l.append(Goal(Point(450, 750)))
    l.append(Goal(Point(450, 250)))
    l.append(Goal(Point(750, 1350)))
    l.append(Goal(Point(1250, 1350)))
    l.append(Goal(Point(1050, 1000)))
    l.append(Goal(Point(550, 400)))
    return l

def test_avoid_strategy(mirror=False):
    l = []
    for i in range(20):
        l.append(Goal(Point(600, 1250), mirror=mirror))
        l.append(Goal(Point(600, 400), mirror=mirror))

    return l

def palet_strategy(cs, mirror=False):
    l = []
    l.append(Goal(Point(1020, 900), mirror=mirror, actions=[
        Action(cs.trajman['pal'].goto_xy, args={'x': 1270, 'y': 900}, avoid=False),
        Action(cs.trajman['pal'].goto_theta, args={'theta': 0}, avoid=False),
        Action(cs.actuators['pal'].get_palet, avoid=False),
        Action(cs.trajman['pal'].goto_theta, args={'theta': -pi/2}, avoid=False),
        Action(cs.trajman['pal'].goto_xy, args={'x': 1270, 'y': 600}),
        Action(cs.trajman['pal'].goto_theta, args={'theta': 0}, avoid=False),
        Action(cs.actuators['pal'].get_palet, avoid=False)
    ]))

    return l

def goldenium_strat(cs, mirror=False):
    l = []
    l.append(Goal(Point(300, 1635, theta=0), mirror=mirror, actions=[]))
    l.append(Goal(Point(150,1635, theta=0), mirror=mirror, actions=[
        Action(cs.actuators['pal'].push_ejecteur),
        Action(cs.actuators['pal'].reset_ejecteur)
    ]))
    return l

def test_wall_evit(mirror=False):
    l = []
    for i in range(10):
        l.append(Goal(Point(300, 750), mirror=mirror))
        l.append(Goal(Point(1350, 750), mirror=mirror))
    return l

def exp_strategy(cs, mirror=False):
    l = []
    l.append(Goal(Point(600, 225), mirror=mirror, actions=[
        Action(cs.trajman['pal'].goto_xy, args={'x': 270, 'y': 225}, avoid=False, mirror=mirror),
        Action(cs.actuators['pal'].activate_exp, avoid=False, mirror=mirror)
    ], score=40))
    return l


""" Goals manager """
##TODO: add name
class Goals:

    def __init__(self, file, mirror, cs):
        """Robot starting position"""
        self.start_x = 600
        self.start_y = 225 if not mirror else 2775
        self.start_theta = pi

        self.goals = []
        self.current = 0

        self.file = "/etc/conf.d/goals_files/" + file
        self.cs = cs

        self.reset(mirror)

        print(self)
        #self.graph = {}
        #self.add_node('Start', done=True)

    def __str__(self):
        s = "start:\n"
        s += "->x: %d\n" % self.start_x
        s += "->y: %d\n" % self.start_y
        s += "->theta: %f\n" % self.start_theta
        for goal in self.goals:
            s += str(goal)
        return s

    def parse(self, mirror=False):
        with open(self.file, 'r') as goal_file:
            data = goal_file.read()

        goals = json.loads(data)

        # Parse start point
        try:
            self.start_x = goals['start']['x']
            self.start_y = goals['start']['y']
            self.start_theta = goals['start']['theta']
            if isinstance(self.start_theta, str):
                self.start_theta = eval(self.start_theta)
        except Exception as e:
            print('Failed to parse start point: %s' % str(e))
            return False
        if mirror:
            self.start_y = 3000 - self.start_y
            self.start_theta = 0 - self.start_theta

        # Parse goals
        result = []
        for goal in goals['goals']:

            # Check if goal is correct
            if not 'name' in goal:
                print('Error in parsing goal: Missing name')
                return False

            if not 'path' in goal:
                print('Error in parsing goal %s: Missing path' % goal['name'])
                return False

            for point in goal['path']:
                if not 'x' in point:
                    print('Error in parsing path in goal %s: Missing x' % goal['name'])
                if not 'y' in point:
                    print('Error in parsing path in goal %s: Missing y' % goal['name'])

            # Parse actions
            actions = []
            if 'actions' in goal:
                for action in goal['actions']:
                    if action['name'] not in goals['actions']:
                        print('Failed to get action in goal %s: Missing action: %s' % (goal['name'],action['name']))
                        return False
                    action_instance = dict(goals['actions'][action['name']])
                    if not 'fct' in action_instance:
                        print('Error in parsing action in goal %s: Missing fct' % goal['name'])
                        return False

                    # Get instance of fct via CellaservProxy (cs.service['id'].fct)
                    try:
                        fct = getattr(getattr(self.cs, action_instance['service'])[action_instance['id']], action_instance['fct'])
                    except Exception as e:
                        print('Failed to get fct in action %s: %s' % (action['name'], str(e)))

                    # Remove service attributes
                    del action_instance['service']
                    del action_instance['id']
                    del action_instance['fct']

                    # Remove name insinde action
                    del action['name']

                    actions.append(Action(fct, **action, **action_instance, mirror=mirror))

            goal['actions'] = actions
            result.append(Goal(**goal, mirror=mirror))

        self.goals = result
        return True

    def reset(self, mirror):
        self.goals = []
        self.current = 0
        #self.goals = get_simple_strategy()
        #self.goals = test_avoid_strategy(mirror)
        #self.goals = palet_strategy(self.cs, mirror)
        #self.goals = test_wall_evit(mirror)
        #self.goals = goldenium_strat(self.cs)
        #self.goals = exp_strategy(self.cs, mirror)
        #return True

        return self.parse(mirror)

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
        self.push_ejecteur = 'push_ejecteur'
        self.reset_ejecteur = 'reset_ejecteur'
        self.drop_goldenium = 'drop_goldenium'
        self.get_goldenium = 'get_goldenium'
        self.get_blue_palet = 'get_blue_palet'
        self.drop_blue_palet = 'drop_blue_palet'

class fake_trajman:
    def __init__(self):
        self.goto_xy = 'goto_xy'
        self.goto_theta = 'goto_theta'
        self.move_trsl = 'move_trsl'

class fake_cs:
    def __init__(self):
        self.actuators = {'pal': fake_actuators()}
        self.trajman = {'pal': fake_trajman()}

if __name__ == "__main__":
    goals = Goals('simple_strategy.json', True, fake_cs())
    #goals.add_node('First', ['Start'])
    #goals.export_dot_file()
    #print(goals.get_available_goals())
