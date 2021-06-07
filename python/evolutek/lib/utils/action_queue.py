import queue
from threading import Thread, Event
from evolutek.lib.utils.lma import launch_multiple_actions


class ActQueue:
    def __init__(self, start_callback=None, end_callback=None):
        self.task = queue.Queue()
        self.response_queue = queue.Queue()
        self.stop = Event()
        self.start_callback = start_callback
        self.end_callback = end_callback
        self.is_running = Event()

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
        self.is_running.set()
        while not self.stop.is_set():
            tmp = self.task.get()

            if self.start_callback is not None:
                self.start_callback()

            if isinstance(tmp[0], list):
                result = launch_multiple_actions(tmp[0], tmp[1])
            else:
                result = tmp[0](*tmp[1])

            if self.end_callback is not None:
                self.end_callback(result)
        self.is_running.clear()

    ###############
    # START QUEUE #
    ###############
    def run_queue(self):
        self.stop.clear()
        if not self.is_running.is_set():
            Thread(target=self._run_queue).start()
            print('[ACT_QUEUE] Running queue')
        else:
            print('[ACT_QUEUE] Is already running')

    ###############
    # CLEAR QUEUE #
    ###############
    def clear_queue(self):
        while not self.task.empty():
            self.task.get()
        print('[ACT_QUEUE] Cleared')

    ##############
    # STOP QUEUE #
    ##############
    def stop_queue(self):
        self.stop.set()
        self.clear_queue()
        print('[ACT_QUEUE] Stopped')
