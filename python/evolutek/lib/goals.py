from math import pi, sqrt
import pygraphviz as pgv

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
        self.fct(self.args)

class Goal:

    def __init__(x, y, theta=None, actions=None, score=0, robot_proximity=False, proprity=0, time=0):
        self.x = x
        self.y = y
        self.theta = theta
        self.actions = [] if actions is None else actions
        self.score = score
        self.robot_proximity = robot_proximity
        self.priority = priority
        self.done = False
        self.last_action = None

class Goals:

    def __init__(self, file, color, actuators, trajman):

        """Robot starting position"""
        self.start_x = 0
        self.start_y = 0 #if color == 'yellow' else 2725
        self.theta = 0 #if color == 'yellow' else -pi/2

        self.goals = []
        self.current = 0

        a = Action(actuators.open_arms)
        b = Actiob(actuators.close_arms)

        self.goals.append(Goal(0, 0, theta=0, actions=[a]))
        self.goals.append(Goal(0, 0, theta=0, actions=[b]))

        #self.graph = {}
        #self.add_node('Start', done=True)

        # parse file

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
        if self.current >= self.len(goals):
            return None
        return self.goals[self.current]

    def finish_goal(self):
        self.current += 1

if __name__ == "__main__":
    goals = Goals('test.json', 'green')
    goals.add_node('First', ['Start'])
    goals.export_dot_file()
    print(goals.get_available_goals())
