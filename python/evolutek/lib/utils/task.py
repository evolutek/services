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
