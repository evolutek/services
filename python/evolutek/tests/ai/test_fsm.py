from evolutek.lib.ai.fsm import Fsm

from enum import Enum
from threading import Event, Thread
from time import sleep

class States(Enum):
    state1 = 'state1'
    state2 = 'state2'
    state3 = 'state3'
    Error = 'error'

class Test_Fsm:

    def __init__(self):

        print('[TEST_FSM] Initializing FSM test')

        self.in_state = Event()
        self.stop = Event()

        self.fsm = Fsm(States)
        self.fsm.add_state(States.state1, self.state1)
        self.fsm.add_state(States.state2, self.state2, prevs=[States.state1])
        self.fsm.add_state(States.state3, self.state3, prevs=[States.state2])
        self.fsm.add_error_state(self.error)

        print('[TEST_FSM] Strating test')
        Thread(target=self.fsm.start_fsm, args=[States.state1]).start()

        succeed = True
        if not self.test_state(States.state1):
            succeed = False

        if succeed:
            if not self.test_state(States.state2):
                succeed = False

        if succeed:
            if not self.test_state(States.state3):
                succeed = False

        if succeed:
            if not self.test_error_state():
                succeed = False

        Thread(target=self.fsm.start_fsm, args=[States.state1]).start()
        if succeed:
            if not self.test_stop_fsm():
                succeed = False

        print('[TEST_FSM] End of the test, success: %s' % str(succeed))

    def test_state(self, state):

        sleep(0.1)
        if self.fsm.in_error:
            print('[TEST_FSM] Failed, fsm in error')
            self.fsm.stop_fsm()
            self.stop.set()
            print('[TEST_FSM] Waiting FSM to stop')

            while self.stop.is_set():
                sleep(0.1)

            print('[TEST_FSM] FSM stopped')
            return False

        self.in_state.wait()
        if self.fsm.running.state != state:
            print('[TEST_FSM] Test failed, fsm not in: %s' % state.value)
            self.fsm.stop_fsm()
            self.stop.set()
            print('[TEST_FSM] Waiting FSM to stop')

            while self.stop.is_set():
                sleep(0.1)

            print('[TEST_FSM] FSM stopped')
            return False

        print('[TEST_FSM] Test succeed, fsm in: %s' % state.value)
        self.in_state.clear()
        return True

    def test_error_state(self):

        succeed = True

        sleep(0.1)
        if self.fsm.in_error:
            print('[TEST_FSM] Succeed to be in error')
        else:
            print('[TEST_FSM] Failed to be in error')
            succeed = False

        self.fsm.stop_fsm()
        self.stop.set()
        print('[TEST_FSM] Waiting FSM to stop')

        while self.stop.is_set():
            sleep(0.1)
        if self.fsm.is_running():
            print('[TEST_FSM] Failed to stop fsm')
            succeed = False
        else:
            print('[TEST_FSM] Succeed to stop fsm')
        return succeed

    def test_stop_fsm(self):

        print('[TEST_FSM] Wating to be in state1')
        sleep(0.1)

        self.in_state.wait()
        self.fsm.stop_fsm()
        self.in_state.clear()

        print('[TEST_FSM] Waiting FSM to stop')
        sleep(0.5)

        if self.fsm.is_running():
            print('[TEST_FSM] Failed to stop fsm')
            return False
        print('[TEST_FSM] Succeed to stop fsm')
        return True

    def state1(self):
        print('[TEST_FSM] Hello, I am state 1')
        self.in_state.set()
        while self.in_state.is_set():
            sleep(0.1)
        return  States.state2

    def state2(self):
        print('[TEST_FSM] Hello, I am state 2')
        self.in_state.set()
        while self.in_state.is_set():
            sleep(0.1)
        return States.state3

    def state3(self):
        print('[TEST_FSM] Hello, I am state 3, I will failed')
        self.in_state.set()
        while self.in_state.is_set():
            sleep(0.1)
        return "I've failed"

    def error(self):
        print("I'm an error")
        self.stop.wait()
        print('Error is finished')
        self.stop.clear()

def main():
    Test_Fsm()

if __name__ == "__main__":
    main()
