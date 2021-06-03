from evolutek.lib.status import RobotStatus
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
            return RobotStatus.Disabled
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
def event_waiter(method, start_event, stop_event, callback=None, callback_refresh=0.1):

    @wraps(method)
    def wrapped(*args, **kwargs):

        nonlocal start_event
        nonlocal stop_event
        start_event.clear()
        stop_event.clear()

        nonlocal callback
        nonlocal callback_refresh

        watchdog = Watchdog(1, timeout_handler)

        global timeout_event
        timeout_event.clear()
        method(*args, **kwargs)

        watchdog.reset()

        while not start_event.is_set() and not timeout_event.is_set():
            sleep(0.01)

        if not start_event.is_set():
            return {'status' : RobotStatus.NotStarted}

        watchdog.stop()

        while not stop_event.is_set():
            if callback is not None and callback():
                break
            sleep(callback_refresh)

        stop_event.wait()
        stop_event.data['status'] = RobotStatus.get_status(stop_event.data)
        return stop_event.data

    return wrapped
