#!/usr/bin/env python3

from evolutek.lib.map.point import Point
from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service, ConfigVariable

from evolutek.lib.settings import ROBOT

RATIO_ROT = 10000
RATIO_TRSL = 1000

from enum import Enum
from functools import wraps
from math import pi, atan2, cos, sin
from threading import Event
from time import sleep

class Commands(Enum):
    DEBUG_MESSAGE      = 127
    TELEMETRY_MESSAGE  = 202
    DEBUG              = 126
    ACKNOWLEDGE        = 200
    MOVE_BEGIN         = 128
    MOVE_END           = 129

    GET_PID_TRSL       = 10
    GET_PID_ROT        = 11
    GET_POSITION       = 12
    GET_SPEEDS         = 13
    GET_WHEELS         = 14
    GET_DELTA_MAX      = 15
    GET_VECTOR_TRSL    = 16
    GET_VECTOR_ROT     = 17
    GOTO_XY            = 100
    GOTO_THETA         = 101
    MOVE_TRSL          = 102
    MOVE_ROT           = 103
    CURVE              = 104
    FREE               = 109
    RECALAGE           = 110
    SET_PWM            = 111
    STOP_ASAP          = 112
    SET_TELEMETRY      = 201
    SET_PID_TRSL       = 150
    SET_PID_ROT        = 151
    SET_TRSL_ACC       = 152
    SET_TRSL_DEC       = 153
    SET_TRSL_MAXSPEED  = 154
    SET_ROT_ACC        = 155
    SET_ROT_DEC        = 156
    SET_ROT_MAXSPEED   = 157
    SET_X              = 158
    SET_Y              = 159
    SET_THETA          = 160
    SET_WHEELS_DIAM    = 161
    SET_WHEELS_SPACING = 162
    SET_DELTA_MAX_ROT  = 163
    SET_DELTA_MAX_TRSL = 164
    SET_ROBOT_SIZE_X   = 165
    SET_ROBOT_SIZE_Y   = 166
    SET_DEBUG          = 200
    ERROR              = 255

#################
# The errors ID #
#################
class Errors(Enum):
    COULD_NOT_READ          = 1
    DESTINATION_UNREACHABLE = 2
    BAD_ORDER               = 3

def if_enabled(method):
    """
    A method can be disabled so that it cannot be used in any circumstances.
    """
    @wraps(method)
    def wrapped(self, *args, **kwargs):
        if self.disabled:
            self.log(what='disabled',
                     msg="Usage of {} is disabled".format(method))
            return
        return method(self, *args, **kwargs)

    return wrapped

