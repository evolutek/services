import queue
from threading import Thread, Event
import concurrent.futures

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