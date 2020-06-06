import queue
from threading import Thread, Event
import concurrent.futures

test = 0

class Act_queue():
    def __init__(self):
        self.task = queue.Queue()
        self.response = queue.Queue()
        self.stop = Event()
    def launch_multiple_actions(self, actions, args):
        if len(args) != len(actions):
            return None
        launched = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for i in range(len(actions)):
                launched.append(executor.submit(actions[i], *args[i]))
        results = []
        for action in launched:
            results.append(action.result())
        return results
    def run_action(self, action, args):
        tmp = (action, args)
        self.task.put(tmp)
    def run_actions(self, actions, args_list):
        tmp = (list(actions), list(args_list))
        self.task.put(tmp)
    def _run_queue(self):
        tmp = ()
        while not self.stop.is_set() and not self.task.empty():
            tmp = self.task.get()
            if type(tmp[0]) == list:
                self.response.put(self.launch_multiple_actions(tmp[0], tmp[1]))
            else :
                self.response.put(tmp[0](*tmp[1]))
    def run_queue(self):
        t = Thread(target=self._run_queue)
        t.start()
        t.join()
    def stop_queue(self):
        self.stop.set()


def print_toto(a, b) :
    global test
    print("Function A: args [", a, "] and [", b, "]")
    test += 1
    return test


def print_tata(a, b) :
    global test
    print("Function B: args [", a, "] and [", b, "]")
    test += 1
    return test


toto = Act_queue()
toto.run_action(print_toto, (1, 2))
toto.run_actions([print_tata, print_toto], [(3, 4), (5, 6)])
toto.run_queue()
while (not toto.response.empty()) :
    print(toto.response.get())