# TODO: manage acc/dec
# TODO: Detect collision
@ Service.require('config')
class TrajMan(Service):

    def __init__(self):

        self.pos = Point(10000, 10000)
        self.theta = 0.0
        self.speed = 0.0

        self.goal_pos = Point(10000, 10000)
        self.goal_theta = 0.0

        self.disabled = False
        self.is_recaling = False
        self.sens = False
        self.tmp_trslmax = None
        self.tmp_rotmax = None
        self.has_stopped = Event()
        self.has_stopped.set()
        self.has_avoid = Event()
        self.need_to_stop = Event()

        cs = CellaservProxy()
        config = cs.config.get_section(name=ROBOT)

        # Trsl speeds
        self.trslacc = float(config['trsl_acc'])
        self.trsldec = float(config['trsl_dec'])
        self.trslmax = float(config['trsl_max'])

        # Rot speeds
        self.rotacc = float(config['rot_acc'])
        self.rotdec = float(config['rot_dec'])
        self.rotmax = float(config['rot_max'])

        # Deltas
        self.deltatrsl = float(config['delta_trsl'])
        self.deltarot = float(config['delta_rot'])

        # Robot size
        self.robot_size_x = float(config['robot_size_x'])
        self.robot_size_y = float(config['robot_size_y'])

        self.telemetry_refresh = float(config['telemetry_refresh'])

        super().__init__(ROBOT)

    @Service.thread
    def move_manager(self):

        while True:

            ################
            # ROT movement #
            ################

            tmp_rotmax = self.tmp_rotmax if self.tmp_rotmax is not None else self.rotmax
            self.tmp_rotmax = None

            while self.goal_theta < 0:
                self.goal_theta += 2 * pi

            while self.goal_theta > 2 * pi:
                self.goal_theta -= 2 * pi

            while self.theta < 0:
                self.theta += 2 * pi

            while self.theta > 2 * pi:
                self.theta -= 2 * pi

            sens = atan2(sin(self.goal_theta - self.theta), cos(self.goal_theta - self.theta)) > 0

            while self.need_to_stop.is_set():
                pass

            while not self.need_to_stop.is_set()\
                and abs(self.goal_theta - self.theta) > (tmp_rotmax / RATIO_ROT):
                if self.has_stopped.is_set():
                    self.has_stopped.clear()
                    self.publish(ROBOT + '_started')

                self.theta += (tmp_rotmax / RATIO_ROT) * (1 if sens else -1)

                while self.theta < 0:
                    self.theta += 2 * pi

                while self.theta > 2 * pi:
                    self.theta -= 2 * pi

                sleep(1 / RATIO_ROT)


            self.goal_theta = self.theta

            #################
            # TRSL Movement #
            #################

            tmp_tslmax = self.tmp_trslmax if self.tmp_trslmax is not None else self.trslmax
            self.tmp_trslmax = None

            dist = self.pos.dist(self.goal_pos)

            while not self.need_to_stop.is_set() and dist > tmp_tslmax / RATIO_TRSL:
                if self.has_stopped.is_set():
                    self.has_stopped.clear()
                    self.publish(ROBOT + '_started')

                dist -= tmp_tslmax / RATIO_TRSL

                new_x = self.pos.x + cos(self.theta) * tmp_tslmax / RATIO_TRSL * (1 if self.sens else -1)
                new_y = self.pos.y + sin(self.theta) * tmp_tslmax / RATIO_TRSL * (1 if self.sens else -1)
                self.pos = Point(new_x, new_y)

                sleep(1 / RATIO_TRSL)

            self.goal_pos = self.pos

            # End move
            if not self.has_stopped.is_set():
                self.has_stopped.set()
                self.publish(ROBOT + '_stopped')
            sleep(0.1)

    @Service.thread
    def publish_telemetry(self):
        while True:
            self.publish(ROBOT + '_telemetry', status='successful', robot=ROBOT,
                         telemetry={'x': self.pos.x,
                                   'y': self.pos.y,
                                   'theta': self.theta,
                                   'speed': self.speed})
            #sleep(self.telemetry_refresh / 200)
            sleep(0.05)

    #######
    # Set #
    #######

    @Service.action
    def set_trsl_acc(self, acc):
        self.trslacc = float(acc)

    @Service.action
    def set_trsl_dec(self, dec):
        self.trsldec = float(dec)

    @Service.action
    def set_trsl_max_speed(self, maxspeed):
        self.trslmax = float(maxspeed)

    @Service.action
    def set_rot_acc(self, acc):
        self.rotacc = float(acc)

    @Service.action
    def set_rot_dec(self, dec):
        self.rotdec = float(dec)

    @Service.action
    def set_rot_max_speed(self, maxspeed):
        self.rotmax = float(maxspeed)

    @Service.action
    def set_x(self, x):
        self.need_to_stop.set()
        while not self.has_stopped.is_set():
            pass

        pos = Point(float(x), self.pos.y)

        self.pos, self.goal_pos = pos, pos

        self.need_to_stop.clear()

    @Service.action
    def set_y(self, y):
        self.need_to_stop.set()
        while not self.has_stopped.is_set():
            pass

        pos = Point(self.pos.x, float(y))

        self.pos, self.goal_pos = pos, pos

        self.need_to_stop.clear()


    @Service.action
    def set_theta(self, theta):
        self.need_to_stop.set()
        while not self.has_stopped.is_set():
            pass

        self.theta, self.goal_theta = float(theta), float(theta)

        self.need_to_stop.clear()


    #######
    # Get #
    #######

    @Service.action
    def get_position(self):
        pos = self.pos.to_dict()
        pos['theta'] = self.theta
        return pos

    @Service.action
    def get_speeds(self):
        speeds = {
            'trslacc' : self.trslacc,
            'trsldec' : self.trsldec,
            'trslmax' : self.trslmax,
            'rotacc'  : self.rotacc,
            'rotdec'  : self.rotdec,
            'rotmax'  : self.rotmax
        }

        return speeds

    @Service.action
    def is_moving(self):
        return not self.has_stopped.is_set()

    @Service.action
    def status(self):
        return {'disabled': self.disabled,
                'moving': self.is_moving()}


    ##########
    # Action #
    ##########

    @Service.action
    def disable(self):
        self.disabled = True

    @Service.action
    def enable(self):
        self.disabled = False

    @Service.action
    def free(self):
        self.stop_asap(0, 0)
        pass

    @Service.action
    def unfree(self):
        pass

    @Service.action
    @if_enabled
    def goto_xy(self, x, y):
        self.need_to_stop.set()
        while not self.has_stopped.is_set():
            pass

        self.goal_pos = Point(float(x), float(y))

        angle = atan2(float(y) - self.pos.y, float(x) - self.pos.x) - atan2(0, 1)

        dist1 = abs(atan2(sin(self.theta - angle), cos(self.theta - angle)))
        dist2 = abs(atan2(sin(self.theta - angle - pi), cos(self.theta - angle - pi)))

        self.sens = dist1 < dist2
        self.goal_theta = angle if self.sens else (angle - pi)

        self.need_to_stop.clear()

    @Service.action
    @if_enabled
    def goto_theta(self, theta):
        self.need_to_stop.set()
        while not self.has_stopped.is_set():
            pass

        theta = float(theta)
        while theta > 2 * pi:
            theta -= 2 * pi
        self.goal_theta = theta

        self.need_to_stop.clear()

    @Service.action
    @if_enabled
    def move_trsl(self, dest, acc, dec, maxspeed, sens):
        self.need_to_stop.set()
        while not self.has_stopped.is_set():
            pass

        angle = self.theta + (0 if int(sens) else pi)

        self.sens = bool(int(sens))
        if float(maxspeed) > 0:
            self.tmp_trslmax = float(maxspeed)

        self.goal_pos = Point(
            self.goal_pos.x + float(dest) * cos(angle),
            self.goal_pos.y + float(dest) * sin(angle))

        self.need_to_stop.clear()

    @Service.action
    @if_enabled
    def move_rot(self, dest, acc, dec, maxspeed, sens):
        self.need_to_stop.set()
        while not self.has_stopped.is_set():
            pass

        self.sens = bool(int(sens))

        if float(maxspeed) > 0:
            self.tmp_rotmax = float(maxspeed)

        self.goal_theta = float(dest)

        self.need_to_stop.clear()

    @Service.action
    @if_enabled
    def recalibration(self, sens, decal=0, set=1):

        self.move_trsl(1000, sens=sens, acc=0, dec=0, maxspeed=0)
        sleep(0.1)

        self.has_stopped.wait()

        if set:
            decal = float(decal)
            sens = bool(int(sens))

            if pi/4 < self.theta < 3*pi/4:
                self.pos.y = (decal + self.robot_size_x) if not sens else (3000 - decal - self.robot_size_x)
            elif 3 * pi/4 < self.theta < 7 * pi/4 :
                self.pos.x = (decal + self.robot_size_x) if sens else (2000 - decal - self.robot_size_x)
            elif 7 * pi/4 < self.theta < 11 * pi/4:
                self.pos.y = (decal + self.robot_size_x) if sens else (3000 - decal - self.robot_size_x)
            else:
                self.pos.x = (decal + self.robot_size_x) if not sens else (2000 - decal - self.robot_size_x)

    @Service.action
    def stop_asap(self, trsldec, rotdec):
        self.need_to_stop.set()
        while not self.has_stopped.is_set():
            pass
        self.need_to_stop.clear()

def main():
    fake_trajman = TrajMan()
    fake_trajman.run()

if __name__ == '__main__':
    main()
