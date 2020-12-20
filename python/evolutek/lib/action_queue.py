import queue
from threading import Thread, Event
import concurrent.futures

# Action queue class
class Act_queue():
    def __init__(self):

        # Queue holding waiting task
        self.task = queue.Queue()

        # Queue holding the tasks returns
        self.response_queue = queue.LifoQueue()

        # Event to tell queue to stop
        self.stop = Event()

    # Get return from the queue
    def get_response(self):
        return self.response_queue.get()

    # Launch mutiple actions and add all actions returns
    # actions: actions to launch
    # args: list of args of the actions
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

    # Add an action to the queue and wait for return
    # action: action to run
    # args: args of the action
    def run_action(self, action, args):
        tmp = (action, args)
        self.task.put(tmp)
        return (self.get_response())

    # Add a list of actions to the queue and wait for returns
    # actions: actions to run
    # arg_list: arg_list of the actions
    def run_actions(self, actions, args_list):
        tmp = (list(actions), list(args_list))
        self.task.put(tmp)
        return (self.get_response())

    # Loop running actions stored in the queue
    def _run_queue(self):
        tmp = ()
        while not self.stop.is_set():
            tmp = self.task.get()
            if type(tmp[0]) == list:
                self.response_queue.put(self.launch_multiple_actions(tmp[0], tmp[1]))
            else :
                self.response_queue.put(tmp[0](tmp[1][0], *tmp[1][1], **tmp[1][2]))

    # Launch a thread to run the queue
    def run_queue(self):
        self.stop.clear()
        t = Thread(target=self._run_queue)
        t.start()


    # Empty the queue and stop run
    def stop_queue(self):
        while self.task.empty() == False:
            self.task.get()
        self.stop.set()
