from math import pi, sqrt
#import pygraphviz as pgv
import json
from collections import namedtuple

class Node:

    def __init__(self, goal, parents, children, done):
        self.goal = goal
        self.parents = parents
        self.children = children
        self.done = done

class Action:

    def __init__(self, fct, args={}, avoid=True, trsl_speed=None, rot_speed=None):
        self.fct = fct
        self.args = args
        self.avoid = avoid
        self.trsl_speed = trsl_speed
        self.rot_speed = rot_speed

    def make(self):
        self.fct()

class Goal:

    def __init__(self, x, y, theta=None, actions=None, score=0, robot_proximity=False, priority=0, time=0):
        self.x = x
        self.y = y
        self.theta = theta
        self.actions = [] if actions is None else actions
        self.score = score
        self.robot_proximity = robot_proximity
        self.priority = priority
        self.done = False
        self.last_action = None

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


def palet_strategy(actuators):
    l = []
    l.append(Goal(1300, 600, theta=0, actions=[
        Action(actuators.get_palet)
    ]))
    l.append(Goal(1300, 900, theta=0, actions=[
        Action(actuators.get_palet)
    ]))
    
    return l

class Goals:

    def __init__(self, file, color, actuators, trajman):

        """Robot starting position"""
        self.start_x = 600
        self.start_y = 225
        self.theta = 0

        self.goals = []
        self.current = 0


        self.reset(actuators)
        #self.graph = {}
        #self.add_node('Start', done=True)

    def parse(self, filename):
        with open(filename, 'r') as goal_file:
            data = goal_file.read()

        goals = json.loads(data)

        self.start_x = goals['start']['x']
        self.start_y = goals['start']['y']
        self.theta = goals['start']['theta']
        result = []
        for g in goals['goals']:
            goal = Goal(g['x'], g['y'])
            if 'theta' in g:
                goal.theta = g['theta']
            result.append(goal)

        self.goals = result

    def reset(self, actuators):
        #self.parse("/root/pls/evolutek/lib/goals_files/good_test.json")
        #self.goals = get_simple_strategy()
        #self.goals = test_avoid_strategy()
        self.goals = palet_strategy(actuators)
        self.current = 0
        
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

    def get_goal(self):
        if self.current >= len(self.goals):
            return None
        return self.goals[self.current]

    def finish_goal(self):
        print("[GOAL] Finished goal " + str(self.current))
        self.current += 1

if __name__ == "__main__":
    goals = Goals('test.json', 'green')
    goals.add_node('First', ['Start'])
    goals.export_dot_file()
    print(goals.get_available_goals())
