import queue
from threading import Thread, Event
import concurrent.futures

class Act_queue():
    def __init__(self):
        self.task = queue.Queue()
        self.response_queue = queue.LifoQueue()
        self.stop = Event()

    #############################
    # EXECUTE A LIST OF ACTIONS #
    #############################
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

    ##############
    # ADD A TASK #
    ##############
    def run_action(self, action, args):
        tmp = (action, args)
        self.task.put(tmp)

    ######################
    # ADD A LIST OF TASK #
    ######################
    def run_actions(self, actions, args_list):
        tmp = (list(actions), list(args_list))
        self.task.put(tmp)

    #################
    # DEPILATE QUEUE #
    #################
    def _run_queue(self):
        tmp = ()
        while not self.stop.is_set():
            tmp = self.task.get()
            if type(tmp[0]) == list:
                self.response_queue.put(self.launch_multiple_actions(tmp[0], tmp[1]))
            else :
                self.response_queue.put(tmp[0](*tmp[1]))

    ###############
    # START QUEUE #
    ###############
    def run_queue(self):
        self.stop.clear()
        t = Thread(target=self._run_queue)
        t.start()


    ##############
    # STOP QUEUE #
    ##############
    def stop_queue(self):
        while self.task.empty() == False:
            self.task.get()
        self.stop.set()

