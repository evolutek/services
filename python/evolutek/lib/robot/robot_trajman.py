from evolutek.lib.map.point import Point
from evolutek.lib.status import RobotStatus
from evolutek.lib.utils.boolean import get_boolean
from evolutek.lib.utils.watchdog import Watchdog
from evolutek.lib.utils.wrappers import if_enabled, use_queue

from enum import Enum
from math import pi
from threading import Event
from time import sleep


class RecalSensor(Enum):
    No = "no"
    Left = "left"
    Right = "right"

class RecalSensor(Enum):
    No = "no"
    Left = "left"
    Right = "right"

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

    mirror = get_boolean(mirror)


    if mirror:
        y = self.mirror_pos(y=float(y))['y']

    self.trajman.set_y(y)

def set_theta(self, theta, mirror=True):
    mirror = get_boolean(mirror)


    if mirror:
        theta = self.mirror_pos(theta=float(theta))['theta']

    self.trajman.set_theta(theta)

def set_pos(self, x, y, theta=None, mirror=True):
    mirror = get_boolean(mirror)

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
    mirror = get_boolean(mirror)

    if mirror:
        y = self.mirror_pos(y=float(y))['y']

    position = self.trajman.get_position()
    distsqr = (x - position['x'])**2 + (y - position['y'])**2
    maxdist = 5
    if distsqr < maxdist**2:
        return RobotStatus.return_status(RobotStatus.Reached)

    return self.goto_xy(x, y)

@if_enabled
@use_queue
def goth(self, theta, mirror=True):
    mirror = get_boolean(mirror)

    if mirror:
        theta = self.mirror_pos(theta=float(theta))['theta']

    current = self.trajman.get_position()['theta']
    if abs(current - theta) < 0.075:
            return RobotStatus.return_status(RobotStatus.Reached)

    return self.goto_theta(theta)

@if_enabled
@use_queue
def move_back(self, side):

    side = get_boolean(side)

    dist = 0
    with self.lock:
        dist = self.dist

    print('[ROBOT] Move back direction: ' + 'front' if side else 'back')

    return self.move_trsl(acc=200, dec=200, dest=self.dist, maxspeed=400, sens=int(side))

timeout_event = Event()

def timeout_handler():
    global timeout_event
    timeout_event.set()

@if_enabled
@use_queue
def goto_avoid(self, x, y, mirror=True, timeout=None):

    x = float(x)
    y = float(y)

    mirror = get_boolean(mirror)

    if mirror:
        _destination = self.mirror_pos(x, y)
        x = _destination['x']
        y = _destination['y']

    destination = Point(x, y)
    status = RobotStatus.NotReached

    while status != RobotStatus.Reached:

        print('[ROBOT] Moving')
        data = self.goto(x, y, mirror=False, use_queue=False)
        status = RobotStatus.get_status(data)

        if status == RobotStatus.HasAvoid:

            side = get_boolean(data['avoid_side'])

            # TODO : check if a robot is in front of our robot before move back
            # _status = RobotStatus.get_status(self.move_back(side=(not side), use_queue=False))

            #if _status == RobotStatus.Aborted or _status == RobotStatus.Disabled:
            #    return RobotStatus.return_status(_status)

            pos = Point(dict=self.trajman.get_position())
            dist = pos.dist(destination)

            global timeout_event
            timeout_event.clear()

            if timeout is not None:
                watchdog = Watchdog(float(timeout), timeout_handler)
                watchdog.reset()

            while get_boolean(self.trajman.need_to_avoid(dist, side)):
                if self.check_abort() != RobotStatus.Ok:
                    return RobotStatus.return_status(RobotStatus.Aborted)

                if timeout_event.is_set():
                    return RobotStatus.return_status(RobotStatus.Timeout)

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

    mirror = get_boolean(mirror)

    if mirror:
        _destination = self.mirror_pos(x, y)
        x = _destination['x']
        y = _destination['y']

    destination = Point(x, y)

    print('[ROBOT] Goto with path : %s' % destination)

    status = RobotStatus.NotReached

    while status != RobotStatus.Reached:


        path = self.get_path(destination)

        if (len(path) < 2):
            return RobotStatus.return_status(RobotStatus.Unreachable)

        for i in range(1, len(path)):

            print('[ROBOT] Going from %s to %s' % (str(path[i - 1]), path[i]))

            data = self.goto(path[i].x, path[i].y, mirror=mirror, use_queue=False)
            status = RobotStatus.get_status(data)
            side = get_boolean(data['avoid_side'])

            if status == RobotStatus.HasAvoid:

                sleep(3)

                _status = RobotStatus.get_status(self.move_back(side=(not side), use_queue=False))

                if _status == RobotStatus.Aborted or _status == RobotStatus.Disabled:
                    return RobotStatus.return_status(_status)

                break

            elif status != RobotStatus.Reached:
                return RobotStatus.return_status(status)

    return RobotStatus.return_status(status)


