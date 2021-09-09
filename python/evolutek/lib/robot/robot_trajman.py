from evolutek.lib.map.point import Point
from evolutek.lib.status import RobotStatus
from evolutek.lib.utils.boolean import get_boolean
from evolutek.lib.utils.watchdog import Watchdog
from evolutek.lib.utils.wrappers import if_enabled, use_queue

from enum import Enum
from math import pi, cos, sin
from threading import Event
from time import sleep

DELTA_POS = 5
DELTA_ANGLE = 0.075
HOMEMADE_RECAL = True

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
def goto(self, x, y, avoid=True, mirror=True):
    mirror = get_boolean(mirror)
    x = float(x)
    y = float(y)

    if mirror:
        y = self.mirror_pos(y=y)['y']

    position = Point(dict=self.trajman.get_position())
    if position.dist(Point(x=x, y=y)) < DELTA_POS:
        print('[ROBOT] Already reached position')
        return RobotStatus.return_status(RobotStatus.Reached)

    return self.goto_xy(x=x, y=y, avoid=avoid)


@if_enabled
@use_queue
def goth(self, theta, mirror=True):
    mirror = get_boolean(mirror)
    theta = float(theta)

    if mirror:
        theta = self.mirror_pos(theta=theta)['theta']

    current = float(self.trajman.get_position()['theta'])
    if abs(current - theta) < DELTA_ANGLE:
        print('[ROBOT] Already reached angle')
        return RobotStatus.return_status(RobotStatus.Reached)

    return self.goto_theta(theta)

@if_enabled
@use_queue
def move_back(self, side):

    side = get_boolean(side)

    dist = 0
    with self.lock:
        dist = self.dist

    _pos = self.trajman.get_position()
    position = Point(dict=_pos)
    angle = float(_pos['theta']) + (0 if side else pi)

    x = position.x + dist * cos(angle)
    y = position.y + dist * sin(angle)

    x_dist = min(x, 2000 - x)
    y_dist = min(y, 3000 - y)

    if x_dist < dist or y_dist < dist:
        print("[ROBOT] Can't move back, too close of the wall")
        # TODO : compute new dist
        return RobotStatus.return_status(RobotStatus.NotReached)

    print('[ROBOT] Move back direction: ' + 'front' if side else 'back')

    return self.move_trsl(acc=200, dec=200, dest=self.dist, maxspeed=400, sens=int(side))

timeout_event = Event()

def timeout_handler():
    global timeout_event
    timeout_event.set()

@if_enabled
@use_queue
def goto_avoid(self, x, y, avoid=True, timeout=None, skip=False, mirror=True):

    x = float(x)
    y = float(y)

    mirror = get_boolean(mirror)
    skip = get_boolean(skip)

    if mirror:
        _destination = self.mirror_pos(x, y)
        x = _destination['x']
        y = _destination['y']

    destination = Point(x, y)
    status = RobotStatus.NotReached

    while status != RobotStatus.Reached:

        print('[ROBOT] Moving')

        data = self.goto(x, y, avoid=avoid, mirror=False, use_queue=False)
        status = RobotStatus.get_status(data)

        if status == RobotStatus.HasAvoid:

            if skip:
                return RobotStatus.return_status(RobotStatus.NotReached)

            side = get_boolean(data['avoid_side'])

            # TODO : check if a robot is in front of our robot before move back
            # _status = RobotStatus.get_status(self.move_back(side=(not side), use_queue=False))

            #if _status == RobotStatus.Aborted or _status == RobotStatus.Disabled:
            #    return RobotStatus.return_status(_status)

            pos = Point(dict=self.trajman.get_position())
            dist = pos.dist(destination)

            global timeout_event
            timeout_event.clear()

            watchdog = None
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

            if watchdog is not None:
                watchdog.stop()

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
    has_moved = False

    print('[ROBOT] Goto with path : %s' % destination)

    status = RobotStatus.NotReached

    while status != RobotStatus.Reached:

        path = self.get_path(destination)

        if (len(path) < 2):
            return RobotStatus.return_status(RobotStatus.Unreachable, has_moved=has_moved)

        for i in range(1, len(path)):

            has_moved = True
            print('[ROBOT] Going from %s to %s' % (str(path[i - 1]), path[i]))

            data = self.goto(path[i].x, path[i].y, mirror=False, use_queue=False)
            status = RobotStatus.get_status(data)
            side = get_boolean(data['avoid_side'])

            if status == RobotStatus.HasAvoid:

                _status = RobotStatus.get_status(self.move_back(side=(not side), use_queue=False))
                sleep(0.5)

                if _status == RobotStatus.Aborted or _status == RobotStatus.Disabled:
                    self.clean_map()
                    return RobotStatus.return_status(_status)

                break

            elif status != RobotStatus.Reached:
                self.clean_map()
                return RobotStatus.return_status(status)

    self.clean_map()
    return RobotStatus.return_status(status)


