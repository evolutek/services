import queue
from threading import Thread, Event
from time import sleep

from evolutek.lib.utils.lma import launch_multiple_actions
from evolutek.lib.utils.task import Task

class ActQueue:
    def __init__(self, start_callback=None, end_callback=None):
        self.tasks = queue.Queue()
        self.response_queue = queue.Queue()
        self.stop = Event()
        self.start_callback = start_callback
        self.end_callback = end_callback
        self.is_running = Event()

    ##############
    # ADD A TASK #
    ##############
    def run_action(self, task):
        self.tasks.put(task)

    ######################
    # ADD A LIST OF TASK #
    ######################
    def run_actions(self, tasks):
        self.tasks.put(tasks)

    #################
    # DEPILATE QUEUE #
    #################
    def _run_queue(self):
        tmp = ()
        self.is_running.set()
        while not self.stop.is_set():
            try:
                task = self.tasks.get(timeout=0.01)
            except:
                continue

            print('[ACT_QUEUE] Running task')

            if self.start_callback is not None:
                self.start_callback()

            if isinstance(task, Task):
                result = task.run()
            else:
                result = launch_multiple_actions(task)

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
        while not self.tasks.empty():
            self.tasks.get()
        print('[ACT_QUEUE] Cleared')

    ##############
    # STOP QUEUE #
    ##############
    def stop_queue(self):
        self.stop.set()
        self.clear_queue()

        while self.is_running.is_set():
            sleep(0.1)

        print('[ACT_QUEUE] Stopped')
