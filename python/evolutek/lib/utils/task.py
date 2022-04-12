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

def async_task(method):

    @wraps(method)
    def wrapped(self, *args, **kwargs):

        async_task = True
        if 'async_task' in kwargs:
            async_task = get_boolean(kwargs['async_task'])

            del kwargs['async_task']

        args = [self] + list(args)
        global CURRENT_TASK_ID
        task = Task(method, args, kwargs, id=CURRENT_TASK_ID)
        CURRENT_TASK_ID = (CURRENT_TASK_ID + 1) % (MAX_TASK_ID + 1)

        if async_task:
            with self.lock:
                if self.current_task is None:
                    self.current_task = task
                else:
                    print('[TASK] Already a current task running/to run')
        else:
            return task.run()

    return wrapped
