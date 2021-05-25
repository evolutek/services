from evolutek.lib.utils.wrappers import event_waiter

##########
# COMMON #
##########

def mirror_pos(self, x=None, y=None, theta=None):
    side = None
    with self.lock:
        side = self.side

    if y is not None:
        y = (y if not side else 3000 - y)

    if theta is not None:
        theta = (theta if not side else -1 * theta)

    return {
        'x' : x,
        'y' : y,
        'theta' : theta
    }

########
# SETS #
########

def set_x(self, x):
    self.trajman.set_x(x)

def set_y(self, y, mirror=True):
    if mirror:
        y = self.mirror_pos(y=y)['y']

    self.trajman.set_y(y)

def set_theta(self, theta, mirror=True):
    if self.mirror:
        theta = self.mirror_pos(theta=theta)['theta']

    self.trajman.set_theta(theta)

def set_pos(self, x, y, theta=None, mirror=True):
    self.set_x(x)
    self.set_y(y, mirror)
    if theta is not None:
        self.set_theta(theta, mirror)

########
# GOTO #
########

def goto(self, x, y, mirror=True):

    if mirror:
        y = self.mirror_pos(y=y)['y']

    return self.goto_xy(x, y)

def goth(self, theta, mirror=True):

    if mirror:
        theta = self.mirror_pos(theta=theta)['theta']

    return self.goto_theta(theta)


