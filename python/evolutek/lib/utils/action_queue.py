import queue
from threading import Thread, Event
from .lma import launch_multiple_actions


class ActQueue:
    def __init__(self, start_callback, end_callback):
        self.task = queue.Queue()
        self.response_queue = queue.Queue()
        self.stop = Event()
        self.start_callback = start_callback
        self.end_callback = end_callback

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
            self.start_callback()
            if isinstance(tmp[0], list):
                result = launch_multiple_actions(tmp[0], tmp[1])
            else:
                result = tmp[0](*tmp[1])
            self.end_callback(result)

    ###############
    # START QUEUE #
    ###############
    def run_queue(self):
        self.stop.clear()
        Thread(target=self._run_queue).start()

    ##############
    # STOP QUEUE #
    ##############
    def stop_queue(self):
        self.stop.set()
        while not self.task.empty():
            self.task.get()

