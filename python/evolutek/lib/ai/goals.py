from enum import Enum
import json
from math import pi

from evolutek.lib.map.point import Point
from evolutek.lib.utils.wrappers import event_waiter


""" Avoid Strategy Enum """
class AvoidStrategy(Enum):
    Wait = 'wait'
    Timeout = 'timeout'
    Skip = 'skip'


# Action Class
# fct: action function
# args: action arguments
# avoid: whether avoidance need to be enable/disable
# avoid_strategy : strategy to use when avoiding
# score: scored points after action
# timeout: timeout to abort action after avoiding
class Action:

    def __init__(self, fct, args=None, avoid_strategy=AvoidStrategy.Wait, score=0, timeout=None):
        self.fct = fct
        self.args = args
        if not args is None and 'theta' in args and isinstance(args['theta'], str):
            args['theta'] = eval(args['theta'])

        # Optionals
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
        s += '\n    -> avoid_strategy: ' + self.avoid_strategy.value
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

                if action['handler'] == 'robot':
                    fct = event_waiter(fct, ai.start_event, ai.stop_event, callback=ai.check_abort)


        except Exception as e:
            print('[GOALS] Failed to get fct in action %s: %s' % (action['fct'], str(e)))
            return None

        args = action['args'] if 'args' in action else None
        avoid_strategy = AvoidStrategy(action['avoid_strategy']) if 'avoid_strategy' in action else AvoidStrategy.Wait
        score = action['score'] if 'score' in action else 0
        timeout = action['timeout'] if 'timeout' in action else None

        if avoid_strategy == AvoidStrategy.Skip:
            args['skip'] = True
        elif avoid_strategy == AvoidStrategy.Timeout:
            args['timeout'] = timeout


        new = Action(fct, args=args, avoid_strategy=avoid_strategy, score=score, timeout=timeout)

        return new


# Goal class
# name: goal name
# position: position of the goal
# theta: needed theta to make goal
# score: scored points after making goal
# obstacles: obstcales to remove from map after making goal
# secondary_goal: goal to make after aborting this goal
# timeout: abort timeout if we can't make goal
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


# Starting pos Class
# name: starting pos name
# position: starting position
# theta: starting theta
# recal_side: recal side of the robot ("x" or "y")
# recal_sensor: used sensor during recal ("right" or "left")
class StartingPosition:

    def __init__(self, name, position, theta, recal_side, recal_sensor):
        self.name = name
        self.position = position
        self.theta = theta
        self.recal_side = recal_side
        self.recal_sensor = recal_sensor

    def __str__(self):
        s = "--- %s ---\n" % self.name
        s += "posisiton: %s\n" % self.position
        s += "theta: %s\n" % self.theta
        s += "recal side: %s\n" % self.recal_side
        s += "recal sensor: %s" % self.recal_sensor
        return s

    # Static method
    # Parse starting pos from JSON
    @classmethod
    def parse(cls, starting_point):

        position = Point(dict=starting_point["position"])

        theta = starting_point['theta']
        if isinstance(theta, str):
            theta = eval(theta)

        recal_side = starting_point["recal_side"]
        if not recal_side in ["x", "y"]:
            print('[GOALS] No existing recal side %s' % recal_side)
            return None

        recal_sensor = starting_point["recal_sensor"]
        if not recal_sensor in ["right", "left"]:
            print('[GOALS] No existing recal sensor %s' % recal_sensor)
            return None

        return StartingPosition(starting_point["name"], position, theta, recal_side, recal_sensor)


# Strategy Class
# name: strategy name
# goals: strategy goals
# available: robot list fro which the strategy is available
# use_pathfinding: tell if the strategy use the pathfinding
class Strategy:
    def __init__(self, name, starting_position, goals=None, available=None, use_pathfinding=True):
        self.name = name
        self.starting_position = starting_position
        self.goals = [] if goals is None else goals
        self.available = [] if available is None else available
        self.use_pathfinding = use_pathfinding

    def __str__(self):
        s = "--- %s ---" % self.name
        s += '\n%s' % self.starting_position
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
    def parse(cls, strategy, starting_positions, goals):

        if not strategy['starting_position'] in starting_positions:
            print('[GOALS] No existing starting position %s' % strategy['starting_position'])
            return None

        starting_position = starting_positions[strategy['starting_position']]

        _goals = []
        for goal in strategy['goals']:

            if not goal in goals:
                print('[GOALS] No existing goal %s' % goal)
                return None

            _goals.append(goal)

        use_pathfinding = strategy['use_pathfinding'] if 'use_pathfinding' in strategy else False

        new = Strategy(strategy['name'], starting_position, _goals, strategy['available'], use_pathfinding)

        return new


# Goals manager class
class Goals:

    def __init__(self, file, ai, robot):
        # Starting position
        self.starting_positions = {}
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

        # Parse starting positions
        for starting_position in goals['starting_positions']:
            try:
                new = StartingPosition.parse(starting_position)
                if new is None:
                    return False
                self.starting_positions[new.name] = new
            except Exception as e:
                print('[GOALS] Failed to parse starting position: %s' % str(e))
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
                new = Strategy.parse(strategy, self.starting_positions, self.goals)
            except Exception as e:
                print('[GOALS] Failed to parse strategy: %s' % str(e))
                return False

            if new is None:
                return False

            if robot in new.available:
                print('[GOALS] Adding %s strategy' % new.name)
                self.strategies.append(new)

        # Parse critical goal
        if 'critical_goals' in goals and robot in goals['critical_goals']:
            try:
                self.critical_goal = goals['critical_goals'][robot]['goal']
                self.timeout_critical_goal = goals['critical_goals'][robot]['timeout']
            except Exception as e:
                print('[GOALS] Failed to parse critical goal: %s' % str(e))
                return False

            if not self.critical_goal in self.goals:
                print('[GOALS] Not existing critical goal: %s' % self.critical_goal)
                return False

        return True

    def __str__(self):
        s = "[Goals manager]\n"
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

    def get_strategies(self):
        strats = {}
        for i in range(len(self.strategies)):
            strats[self.strategies[i].name] = i
        return strats

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
