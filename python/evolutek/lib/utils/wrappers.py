from evolutek.lib.status import RobotStatus
from evolutek.lib.utils.boolean import get_boolean
from evolutek.lib.utils.task import Task
from evolutek.lib.utils.watchdog import Watchdog
from functools import wraps
from threading import Event
from time import sleep

# Decorator wrapper to disable a method if the disabled flag is set
# method: method to decorate
def if_enabled(method):
    """
    A method can be disabled so that it cannot be used in any circumstances.
    """
    @wraps(method)
    def wrapped(self, *args, **kwargs):
        if self.disabled.is_set():
            self.log(what='disabled',
                    msg="Usage of {} is disabled".format(method))
            return RobotStatus.return_status(RobotStatus.Disabled)
        return method(self, *args, **kwargs)

    return wrapped


timeout_event = Event()

def timeout_handler():
    global timeout_event
    timeout_event.set()

# Decorator wrapper to call a wait for a start and stop event after calling a method
# method: method to decorate
# start_event: start event to wait
# stop_event: stop event to wait
# callback: callback to call at each iteration while waiting for stop event
# callback_refresh : refresh to call callback
def event_waiter(method, start_event, stop_event, timeout_not_started=1, callback=None, callback_refresh=0.01):

    @wraps(method)
    def wrapped(*args, **kwargs):

        nonlocal start_event
        nonlocal stop_event
        start_event.clear()
        stop_event.clear()

        nonlocal callback
        nonlocal callback_refresh

        nonlocal timeout_not_started
        watchdog = Watchdog(timeout_not_started, timeout_handler)

        global timeout_event
        timeout_event.clear()
        r = method(*args, **kwargs)

        if RobotStatus.get_status(r) == RobotStatus.Disabled:
            return RobotStatus.return_status(RobotStatus.Disabled)

        id = None
        if r != None:
            id = int(r)

        watchdog.reset()

        while True:
            if start_event.is_set():
                if id is not None and ('id' not in start_event.data or id != int(start_event.data['id'])):
                    start_event.clear()
                else:
                    watchdog.stop()
                    break

            if timeout_event.is_set():
                return RobotStatus.return_status(RobotStatus.NotStarted)

            sleep(0.01)

        status = None
        while True:
            if stop_event.is_set():
                if id is not None and ('id' not in stop_event.data or id != int(stop_event.data['id'])):
                    stop_event.clear()
                else:
                    break

            if callback is not None:
                status =  callback()
                if status != RobotStatus.Ok:
                    break

            sleep(callback_refresh)

        stop_event.wait()

        if status is None or status == RobotStatus.Ok:
            status = RobotStatus.get_status(stop_event.data)

        del stop_event.data['status']

        return RobotStatus.return_status(status, **stop_event.data)

    return wrapped

def use_queue(method):

    @wraps(method)
    def wrapped(self, *args, **kwargs):

        use_queue = True
        if 'use_queue' in kwargs:
            use_queue = get_boolean(kwargs['use_queue'])

            del kwargs['use_queue']

        args = [self] + list(args)
        task = Task(method, args, kwargs)

        if use_queue:
            return self.queue.run_action(task)
        else:
            return task.run()

    return wrapped
