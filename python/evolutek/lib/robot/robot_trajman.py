from evolutek.lib.status import RobotStatus
from evolutek.lib.utils.wrappers import if_enabled
from time import sleep

##########
# COMMON #
##########

def mirror_pos(self, x=None, y=None, theta=None):
    side = None
    with self.lock:
        side = self.side

    if y is not None:
        y = (y if side else 3000 - y)

    if theta is not None:
        theta = (theta if side else -1 * theta)

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

#########
# MOVES #
#########

@if_enabled
def goto(self, x, y, mirror=True):
    if mirror:
        y = self.mirror_pos(y=y)['y']

    return self.goto_xy(x, y)

@if_enabled
def goth(self, theta, mirror=True):
    if mirror:
        theta = self.mirror_pos(theta=theta)['theta']

    return self.goto_theta(theta)

@if_enabled
def move_back(self):
    #print('[ROBOT] Move back direction: ' + 'back' if self.avoid_side else 'front')
    return self.move_trsl(acc=200, dec=200, dest=dist, maxspeed=400, sens=int(not self.avoid_side))

#################
# RECALIBRATION #
#################

@if_enabled
def recalibration(self,
                    x=True,
                    y=True,
                    decal_x=0,
                    decal_y=0,
                    init=False,
                    mirror=True):

    # TODO: Update
    side_x = (False, False)
    side_y = (False, False)

    speeds = self.trajman.get_speeds()
    self.trajman.free()

    self.trajman.set_trsl_max_speed(100)
    self.trajman.set_trsl_acc(300)
    self.trajman.set_trsl_dec(300)

    # Init pos if necessary
    if init:
        self.trajman.set_theta(0)
        self.trajman.set_x(1000)
        self.trajman.set_y(1000)

    # TODO : check trajman returns ?

    if x:
        print('[ROBOT] Recalibration X')
        theta = pi if side_x[0] ^ side_x[1] else 0
        self.goth(theta)
        self.recal(sens=int(side_x[0]), decal=float(decal_x))
        self.move_trsl(dest=2*(self.recal_dist - self.size_x), acc=200, dec=200, maxspeed=200, sens=not side_x[0])

    if y:
        print('[ROBOT] Recalibration Y')
        theta = -pi/2 if side_y[0] ^ side_y[1] else pi/2
        self.goth(theta)
        self.recal(sens=int(side_y[0]), decal=float(decal_y))
        self.move_trsl(dest=2*(self.dist - self.size_x), acc=200, dec=200, maxspeed=200, sens=not side_y[0])

    self.trajman.set_trsl_max_speed(speeds['trmax'])
    self.trajman.set_trsl_acc(speeds['tracc'])
    self.trajman.set_trsl_dec(speeds['trdec'])

    return RobotStatus.Done
