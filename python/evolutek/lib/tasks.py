from math import pi

class Task:

    def __init__(self, x, y, mirror=False, theta=None, speed=None, action=None, \
        action_param=None, not_avoid=False, score=0):
        self.x = x
        self.y = y if not mirror else 3000 - y
        self.theta = theta
        if not theta is None and mirror:
            self.theta = 0 - theta
        self.action = action
        self.action_param = action_param
        self.speed = speed
        self.not_avoid = not_avoid
        self.score = score

    def action_make(self):
        if self.action is not None:
            self.action(**self.action_param)

    def __str__(self):
        s = "--- Task ---\n"
        s += "--> x: %d, y:%d\n" % (self.x, self.y)
        if not self.theta is None:
            s += "--> theta: %f\n" & (self.theta)
        if not self.action is None:
            s += "--> action: %s" % (str(self.action))
            if not self.action_param is None:
                s += ", %s\n" % (str(self.action_param))
            else:
                s += "\n"
        if not self.speed is None:
            s += "--> speed: %d\n" % (self.speed)
        s += "--> not avoid: %s\n" % ('True' if self.not_avoid else 'False')
        s += "--> score: %d\n" % (self.score)
        return s

class Tasks:

    def __init__(self, start_x, start_y, start_theta, cs, mirror = False):

        self.mirror = mirror

        self.cs = cs

        self.start_x = start_x
        self.start_y = start_y if not mirror else 3000 - start_y
        self.start_theta = start_theta if not mirror else 0 - start_theta

        self.tasks = []
        self.reset()

    def reset(self, mirror=False):

        if self.mirror != mirror:
            self.mirror = mirror
            self.start_y = 3000 - self.start_y
            self.start_theta = 0 - self.start_theta

        self.tasks = get_tasks(self.cs, self.mirror)

    def __str__(self):
        s = "--- Start ---\n"
        s += "--> start_x: %d\n" % self.start_x
        s += "--> start_y: %d\n" % self.start_y
        s += "--> start_theta: %f\n" % self.start_theta
        for task in self.tasks:
            s += str(task)
        return s

""" TASKS """
def get_tasks(cs, mirror=False):
    tasks = []
    tasks.append(
        Task(1000, 1500, mirror=mirror)
    )
    return tasks

if __name__ == "__main__":
    t = Tasks(800, 50, pi/2, False)
    print(t)