#################
# RECALIBRATION #
#################

@if_enabled
@use_queue
def homemade_recal(self, decal=0):

    decal = float(decal)

    print("[ROBOT] Using homemade recal")

    position = self.trajman.get_position()
    theta = position['theta']

    self.trajman.move_trsl(dest=200, acc=300, dec=300, maxspeed=200, sens=0)
    sleep(0.75)

    if theta < pi/4 and theta > -pi/4:
        self.trajman.set_theta(0)
        self.trajman.set_x(120 + decal)
    elif theta > pi/4 and theta < 3*pi/4:
        self.trajman.set_theta(pi/2)
        self.trajman.set_y(120 + decal)
    elif theta > 3*pi/4 or theta < -3*pi/4:
        self.trajman.set_theta(pi)
        self.trajman.set_x(2000 - 120 - decal)
    else:
        self.trajman.set_theta(-pi/2)
        self.trajman.set_y(3000 - 120 - decal)

    sleep(0.1)
    self.trajman.free()

    return RobotStatus.return_status(RobotStatus.Done)


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
    pos = self.actuators.recal_sensor_read(id) + dist_to_center
    print(f'[ROBOT] Measured distance: {pos}mm')

    if not axis_x and (side ^ (sensor == RecalSensor.Left)):
        pos = 3000 - pos
    if axis_x and ((not side) ^ (sensor == RecalSensor.Left)):
        pos = 2000 - pos

    if not init:
        position = self.trajman.get_position()
        print(f"[ROBOT] Old position: {position}")
        axis = 'x' if axis_x else 'y'
        if abs(position[axis] - pos) > 50:
            print(f'[ROBOT] WARNING: Recalibration failed, measured position is too far away from current position')
            print(f'Axis: {axis}. Current position: {position[axis]}. Measured position: {pos}')
            return

    setter = self.trajman.set_x if axis_x else self.trajman.set_y
    setter(pos)


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
        self.set_theta(pi/2)
        self.trajman.set_x(1000)
        self.trajman.set_y(1000)
        sleep(1)

    if x:
        print('[ROBOT] Recalibration X')
        theta = pi if side_x else 0

        status = RobotStatus.get_status(self.goth(theta, mirror=mirror, use_queue=False))
        if status != RobotStatus.Reached:
            return RobotStatus.return_status(status)

        if HOMEMADE_RECAL:
            self.homemade_recal(decal_x, use_queue=False)
        else:
            status = RobotStatus.get_status(self.recal(sens=0, decal=float(decal_x)))
            if status not in [RobotStatus.NotReached, RobotStatus.Reached]:
                return RobotStatus.return_status(status)

        sleep(1)
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

        if HOMEMADE_RECAL:
            self.homemade_recal(decal_y, use_queue=False)
        else:
            status = RobotStatus.get_status(self.recal(sens=0, decal=float(decal_y)))
            if status not in [RobotStatus.NotReached, RobotStatus.Reached]:
                return RobotStatus.return_status(status)

        sleep(1)
        if x_sensor != RecalSensor.No:
            self.recalibration_sensors(axis_x=True, side=side_y, sensor=x_sensor, mirror=mirror, init=init)

        status = RobotStatus.get_status(self.move_trsl(dest=100, acc=200, dec=200, maxspeed=200, sens=1))
        if status != RobotStatus.Reached:
            return RobotStatus.return_status(status)

    self.trajman.set_trsl_max_speed(speeds['trmax'])
    self.trajman.set_trsl_acc(speeds['tracc'])
    self.trajman.set_trsl_dec(speeds['trdec'])

    print('[ROBOT] New position: ' + str(self.trajman.get_position()))

    return RobotStatus.return_status(RobotStatus.Done)
