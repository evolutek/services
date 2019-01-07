from math import pi, sqrt
import pygraphviz as pgv

class Node:

    def __init__(self, goal, parents, children, done, score):
        self.goal = goal
        self.parents = parents
        self.children = children
        self.done = done
        self.score = score

class Action:

    def __init__(self, trsl_speed, rot_speed, fct, args={}, avoid=True):
        self.trsl_speed = trsl_speed
        self.rot_speed = rot_speed
        self.fct = fct
        self.args = args
        self.avoid = avoid

    def make(self):
        self.fct(argsgoa)

class Goal:

    def __init__(x, y, theta=None, actions=None, score=0, robot_proximity=False):
        self.x = x
        self.y = y
        self.theta = theta
        self.actions = [] if actions is None else actions
        self.score = 0
        self.robot_proximity = robot_proximity
        self.done = False
        self.last_action = -1

class Goals:

    def __init__(self, file, color):
        # parse file

        self.start_x = 600
        self.start_y = 225 if color == 'yellow' else 2725
        self.theta = pi/2 if color == 'yellow' else -pi/2

        self.graph = {}

        # parse file

    def add_node(self, name, parents=None, children=None, goal=None, done=False, score=0):
        if parents is None:
            parents = []
        if children is None:
            children = []
        node = Node(goal, parents, children, done, score)
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
        for name, node in self.graph.items():
            if not node.done:
                parents_done= True
                for parent in node.parents:
                    if not self.graph[parent].done:
                        parents_done = False
                        break
                if parents_done:
                    l.append((name, node))
        return l

goals = Goals('test.json', 'green')
goals.add_node('Start', done=True)
goals.add_node('First', ['Start'])
goals.export_dot_file()
print(goals.get_available_goals())
