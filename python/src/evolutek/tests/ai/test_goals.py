from evolutek.lib.ai.goals import AvoidStrategy, Goals
from evolutek.lib.map.point import Point

from math import pi

##TODO: Optional goal
##TODO: Critical goal

class Test:

    tested = False

    def test(self, x, y, theta, timeout=None):
        print(timeout)
        return x == 1000 and y == 1000 and theta == -3 * pi / 4

class Test_Goals:

    def __init__(self):

        self.test = Test()
        self.sleeped = False
        self.goals = Goals('/etc/conf.d/tests_goals.json', self, 'pal')

        if not self.goals.parsed:
            print('[TEST] Failed to parse goals')
            return

        print('[TEST] Tested goals:')
        print(self.goals)

        print('[TEST] Starting tests')

        if self.goals.starting_position != Point(450, 225):
            print('[TEST Bad starting position: %s' % str(self.goals.starting_position))

        if self.goals.starting_theta != pi:
            print('[TEST Bad starting theta: %f' % str(self.goals.starting_theta))

        print('[TEST] Testing of a success: %s' % str(self.eval_a()))
        print('[TEST] Testing of b success: %s' % str(self.eval_b()))
        print('[TEST] Testing of strategies success: %s' % str(self.eval_strategies()))
        print('[TEST] Testing of critical goal success: %s' % str(self.eval_critical_goal()))
        print('[TEST] Testing of goals success: %s' % str(self.eval_goals()))

        print('[TEST] End testing')

    def eval_a(self):
        if not 'a' in self.goals.goals:
            print('[TEST] a not in goals')
            return False

        passed = True
        goal = self.goals.goals['a']

        if goal.name != 'a':
            print('[TEST] a has a bad name: %s' % goal.name)
            passed = False

        if goal.position != Point(0, 0):
            print('[TEST] a has a bad positon: %s' % str(goal.position))
            passed = False

        if not goal.theta is None:
            print('[TEST] a has a bad theta')
            passed = False

        if not goal.secondary_goal is None:
            print('[TEST] a has a bad optional_goal')
            passed = False

        if goal.score != 0:
            print('[TEST] a has a bad score: %d' % goal.score)
            passed = False

        if len(goal.actions) != 0:
            print('[TEST] a has a bad actions number: %d' % len(goal.actions))
            passed = False

        return passed

    def eval_b(self):

        if not 'b' in self.goals.goals:
            print('[TEST] b not in goals')
            return False

        passed = True
        goal = self.goals.goals['b']

        if goal.name != 'b':
            print('[TEST] b has a bad name: %s' % goal.name)
            passed = False

        if goal.position != Point(0, 500):
            print('[TEST] b has a bad positon: %s' % str(goal.positon))
            passed = False

        if goal.score != 42:
            print('[TEST] b has a bad score: %d' % goal.score)
            passed = False

        if goal.theta != pi:
            print('[TEST] b has a bad theta: %f' % goal.theta)
            passed = False

        if len(goal.actions) != 2:
            print('[TEST] b has a bad number of action: %d' % len(goal.actions))
            return False

        action = goal.actions[0]
        action.make()

        if not action.args is None:
            print('[TEST] sleep has a bad args: %s' % str(action.args))

        if not self.sleeped:
            print('[TEST] sleep action failed')
            passed = False

        if action.avoid_strategy != AvoidStrategy.Wait:
            print('[TEST] sleep action has bad avoid strategy: %s' % action.avoid_strategy.name)
            passed = False

        if action.score != 0:
            print('[TEST] sleep action has bad score: %d' % action.score)
            passed = False

        if action.timeout != None:
            print('[TEST] sleep action has bad timeout: %d' % action.timeout)

        action = goal.actions[1]

        if not action.make():
            print('[TEST] test action got bad args: %s' % str(action.args))
            passed = False

        if action.avoid_strategy != AvoidStrategy.Timeout:
            print('[TEST] test action has bad avoid strategy: %s' % action.avoid_strategy.name)
            passed = False

        if action.score != 21:
            print('[TEST] test action has bad score: %d' % action.score)
            passed = False

        if action.timeout != 42:
            print('[TEST] test action has bad timeout: %d' % action.timeout)

        if goal.secondary_goal != "secondary":
            print('[TEST] test goals has bad optional_goals: %s' % goal.optional)

        if goal.obstacles != ["lol1", "lol2"]:
            print('[TEST] test goals has bad obstacles: %s' % str(goal.obstacles))

        if goal.timeout != 42:
            print('[TEST] test goals has bad timeout: %d' % goal.timeout)

        return passed

    def eval_strategies(self):

        passed = True

        if len(self.goals.strategies) != 2:
            print('[TEST] Goals has a bad bumber of strategies: %d' % len(self.goals.strategies))
            return False

        # Test of first strategy
        strategy = self.goals.strategies[0]

        if strategy.name != 'A':
            print('[TEST Strategy A has a bad name: %s' % strategy.name)
            passed = False

        if len(strategy.goals) != 2:
            print('[TEST] Strategy A has a bad bumber of goal: %d' % len(strategy.goals))
            passed = False

        if not passed and strategy.goals[0] != 'a':
            print('[TEST] Strategy A has a bad first goal: %s' % strategy.goals[0])
            passed = False

        if not passed and strategy.goals[1] != 'b':
            print('[TEST] Strategy A has a bad second goal: %s' % strategy.goals[1])
            passed = False

        # Test of second strategy
        strategy = self.goals.strategies[1]

        if strategy.name != 'B':
            print('[TEST Strategy B has a bad name: %s' % strategy.name)
            passed = False

        if len(strategy.goals) != 2:
            print('[TEST] Strategy B has a bad bumber of goal: %d' % len(strategy.goals))
            passed = False

        if not passed and strategy.goals[0] != 'b':
            print('[TEST] Strategy B has a bad first goal: %s' % strategy.goals[0])
            passed = False

        if not passed and strategy.goals[1] != 'a':
            print('[TEST] Strategy B has a bad second goal: %s' % strategy.goals[1])
            passed = False

        return passed

    def eval_critical_goal(self):

        if self.goals.critical_goal != 'secondary':
            print('[TEST] Critical goal is not correct: %s' % self.goals.critical_goal)
            return False

        if self.goals.timeout_critical_goal != 1024:
            print('[TEST] Critical timeout is not correct: %s' % self.goals.timeout_critical_goal)
            return False

        return True

    def eval_goals(self):
        if self.goals.current_strategy.name != 'A':
            print('[TEST] Bad current strategy: %s' % self.goals.current_strategy.name)
            return False

        if self.goals.current != 0:
            print('[TEST] Bad current: %d' % self.goals.current)
            return False

        goal = self.goals.get_goal()
        if goal.name != 'a':
            print('[TEST] Bad getted goal: %s' % goal.name)
            return False

        self.goals.finish_goal()
        if self.goals.current != 1:
            print('[TEST] Bad current: %d' % self.goals.current)
            return False

        goal = self.goals.get_goal()
        if goal.name != 'b':
            print('[TEST] Bag getted goal: %s' % goal.name)
            return False

        self.goals.finish_goal()
        if self.goals.current != 2:
            print('[TEST] Bad current: %d' % self.goals.current)
            return False

        self.goals.reset(1)

        if self.goals.current_strategy.name != 'B':
            print('[TEST] Bad current strategy: %s' % self.goals.current_strategy.name)
            return False

        if self.goals.current != 0:
            print('[TEST] Bad current: %d' % self.goals.current)
            return False

        return True


    def sleep(self):
        self.sleeped = True
        print('[TEST] Sleep')

if __name__ == "__main__":
    Test_Goals()
