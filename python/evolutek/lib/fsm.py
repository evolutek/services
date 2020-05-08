from enum import Enum
from threading import Event
from traceback  import print_exc

class State:

    def __init__(self, state, fct):

        self. state = state
        self.fct = fct

    def run_state(self):

        print('[FSM] Running %s' % self.state.value)

        try:
            return self.fct()
        except Exception as e:

            print('[FSM] Error in state %s:' % (self.state.value))
            print_exc()
            return None

class Fsm:

    def __init__(self, states_enum):

        self.states_enum = states_enum

        self.states = {}
        self.transistions = {}

        self.error_state = None
        self.in_error = False

        self.running = None
        self.stopping = Event()

    def add_state(self, state, fct, prevs=None):
        if not state in self.states_enum:
            print('[FSM] Not possible state: %s' % state)
            return False

        if state in self.states:
            print('[FSM] State already registered: %s' % state.value)
            return False

        self.states[state] = State(state, fct)
        self.transistions[state] = prevs
        print('[FSM] State registered: %s' % state.value)
        return True

    def add_error_state(self, fct):
        self.error_state = State(self.states_enum.Error, fct)
        print('[FSM] Error state registered')

    def is_running(self):
        return not self.running is None

    def stop_fsm(self):
        if self.is_running():
            print('[FSM] Stopping FSM')
            self.stopping.set()

    def run_error(self):
        self.in_error = True
        self.running = self.error_state

        self.error_state.run_state()

        self.in_error = False

    # Will run on a thread
    def start_fsm(self, state):

        if not self.running is None:
            print('[FSM] Already running')

        if not state in self.states:
            print('[FSM] Not registered state')
            return False

        print('[FSM] Running')
        self.running = self.states[state]
        next = self.running.run_state()

        while not self.stopping.is_set():
            if next is None :
                self.run_error()
                break

            if not next in self.states:
                print('[FSM] Next not registered: %s' % next)
                self.run_error()
                break

            if not self.running.state in self.transistions[next]:
                print("[FSM] Can't go to this state: %s" % next)
                self.run_error()
                break

            self.running = self.states[next]
            next = self.running.run_state()

        self.stopping.clear()
        self.running = None
        print('[FSM] Stopped')
