from functools import wraps

from evolutek.lib.utils.boolean import get_boolean

MAX_TASK_ID = 42
CURRENT_TASK_ID = 0

class Task:

    def __init__(self, action, args=None, kwargs=None, id=-1):
        self.action = action

        if args is None:
            args = []
        self.args = args

        if kwargs is None:
            kwargs = {}
        self.kwargs = kwargs

        self.id = id

    def run(self):
        return self.action(*self.args, **self.kwargs)

    def __str__(self):
        s = '----------\n'
        s += 'Task nb %d\n' % self.id
        s += 'action: %s\n' % str(self.action.__name__)
        s += 'args: %s\n' % str(self.args)
        s += 'kwargs: %s\n' % str(self.kwargs)
        s += '----------'
        return s

# Decorator factory: routes the produced Task into self.current_tasks[category]
# so trajman moves ('move') and actuator actions ('actuator') run on separate
# slots and can execute concurrently.
def async_task(category):

    def decorator(method):

        @wraps(method)
        def wrapped(self, *args, **kwargs):

            run_async = True
            if 'async_task' in kwargs:
                run_async = get_boolean(kwargs['async_task'])

                del kwargs['async_task']

            args = [self] + list(args)
            global CURRENT_TASK_ID
            task = Task(method, args, kwargs, id=CURRENT_TASK_ID)
            CURRENT_TASK_ID = (CURRENT_TASK_ID + 1) % (MAX_TASK_ID + 1)

            if run_async:
                with self.lock:
                    if self.current_tasks[category] is None:
                        self.current_tasks[category] = task
                    else:
                        print('[TASK][%s] Already a current task running/to run' % category)
            else:
                return task.run()

        return wrapped

    return decorator
