#!/usr/bin/env python3

from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service

from evolutek.lib.fsm import Fsm
from evolutek.lib.goals import Goals, AvoidStrategy
from evolutek.lib.settings import ROBOT

from enum import Enum
from threading import Event, Thread, Timer

class States(Enum):
    Setup = "Setup"
    Waiting = "Waiting"
    Selecting = "Selecting"
    Making = "Making"
    Ending = "Ending"
    Error = "Error"

# TODO :
# - states
# - interface
# - secondary goal
# - critical goal
# - manage action avoid strategies
# - set strategy
# - sleep

@Service.require('config')
@Service.require('actuators')
@Service.require('trajman')
@Service.require('robot')
class AI(Service):

    def __init__(self):

        print('[AI] Init')

        self.cs = CellaservProxy()
        self.actuators = self.cs.actuators[ROBOT]
        self.trajman = self.cs.trajman[ROBOT]
        self.robot = self.cs.robot[ROBOT]

        self.red_led = create_gpio(23, 'red led', dir=True, type=GpioType.RPI)
        self.green_led = create_gpio(24, 'green led', dir=True, type=GpioType.RPI)

        self.tirette = create_gpio(17, 'tirette', dir=False, edge=Edge.FALLING, type=GpioType.RPI)
        self.tirette.auto_refresh(refresh=0.05, callback=self.publish)

        self.fsm = Fsm(States)
        self.fsm.add_state(States.Setup, self.setup, prevs=[States.Waiting, States.Ending])
        self.fsm.add_state(States.Waiting, self.waiting, prevs=[States.Setup])
        self.fsm.add_state(States.Selecting, self.selecting, prevs=[States.Waiting, States.Making])
        self.fsm.add_state(States.Making, self.making, prevs=[States.Selecting, States.Making])
        self.fsm.add_state(States.Ending, self.ending, prevs=[States.Setup, States.Waiting, States.Selecting, States.Making])
        self.fsm.add_error_state(self.error)

        self.goals = Goals(file='/etc/conf.d/strategies.json', ai=self, robot=ROBOT)

        if not self.goals.parsed:
            print('[AI] Failed to parsed goals')
            Thread(target=self.fsm.run_error).start()

        else:
            print('[AI] Ready')
            print(self.goals)

            self.use_pathfinding = self.goals.current_strategy.use_pathfinding

            Thread(target=self.fsm.start_fsm, args=[States.Setup]).start()


        """ SETUP """
        def setup(self):
            # TODO :
            # - reset services
            # - reset variables
            # - set pos / calibration
            return States.Waiting

        """ WAITING """
        def waiting(self):
            # TODO :
            # - wait for reset or match start
            # - launch timer for critical goal
            # - return Selectig or Setup
            pass

        """ SELECTING """
        def selecting(self):
            # TODO :
            # - check for match end
            # - select next goal (critical, secondary or next)
            # - quit if now goal
            return States.Making

        """ MAKING """
        def making(self):
            # TODO :
            # - check for critical goal
            # - goto pos
            # - goto theta
            # - make actions
            # - publish score
            # Think to check for critical goal or math end
            return States.Selecting

        """ ENDING """
        def ending(self):
            # TODO :
            # - stop timer
            # - disable services
            # - clear all
            # - wait for reset

            return States.Setup
