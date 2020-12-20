from enum import Enum
import json
from math import pi

from evolutek.lib.map.point import Point


""" Avoid Strategy Enum """
class AvoidStrategy(Enum):
    Wait = 0
    Timeout = 1
    Skip = 2


# Action Class
# fct: action function
# args: action arguments
# avoid: whether avoidance need to be enable/disable
# avoid_strategy : strategy to use when avoiding
# score: scored points after action
# timeout: timeout to abort action after avoiding
class Action:

    def __init__(self, fct, args=None, avoid=True, avoid_strategy=AvoidStrategy.Wait, score=0, timeout=None):
        self.fct = fct
        self.args = args
        if not args is None and 'theta' in args and isinstance(args['theta'], str):
            args['theta'] = eval(args['theta'])

        # Optionals
        self.avoid = avoid
        self.avoid_strategy = avoid_strategy
        self.score = score
        self.timeout = timeout

    # Make action
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

    # Static method
    # Parse action from JSON
    @classmethod
    def parse(cls, action, ai):

        fct = None

        # Try get action from handler
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


# Goal class
# name: goal name
# position: position of the goal
# theta: needed theta to make goal
# score: scored points after making goal
# obstacles: obstcales to remove from map after making goal
# secondary_goal: goal to make after aborting this goal
# timeout: aboirt timeout if we can't make goal
class Goal:

    def __init__(self, name, position, theta=None, actions=None, score=0, obstacles=None, secondary_goal=None, timeout=None):
        self.name = name
        self.position = position
        self.actions = [] if actions is None else actions

        # Optionals
        self.theta = theta
        self.score = score
        self.obstacles = [] if obstacles is None else obstacles
        self.secondary_goal = secondary_goal
        self.timeout = timeout

    def __str__(self):
        actions = ""
        for action in self.actions:
            actions += "%s\n" % str(action)
        return "--- %s ---\nposition: %s\ntheta: %s\nscore: %d\nactions:\n%s\nsecondary_goal: %s\nobstacles: %s\ntimeout: %s\n"\
            % (self.name, self.position, str(self.theta), self.score, actions, self.secondary_goal, str(self.obstacles), str(self.timeout))

    # Static method
    # Parse goal from JSON
    @classmethod
    def parse(cls, goal, ai):

        theta = goal['theta'] if 'theta' in goal else None
        if isinstance(theta, str):
            theta = eval(theta)

        score = goal['score'] if 'score' in goal else 0

        position = Point(x=goal['position']['x'], y=goal['position']['y'])

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

        obstacles = goal['obstacles'] if 'obstacles' in goal else []
        secondary_goal = goal['secondary_goal'] if 'secondary_goal' in goal else None
        timeout = goal['timeout'] if 'timeout' in goal else None

        new = Goal(goal['name'], position, theta, actions, score, obstacles, secondary_goal, timeout)

        return new


# Strategy Class
# name: strategy name
# goals: strategy goals
# available: robot list fro which the strategy is available
# use_pathfinding: tell if the startegy use the pathfinding
class Strategy:
    def __init__(self, name, goals=None, available=None, use_pathfinding=True):
        self.name = name
        self.goals = [] if goals is None else goals
        self.available = [] if available is None else available
        self.use_pathfinding = use_pathfinding

    def __str__(self):
        s = "--- %s ---" % self.name
        for goal in self.goals:
            s += '\n%s' % goal
        s += "\navailable for:"
        for robot in self.available:
            s += '\n-->%s' % robot
        s += "\nuse pathfinding: " + str(self.use_pathfinding)
        return s

    # Static method
    # Parse strategy from JSON
    @classmethod
    def parse(cls, strategy, goals):

        _goals = []
        for goal in strategy['goals']:

            if not goal in goals:
                print('[GOALS] No existing goal')
                return None

            _goals.append(goal)

        use_pathfinding = strategy['use_pathfinding'] if 'use_pathfinding' in strategy else True

        new = Strategy(strategy['name'], _goals, strategy['available'], use_pathfinding)

        return new


# Goals manager class
class Goals:

    def __init__(self, file, ai, robot):
        # Starting position
        self.starting_position = None
        self.starting_theta = None
        self.strategies = []

        # Goals
        self.goals = {}

        # Current strategy
        self.current_strategy = None
        self.current = 0

        # Critical goal (ex: match end goal)
        self.critical_goal = None
        self.timeout_critical_goal = None

        # Parsed JSON
        self.parsed = self.parse(file, ai, robot)

        if self.parsed:
            self.reset(0)

    # Parse JSON
    def parse(self, file, ai, robot):

        # Read file
        data = None
        try:
            with open(file, 'r') as goals_file:
                data = goals_file.read()
        except Exception as e:
            print('[GOALS] Failed to read file: %s' % str(e))
            return False

        goals = json.loads(data)

        # Parse starting position
        try:
            pos = goals['starting_pos'][robot]
            self.starting_position = Point(x=pos['x'],
                                           y=pos['y'])
            self.starting_theta = pos['theta']
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

            if new.secondary_goal is not None:
                found = False
                for goal in goals['goals']:
                    if goal['name'] == new.secondary_goal:
                        found = True

                if not found:
                    print('[GOALS] Secondary goal not existing')
                    return False

            self.goals[new.name] = new

        # Parse strategies
        for strategy in goals['strategies']:

            try:
                new = Strategy.parse(strategy, self.goals)
            except Exception as e:
                print('[GOALS] Failed to parse strategy: %s' % str(e))
                return False

            if new is None:
                return False

            if robot in new.available:
                print('[GOALS] Adding %s strategy' % new.name)
                self.strategies.append(new)

        # Parse critical goal
        if 'critical_goal' in goals:
            try:
                self.critical_goal = goals['critical_goal']['goal']
                self.timeout_critical_goal = goals['critical_goal']['timeout']
            except Exception as e:
                print('[GOALS] Failed to parse critical goal: %s' % str(e))
                return False

            if not self.critical_goal in self.goals:
                print('[GOALS] Not existing critical goal: %s' % self.critical_goal)
                return False

        return True

    def __str__(self):
        s = "[Goals manager]\n"
        s += "-> Starting position\n"
        s += "x: %d\n" % self.starting_position.x
        s += "y: %d\n" % self.starting_position.y
        s += "theta: %f\n" % self.starting_theta
        s += "-> Goals\n"
        s += "Current Strategy: %s\n" % str(self.current_strategy.name)
        s += "Number Current Strategy: %d\n" % self.current
        s += "Critical goal: %s\n" % str(self.critical_goal)
        s += "Timeout Critical goal: %s\n" % str(self.timeout_critical_goal)
        for goal in self.goals:
            s += str(self.goals[goal])
        s += "-> Strategies\n"
        for strategy in self.strategies:
            s += str(strategy) + '\n'
        return s

    # Reset goals manager
    # index: index of the strategy to load
    def reset(self, index=None):

        if index is not None:

            if index < 0 or index >= len(self.strategies):
                print('[GOALS] Strategy index incorrect')
                return False

            self.current_strategy = self.strategies[index]

        self.current = 0

        return True

    # Get next goal
    def get_goal(self):
        if self.current >= len(self.current_strategy.goals):
            return None
        return self.goals[self.current_strategy.goals[self.current]]

    # Get secondary goal of a goal
    def get_secondary_goal(self, goal):
        return self.goals[goal]

    # Get critical goal
    def get_critical_goal(self):
        self.current = len(self.current_strategy.goals)
        return self.goals[self.critical_goal]

    # Mark current goal as finished
    def finish_goal(self):
        self.current += 1