#################
# RECALIBRATION #
#################

# Recalibration with sensors
# Set axis_x to True to recal on x axis
# Set left to True to use the left sensor
def recalibration_sensors(self, axis_x, side, sensor, mirror=True, init=False):

    axis_x = get_boolean(axis_x)
    side = get_boolean(side)
    mirror = get_boolean(mirror)

    if isinstance(sensor, str):
        sensor = RecalSensor(sensor)

    print('[ROBOT] Recalibration with sensors')
    print(f'[ROBOT] axis_x={axis_x} sensor={sensor.value}')

    # Distance between the sensor and the center of the robot
    dist_to_center = 109

    id = 1 if (sensor == RecalSensor.Left) ^ (not self.side and mirror) else 2
    dist = self.actuators.recal_sensor_read(id) + dist_to_center
    print(f'[ROBOT] Measured distance: {dist}mm')

    if not axis_x and (side ^ (sensor == RecalSensor.Left)):
        value = 3000 - dist
    if axis_x and ((not side) ^ (sensor == RecalSensor.Left)):
        value = 2000 - dist

    if not init:
        position = self.trajman.get_position()
        axis = 'x' if axis_x else 'y'
        if abs(position[axis] - value) > 50:
            print(f'[ROBOT] WARNING: Recalibration failed, measured position is too far away from current position')
            print(f'Axis: {axis}. Current position: {position[axis]}. Measured position: {value}')

    setter = self.trajman.set_x if axis_x else self.trajman.set_y
    setter(value)


@if_enabled
@use_queue
def recalibration(self,
                    x=True,
                    y=True,
                    x_sensor=RecalSensor.No,
                    y_sensor=RecalSensor.No,
                    decal_x=0,
                    decal_y=0,
                    side_x=False,
                    side_y=False,
                    init=False,
                    mirror=True):

    speeds = self.trajman.get_speeds()
    self.trajman.free()

    self.trajman.set_trsl_max_speed(100)
    self.trajman.set_trsl_acc(300)
    self.trajman.set_trsl_dec(300)

    x = get_boolean(x)
    y = get_boolean(y)
    side_x = get_boolean(side_x)
    side_y = get_boolean(side_y)
    init = get_boolean(init)
    mirror = get_boolean(mirror)

    if isinstance(x_sensor, str):
        x_sensor = RecalSensor(x_sensor)
    if isinstance(y_sensor, str):
        y_sensor = RecalSensor(y_sensor)

    # Init pos if necessary
    if init:
        self.trajman.set_theta(0)
        self.trajman.set_x(1000)
        self.trajman.set_y(1000)

    if x:
        print('[ROBOT] Recalibration X')
        theta = pi if side_x else 0

        status = RobotStatus.get_status(self.goth(theta, mirror=mirror, use_queue=False))
        if status != RobotStatus.Reached:
            return RobotStatus.return_status(status)

        status = RobotStatus.get_status(self.recal(sens=0, decal=float(decal_x)))
        if status not in [RobotStatus.NotReached, RobotStatus.Reached]:
            return RobotStatus.return_status(status)

        sleep(0.75)
        if y_sensor != RecalSensor.No:
            self.recalibration_sensors(axis_x=False, side=side_x, sensor=y_sensor, mirror=mirror, init=init)

        status = RobotStatus.get_status(self.move_trsl(dest=2*(self.dist - self.size_x), acc=200, dec=200, maxspeed=200, sens=1))
        if status != RobotStatus.Reached:
            return RobotStatus.return_status(status)

    if y:
        print('[ROBOT] Recalibration Y')
        theta = -pi/2 if side_y else pi/2

        status = RobotStatus.get_status(self.goth(theta, mirror = mirror, use_queue=False))
        if status != RobotStatus.Reached:
            return RobotStatus.return_status(status)

        status = RobotStatus.get_status(self.recal(sens=0, decal=float(decal_x)))
        if status not in [RobotStatus.NotReached, RobotStatus.Reached]:
            return RobotStatus.return_status(status)

        sleep(0.75)
        if x_sensor != RecalSensor.No:
            self.recalibration_sensors(axis_x=True, side=side_y, sensor=x_sensor, mirror=mirror, init=init)

        status = RobotStatus.get_status(self.move_trsl(dest=2*(self.dist - self.size_x), acc=200, dec=200, maxspeed=200, sens=1))
        if status != RobotStatus.Reached:
            return RobotStatus.return_status(status)

    self.trajman.set_trsl_max_speed(speeds['trmax'])
    self.trajman.set_trsl_acc(speeds['tracc'])
    self.trajman.set_trsl_dec(speeds['trdec'])

    print('[ROBOT] New position: ' + str(self.trajman.get_position()))

    return RobotStatus.return_status(RobotStatus.Done)
