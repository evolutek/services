from enum import Enum
import json
from math import pi

from evolutek.lib.map.point import Point

##TODO: Critial goal
##TODO: Tests
##TODO: Check if position is possible
##TODO: Update UML

""" Avoid Strategy Enum """
class AvoidStrategy(Enum):
    Wait = 0
    Timeout = 1
    Skip = 2


""" Action Class """
class Action:

    def __init__(self, fct, args=None, avoid=True, avoid_strategy=AvoidStrategy.Wait, score=0, timeout=None):
        self.fct = fct
        self.args = args
        if not args is None and 'theta' in args:
            args['theta'] = eval(args['theta'])
        self.avoid = avoid
        self.avoid_strategy = avoid_strategy
        self.score = score
        self.timeout = timeout

    def make(self):
        r = self.score
        if not self.args is None:
            r = self.fct(**self.args)
        else:
            r = self.fct()
        return r

    def __str__(self):
        s = str(self.fct)
        s += '\n    -> args: ' + str(self.args)
        s += '\n    -> avoid: ' + str(self.avoid)
        s += '\n    -> avoid_strategy: ' + str(self.avoid_strategy)
        s += '\n    -> score: ' + str(self.score)
        s += '\n    -> timeout: ' + str(self.timeout)
        return s

    @classmethod
    def parse(cls, action, ai):

        fct = None
        try:
            fct = None
            if not 'handler' in action:
                fct = getattr(ai, action['fct'])
            else:
                fct = getattr(getattr(ai, action['handler']), action['fct'])
        except Exception as e:
            print('[GOALS] Failed to get fct in action %s: %s' % (action['fct'], str(e)))
            return None

        args = action['args'] if 'args' in action else None
        avoid = action['avoid'] if 'avoid' in action else True
        avoid_strategy = eval(action['avoid_strategy']) if 'avoid_strategy' in action else AvoidStrategy.Wait
        score = action['score'] if 'score' in action else 0
        timeout = action['timeout'] if 'timeout' in action else None

        new = Action(fct, args=args, avoid=avoid,\
                     avoid_strategy=avoid_strategy, score=score, timeout=timeout)

        return new


""" Goal Class """
class Goal:

    def __init__(self, name, position, theta=None, actions=None, score=0, optional_goal=None):
        self.name = name
        self.position = position
        self.theta = theta
        self.actions = [] if actions is None else actions
        self.score = score
        self.optional_goal = optional_goal

    def __str__(self):
        actions = ""
        for action in self.actions:
            actions += "%s\n" % str(action)
        return "--- %s ---\nposition: %s\ntheta: %s\nscore: %d\nactions:\n%s"\
            % (self.name, self.position, str(self.theta), self.score, actions)

    @classmethod
    def parse(cls, goal, ai):

        theta = goal['theta'] if 'theta' in goal else None
        if isinstance(theta, str):
            theta = eval(theta)

        score = goal['score'] if 'score' in goal else 0
        optional_goal = goal['optional'] if 'optional' in goal else None

        position = Point(x=goal['position']['x'],
                                       y=goal['position']['y'])

        actions = []
        if 'actions' in goal:
            for action in goal['actions']:

                try:
                    new = Action.parse(action, ai)
                except Exception as e:
                    print('[GOALS] Fails to parse action: %s' % str(e))
                    return None

                if new is None:
                    return None

                actions.append(new)

        new = Goal(goal['name'], position, theta, actions, score, optional_goal)

        return new


""" Strategy Class """
class Strategy:
    def __init__(self, name, goals=None):
        self.name = name
        self.goals = [] if goals is None else goals

    def __str__(self):
        s = "--- %s ---" % self.name
        for goal in self.goals:
            s += '\n%s' % goal
        return s

    @classmethod
    def parse(cls, strategy, goals):

        _goals = []
        for goal in strategy['goals']:

            if not goal in goals:
                print('[GOALS] No existing goal')
                return None

            _goals.append(goal)

        new = Strategy(strategy['name'], _goals)

        return new


""" Goals Manager """
class Goals:

    def __init__(self, file, ai):
        # Starting position
        self.starting_position = None
        self.starting_theta = None
        self.strategies = []

        # Goals
        self.goals = {}

        # Current strategy
        self.current_strategy = []
        self.current = 0

        # Critical goal
        self.critical_goal = None
        self.timeout_critical_goal = None

        self.parse(file, ai)

        self.reset(0)

    def parse(self, file, ai):

        # Read file
        data = None
        with open(file, 'r') as goals_file:
            data = goals_file.read()

        if data is None:
            print('[GOALS] Failed to read file')
            return False

        goals = json.loads(data)

        # Parse starting position
        try:
            self.starting_position = Point(x=goals['start']['x'],
                                           y=goals['start']['y'])
            self.starting_theta = goals['start']['theta']
            if isinstance(self.starting_theta, str):
                self.starting_theta = eval(self.starting_theta)

        except Exception as e:
            print('[GOALS] Failed to parse start point: %s' % str(e))
            return False

        # Parse goals
        for goal in goals['goals']:

            try:
                new = Goal.parse(goal, ai)
            except Exception as e:
                print('[GOALS] Failed to parse goal: %s' % str(e))
                return False

            if new is None:
                return False

            self.goals[new.name] = new

        # Parse
        for strategy in goals['strategies']:

            try:
                new = Strategy.parse(strategy, self.goals)
            except Exception as e:
                print('[GOALS] Failed to parse strategy: %s' % str(e))
                return False

            if new is None:
                return False

            self.strategies.append(new)

        return True

    def __str__(self):
        s = "[Goals manager]\n"
        s += "-> Starting position\n"
        s += "x: %d\n" % self.starting_position.x
        s += "y: %d\n" % self.starting_position.y
        s += "theta: %f\n" % self.starting_theta
        s += "-> Goals\n"
        for goal in self.goals:
            s += str(self.goals[goal])
        s += "-> Strategies\n"
        for strategy in self.strategies:
            s += str(strategy) + '\n'
        return s

    def reset(self, index):
        if index < 0 or index >= len(self.strategies):
            print('[GOALS] Strategy index incorrect')

        self.current_strategy = self.strategies[index]
        self.current = 0

    def get_goal(self):
        if self.current >= len(self.current_strategy.goals):
            return None
        return self.goals[self.current_strategy.goals[self.current]]

    def finish_goal(self):
        self.current += 1
