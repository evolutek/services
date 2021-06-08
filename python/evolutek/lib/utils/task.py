class Task:

    def __init__(self, action, args=None, kwargs=None):
        self.action = action

        if args is None:
            args = []
        self.args = args

        if kwargs is None:
            kwargs = {}
        self.kwargs = kwargs
    
    def run(self):
        return self.action(*self.args, **self.kwargs)
