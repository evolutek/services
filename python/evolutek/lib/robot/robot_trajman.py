from evolutek.lib.map.point import Point
from evolutek.lib.status import RobotStatus
from evolutek.lib.utils.wrappers import if_enabled, use_queue
from math import pi
from time import sleep

# TODO : Check abort
# TODO : Timeout

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
    self.trajman.set_x(float(x))

def set_y(self, y, mirror=True):
    if mirror:
        y = self.mirror_pos(y=float(y))['y']

    self.trajman.set_y(y)

def set_theta(self, theta, mirror=True):
    if mirror:
        theta = self.mirror_pos(theta=float(theta))['theta']

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
@use_queue
def goto(self, x, y, mirror=True):
    if mirror:
        y = self.mirror_pos(y=float(y))['y']

    status = self.goto_xy(x, y)
    with self.lock:
        self.moving_side = None
    return status

@if_enabled
@use_queue
def goth(self, theta, mirror=True):
    if mirror:
        theta = self.mirror_pos(theta=float(theta))['theta']

    return self.goto_theta(theta)

@if_enabled
@use_queue
def move_back(self):
    side = 0
    dist = 0
    with self.lock:
        side = int(not self.avoid_side)
        dist = self.dist

    print('[ROBOT] Move back direction: ' + 'front' if side else 'back')

    return self.move_trsl(acc=200, dec=200, dest=self.dist, maxspeed=400, sens=side)

@if_enabled
@use_queue
def goto_avoid(self, x, y, mirror=True):

    x = float(x)
    y = float(y)

    if mirror:
        _destination = self.mirror_pos(x, y)
        x = _destination['x']
        y = _destination['y']

    destination = Point(x, y)

    status = RobotStatus.NotReached
    while status != RobotStatus.Reached:

        print('[ROBOT] Moving')
        status = RobotStatus.get_status(self.goto(x, y, mirror=False, use_queue=False))

        if status == RobotStatus.HasAvoid:

            # TODO : check if a robot is in front of our robot before move back

            _status = RobotStatus.get_status(self.move_back(use_queue=False))

            if _status == RobotStatus.Aborted or _status == RobotStatus.Disabled:
                return RobotStatus.return_status(_status)

            dist = 0.0
            side = True
            with self.lock:
                dist = self.robot_position.dist(Point(x=x, y=y))
                side = self.avoid_side

            while self.need_to_avoid(dist, side):
                if self.check_abort() != RobotStatus.Ok:
                    return RobotStatus.return_status(RobotStatus.Aborted)

                print('[ROBOT] Waiting')
                sleep(0.1)

        elif status != RobotStatus.Reached:
            break

    return RobotStatus.return_status(status)

@if_enabled
@use_queue
def goto_with_path(self, x, y, mirror=True):

    x = float(x)
    y = float(y)

    if mirror:
        _destination = self.mirror_pos(x, y)
        x = _destination['x']
        y = _destination['y']

    destination = Point(x, y)

    print('[ROBOT] Goto with path : %s' % destination)

    status = RobotStatus.NotReached

    while status != RobotStatus.Reached:

        origin = None
        with self.lock:
            origin = self.robot_position

        path = self.get_path(origin, destination)

        if (len(path) < 2):
            return RobotStatus.return_status(RobotStatus.Unreachable)

        for i in range(1, len(path)):

            print('[ROBOT] Going from %s to %s' % (str(path[i - 1]), path[i]))

            status = RobotStatus.get_status( self.goto(path[i].x, path[i].y, mirror=mirror, use_queue=False))

            if status == RobotStatus.HasAvoid:

                sleep(3)

                _status = RobotStatus.get_status(self.move_back(use_queue=False))

                if _status == RobotStatus.Aborted or _status == RobotStatus.Disabled:
                    return RobotStatus.return_status(_status)

                break

            elif status != RobotStatus.Reached:
                return RobotStatus.return_status(status)

    return RobotStatus.return_status(status)


#################
# RECALIBRATION #
#################

@if_enabled
@use_queue
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

    if isinstance(init, str):
        init = init == 'true'

    if isinstance(mirror, str):
        mirror = mirror == 'true'

    # Init pos if necessary
    if init:
        self.trajman.set_theta(0)
        self.trajman.set_x(1000)
        self.trajman.set_y(1000)

    # TODO : check trajman returns ?

    if isinstance(x, str):
        x = x == 'true'

    if isinstance(y, str):
        y = y == 'true'

    if x:
        print('[ROBOT] Recalibration X')
        theta = pi if side_x[0] ^ side_x[1] else 0
        self.goth(theta, mirror=mirror, use_queue=False)
        self.recal(sens=int(side_x[0]), decal=float(decal_x))
        sleep(0.75)
        self.move_trsl(dest=2*(self.dist - self.size_x), acc=200, dec=200, maxspeed=200, sens=not side_x[0])

    if y:
        print('[ROBOT] Recalibration Y')
        theta = -pi/2 if side_y[0] ^ side_y[1] else pi/2
        self.goth(theta, mirror = mirror, use_queue=False)
        self.recal(sens=int(side_y[0]), decal=float(decal_y))
        sleep(0.75)
        self.move_trsl(dest=2*(self.dist - self.size_x), acc=200, dec=200, maxspeed=200, sens=not side_y[0])

    self.trajman.set_trsl_max_speed(speeds['trmax'])
    self.trajman.set_trsl_acc(speeds['tracc'])
    self.trajman.set_trsl_dec(speeds['trdec'])

    return RobotStatus.return_status(RobotStatus.Done)


# Recalibration with sensors
# Set axis_x to True to recal on x axis
# Set left to True to use the left sensor
@if_enabled
@use_queue
def recalibration_sensors(self, axis_x, left):

    print('[ROBOT] Recalibration with sensors')
    print(f'[ROBOT] axis_x={axis_x} left={left}')

    id = 1 if left else 2
    dist = self.actuators.read_sensor_read(id)
    print(f'[ROBOT] Measured distance: {dist}mm')

    # Distance between the sensor and the center of the robot
    dist_to_center = 200

    setter = self.trajman.set_x if axis_x else self.trajman.set_y
    setter(dist + dist_to_center)

    return RobotStatus.return_status(RobotStatus.Done)
