#!/usr/bin/env python3

from enum import Enum
from functools import wraps
import os
from queue import Queue
import serial
from struct import pack, unpack, calcsize
from threading import Thread, Event
from time import sleep
import board

from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service, ConfigVariable
from cellaserv.settings import make_setting

make_setting('TRAJMAN_PORT', '/dev/serial0', 'trajman', 'port', 'TRAJMAN_PORT')
make_setting('TRAJMAN_BAUDRATE', 38400, 'trajman', 'baudrate',
             'TRAJMAN_BAUDRATE', int)
from cellaserv.settings import TRAJMAN_PORT, TRAJMAN_BAUDRATE

from evolutek.lib.gpio import Gpio, Edge as GpioEdge
from evolutek.lib.mdb import Mdb
from evolutek.lib.settings import ROBOT

#######################
# All the commands ID #
#######################
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

# Emergency stop button
BAU_GPIO = 21

#################
# The errors ID #
#################
class Errors(Enum):
    COULD_NOT_READ          = 1
    DESTINATION_UNREACHABLE = 2
    BAD_ORDER               = 3

class AckTimeout(Exception):
    """Raised when a ACK message is not received in time."""
    def __init__(self):
        super().__init__("AckTimeout")


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

# TODO: check if we collided

@Service.require("config")
class TrajMan(Service):
    """
    The trajman service is the interface between cellaserv and the motors of
    the robot.

    It uses two threads: one for the service and one to read on the serial
    asynchronously.

    It can be disabled in order to stop processing commands and make sure that
    the robot will not move.
    """

    w1 = ConfigVariable(section=ROBOT, option="wheel_diam1", coerc=float)
    w2 = ConfigVariable(section=ROBOT, option="wheel_diam2", coerc=float)
    spacing = ConfigVariable(section=ROBOT, option="wheels_spacing", coerc=float)
    pidtp = ConfigVariable(section=ROBOT, option="pidtrsl_p", coerc=float)
    pidti = ConfigVariable(section=ROBOT, option="pidtrsl_i", coerc=float)
    pidtd = ConfigVariable(section=ROBOT, option="pidtrsl_d", coerc=float)
    pidrp = ConfigVariable(section=ROBOT, option="pidrot_p", coerc=float)
    pidri = ConfigVariable(section=ROBOT, option="pidrot_i", coerc=float)
    pidrd = ConfigVariable(section=ROBOT, option="pidrot_d", coerc=float)
    trslacc = ConfigVariable(section=ROBOT, option="trsl_acc", coerc=float)
    trsldec = ConfigVariable(section=ROBOT, option="trsl_dec", coerc=float)
    trslmax = ConfigVariable(section=ROBOT, option="trsl_max", coerc=float)
    rotacc = ConfigVariable(section=ROBOT, option="rot_acc", coerc=float)
    rotdec = ConfigVariable(section=ROBOT, option="rot_dec", coerc=float)
    rotmax = ConfigVariable(section=ROBOT, option="rot_max", coerc=float)
    deltatrsl = ConfigVariable(section=ROBOT, option="delta_trsl", coerc=float)
    deltarot = ConfigVariable(section=ROBOT, option="delta_rot", coerc=float)
    robot_size_x = ConfigVariable(section=ROBOT, option="robot_size_x", coerc=float)
    robot_size_y = ConfigVariable(section=ROBOT, option="robot_size_y", coerc=float)
    telemetry_refresh = ConfigVariable(section=ROBOT, option="telemetry_refresh", coerc=float)
    stoptrsldec = ConfigVariable(section=ROBOT, option="stop_trsl_dec", coerc=float)
    stoptrslrot = ConfigVariable(section=ROBOT, option="stop_trsl_rot", coerc=float)

    def __init__(self):
        super().__init__(ROBOT)

        self.cs = CellaservProxy()

        # Messages comming from the motor card
        self.queue = Queue()
        self.ack_recieved = Event()

        self.has_stopped = Event()
        self.has_avoid = Event()

        # Used to generate debug
        self.debug_file = None
        self.disabled = False

        self.serial = serial.Serial(TRAJMAN_PORT, TRAJMAN_BAUDRATE)

        self.thread = Thread(target=self.async_read)
        self.thread.start()

        """ AVOID """
        self.telemetry = None
        self.avoid_disabled = Event()
        self.front = False
        self.back = False
        self.is_robot = False
        self.side = ''

        # MDB
        self.mdb = Mdb()

        # Set config of the robot
        self.trsl_max_speed = self.trslmax()
        self.rot_max_speed = self.rotmax()
        self.stop_trsl_dec = self.stoptrsldec()
        self.stop_trsl_rot = self.stoptrslrot()

        self.init_sequence()
        self.set_telemetry(0)

        self.set_wheels_diameter(w1=self.w1(), w2=self.w2())
        self.set_wheels_spacing(spacing=self.spacing())

        self.set_pid_trsl(self.pidtp(), self.pidti(), self.pidtd())
        self.set_pid_rot(self.pidrp(), self.pidri(), self.pidrd())

        self.set_trsl_acc(self.trslacc())
        self.set_trsl_dec(self.trsldec())
        self.trsl_max_speed = self.trslmax()
        self.set_trsl_max_speed(self.trsl_max_speed)

        self.set_rot_acc(self.rotacc())
        self.set_rot_dec(self.rotdec())
        self.set_rot_max_speed(self.rotmax())

        self.set_delta_max_rot(self.deltarot())
        self.set_delta_max_trsl(self.deltatrsl())

        self.set_robot_size_x(self.robot_size_x())
        self.set_robot_size_y(self.robot_size_y())

        self.set_telemetry(self.telemetry_refresh())
        self.set_telemetry(500)

        # Get and set MDB config
        self.avoid_refresh = float(self.cs.config.get('avoid', 'refresh'))
        near = self.cs.config.get('avoid', 'near')
        far = self.cs.config.get('avoid', 'far')
        brightness = self.cs.config.get('avoid', 'mdb_brightness')
        self.set_mdb_config(near=near, far=far, brightness=brightness)

        # BAU (emergency stop)
        bau_gpio = Gpio(BAU_GPIO, 'bau', dir=False, edge=GpioEdge.BOTH)
        self.bau_status = bau_gpio.read()
        # If the BAU is set at init, free the robot
        if not self.bau_status:
            self.free()

        bau_gpio.auto_refresh(callback=self.handle_bau)


    # Threading sending the telemetry
    #@Service.thread
    def send_telemetry(self):
        while True:
            if self.telemetry is not None:
                self.publish(ROBOT + '_telemetry', status='successful', telemetry = self.telemetry, robot = ROBOT)
            print('Sending telemetry')
            sleep(0.5)

    """ BAU """
    # BAU handler
    @Service.action
    def handle_bau(self, value, event='', name='', id=0):
        self.bau_status = value
        if value == 0:
            self.free()
            self.disable()
        else:
            self.enable()
            self.unfree()

    @Service.action
    def get_bau_status(self):
        return self.bau_status

    """ AVOID """

    # Thread for avoidance
    @Service.thread
    def loop_avoid(self):
        while True:
            if self.telemetry is None:
                continue
            if self.avoid_disabled.isSet():
                continue
            self.check_avoid()
            sleep(self.avoid_refresh)

    # Check and stop the robot if it need to avoid
    @Service.action
    def check_avoid(self):

        # Read MDB
        zones = self.mdb.get_zones()
        front = zones['front']
        back = zones['back']
        is_robot = zones['is_robot']

        # End detection
        if (self.side == 'front' and not front) or (self.side == 'back' and not back):
            self.side = None
            self.publish(ROBOT + '_end_avoid')

        if(self.is_robot != is_robot):
            self.set_speeds(not self.is_robot)

        # Change the values after the read to avoid race conflict
        self.front = front
        self.back = back
        self.is_robot = is_robot

        if self.has_avoid.isSet() or self.has_stopped.isSet():
            return

        # Check if the robot need to stop
        if self.telemetry['speed'] > 0.0 and self.front:
            self.stop_robot('front')
            print("[AVOID] Front detection")
        elif self.telemetry['speed'] < 0.0 and self.back:
            self.stop_robot('back')
            print("[AVOID] Back detection")


    # Get the avoidance status
    @Service.action
    def avoid_status(self):
        status = {
            'front' : self.front,
            'back' : self.back,
            'side': self.side,
            'is_robot' : self.is_robot,
            'avoid' : self.has_avoid.isSet(),
            'enabled' : not self.avoid_disabled.isSet(),
        }

        return status

    # Set moving speeds of the robot
    @Service.action
    def set_speeds(self, state):
        trsl_speed = self.trsl_max_speed
        rot_speed = self.rot_max_speed
        self.set_trsl_max_speed(trsl_speed)
        self.set_rot_max_speed(rot_speed)

    # Stop the robot
    @Service.action
    def stop_robot(self, side=None):
        stopped = False
        self.side = side
        self.has_avoid.set()
        try:
            self.stop_asap(self.stop_trsl_dec, self.stop_trsl_rot)
            stopped = True
        except Exception as e:
            print('[AVOID] Failed to abort ai of %s: %s' % (ROBOT, str(e)))
        print('[AVOID] Stopping robot, %s detection triggered' % side)
        sleep(0.5)

    # Enable avoidance
    @Service.action
    def enable_avoid(self):
        print('[AVOID] Enable')
        self.avoid_disabled.clear()
        self.enable_mdb()

    # Disable avoidance
    @Service.action
    def disable_avoid(self):
        print('[AVOID] Disable')
        self.avoid_disabled.set()
        self.front = False
        self.back = False
        self.is_robot = False
        # Get speeds back to normal
        self.set_speeds(True)
        self.has_avoid.clear()
        self.disable_mdb()

    # Enable MDB
    @Service.action
    def enable_mdb(self):
        print('[AVOID] Enabling mdb')
        self.mdb.enable()

    # Disable MDB
    @Service.action
    def disable_mdb(self):
        print('[AVOID] Disabling mdb')
        self.mdb.disable()

    # Put MDB in error mode
    @Service.action
    def error_mdb(self, enable=True):
        enable = enable in ['True', 'true', 't', 'T', True, '1', 1]
        if(enable): print('[AVOID] Putting mdb in error mode')
        else: print('[AVOID] Disabling error mode on MDB')
        self.mdb.error_mode(enable)

    def write(self, data):
        """Write data to serial and flush."""

        self.serial.write(data)
        self.serial.flush()

    def command(self, data):
        """Handle commands sent to the card and wait for ack."""

        self.ack_recieved.clear()
        self.write(data)
        if not self.ack_recieved.wait(timeout=1):
            # If no ACK is received within 1s
            raise AckTimeout

    def get_command(self, data):
        """Handle commands that waits for an answer from the motors."""

        self.write(data)
        # If no data is received within 1s, raises the Empty exception
        return self.queue.get(timeout=1)

    ########
    # Meta #
    ########

    @Service.action
    def status(self):
        return {'disabled': self.disabled,
                'moving': self.is_moving()}

    ###########
    # Actions #
    ###########

    @Service.action
    @if_enabled
    def goto_xy(self, x, y):
        tab = pack('B', 2 + calcsize('ff'))
        tab += pack('B', Commands.GOTO_XY.value)
        tab += pack('ff', float(x), float(y))
        self.command(bytes(tab))

    @Service.action
    @if_enabled
    def goto_theta(self, theta):
        tab = pack('B', 6)
        tab += pack('B', Commands.GOTO_THETA.value)
        tab += pack('f', float(theta))
        self.command(bytes(tab))

    @Service.action
    @if_enabled
    def move_trsl(self, dest, acc, dec, maxspeed, sens):
        tab = pack('B', 19)
        tab += pack('B', Commands.MOVE_TRSL.value)
        tab += pack('ffffb', float(dest), float(acc), float(dec),
                    float(maxspeed), int(sens))
        self.command(bytes(tab))

    @Service.action
    @if_enabled
    def move_rot(self, dest, acc, dec, maxspeed, sens):
        tab = pack('B', 19)
        tab += pack('B', Commands.MOVE_ROT.value)
        tab += pack('ffffb', float(dest), float(acc), float(dec),
                    float(maxspeed), int(sens))
        self.command(bytes(tab))

    @Service.action
    @if_enabled
    def curve(self, dt, at, det, mt, st, dr, ar, der, mr, sr, delayed):
        tab = pack('B', 35)
        tab += pack('B', Commands.CURVE.value)
        tab += pack('ffffffff', float(dt), float(at), float(det), float(mt),
                    float(dr), float(ar), float(der), float(mt))

        s = 0
        s += 1 if int(st) == 1 else 0
        s += 2 if int(sr) == 1 else 0
        s += 4 if int(delayed) == 1 else 0

        self.log_serial(s)
        tab += pack('B', s)
        self.write(bytes(tab))

    @Service.action
    def free(self):
        print('[TRAJMAN] Freed robot')
        tab = pack('B', 2)
        tab += pack('B', Commands.FREE.value)
        self.command(bytes(tab))

    @Service.action
    @if_enabled
    def unfree(self):
        self.move_trsl(0, 1, 1, 1, 1)

    @Service.action
    def disable(self):
        self.disabled = True

    @Service.action
    def enable(self):
        self.disabled = False

    #######
    # Set #
    #######

    @Service.action
    def set_telemetry(self, inter):
        tab = pack('B', 4)
        tab += pack('B', Commands.SET_TELEMETRY.value)
        tab += pack('H', int(inter))
        self.command(bytes(tab))

    @Service.action
    def set_pid_trsl(self, P, I, D):
        tab = pack('B', 14)
        tab += pack('B', Commands.SET_PID_TRSL.value)
        tab += pack('fff', float(P), float(I), float(D))
        self.command(bytes(tab))

    @Service.action
    def set_pid_rot(self, P, I, D):
        tab = pack('B', 14)
        tab += pack('B', Commands.SET_PID_ROT.value)
        tab += pack('fff', float(P), float(I), float(D))
        self.command(bytes(tab))

    @Service.action
    def set_debug(self, state: "on or off"):
        tab = pack('B', 3)
        tab += pack('B', Commands.SET_DEBUG.value)
        if state == "on":
            self.debug_file = open("debug.data", "w")
            tab += pack('B', 1)

            data = self.get_pid_trsl()
            with open("trslpid.data", "w") as f:
                f.write("P = {kp} I = {ki} D = {kd}\n".format(**data))

            data = self.get_pid_rot()

            with open("rotpid.data", "w") as f:
                f.write("P = {kp} I = {ki} D = {kd}\n".format(**data))
        else:
            tab += pack('B', 0)
            if self.debug_file:
                self.debug_file.close()

        self.command(bytes(tab))

    @Service.action
    def set_trsl_acc(self, acc):
        tab = pack('B', 6)
        tab += pack('B', Commands.SET_TRSL_ACC.value)
        tab += pack('f', float(acc))
        self.command(bytes(tab))

    @Service.action
    def set_trsl_max_speed(self, maxspeed):
        if maxspeed is None:
            maxspeed = self.trsl_max_speed
        tab = pack('B', 6)
        tab += pack('B', Commands.SET_TRSL_MAXSPEED.value)
        tab += pack('f', float(maxspeed))
        self.command(bytes(tab))


    @Service.action
    def set_trsl_dec(self, dec):
        tab = pack('B', 6)
        tab += pack('B', Commands.SET_TRSL_DEC.value)
        tab += pack('f', float(dec))
        self.command(bytes(tab))

    @Service.action
    def set_rot_acc(self, acc):
        tab = pack('B', 6)
        tab += pack('B', Commands.SET_ROT_ACC.value)
        tab += pack('f', float(acc))
        self.command(bytes(tab))

    @Service.action
    def set_rot_max_speed(self, maxspeed):
        tab = pack('B', 6)
        tab += pack('B', Commands.SET_ROT_MAXSPEED.value)
        tab += pack('f', float(maxspeed))
        self.command(bytes(tab))

    @Service.action
    def set_rot_dec(self, dec):
        tab = pack('B', 6)
        tab += pack('B', Commands.SET_ROT_DEC.value)
        tab += pack('f', float(dec))
        self.command(bytes(tab))

    @Service.action
    def set_x(self, x):
        tab = pack('B', 6)
        tab += pack('B', Commands.SET_X.value)
        tab += pack('f', float(x))
        self.command(bytes(tab))

    @Service.action
    def set_y(self, y):
        tab = pack('B', 6)
        tab += pack('B', Commands.SET_Y.value)
        tab += pack('f', float(y))
        self.command(bytes(tab))

    @Service.action
    def set_theta(self, theta):
        tab = pack('B', 6)
        tab += pack('B', Commands.SET_THETA.value)
        tab += pack('f', float(theta))
        self.command(bytes(tab))

    @Service.action
    def set_wheels_diameter(self, w1, w2):
        tab = pack('B', 10)
        tab += pack('B', Commands.SET_WHEELS_DIAM.value)
        tab += pack('ff', float(w1), float(w2))
        self.command(bytes(tab))

    @Service.action
    def set_delta_max_rot(self, delta):
        tab = pack('B', 6)
        tab += pack('B', Commands.SET_DELTA_MAX_ROT.value)
        tab += pack('f', float(delta))
        self.command(bytes(tab))

    @Service.action
    def set_delta_max_trsl(self, delta):
        tab = pack('B', 6)
        tab += pack('B', Commands.SET_DELTA_MAX_TRSL.value)
        tab += pack('f', float(delta))
        self.command(bytes(tab))

    @Service.action
    def set_wheels_spacing(self, spacing):
        tab = pack('B', 6)
        tab += pack('B', Commands.SET_WHEELS_SPACING.value)
        tab += pack('f', float(spacing))
        self.command(bytes(tab))

    @Service.action
    def set_pwm(self, left, right):
        tab = pack('B', 10)
        tab += pack('B', Commands.SET_PWM.value)
        tab += pack('ff', float(left), float(right))
        self.command(bytes(tab))

    @Service.action
    def set_robot_size_x(self, size):
        tab = pack('B', 6)
        tab += pack('B', Commands.SET_ROBOT_SIZE_X.value)
        tab += pack('f', float(size))
        self.command(bytes(tab))

    @Service.action
    def set_robot_size_y(self, size):
        tab = pack('B', 6)
        tab += pack('B', Commands.SET_ROBOT_SIZE_Y.value)
        tab += pack('f', float(size))
        self.command(bytes(tab))

    @Service.action
    def stop_asap(self, trsldec, rotdec):
        tab = pack('B', 10)
        tab += pack('B', Commands.STOP_ASAP.value)
        tab += pack('ff', float(trsldec), float(rotdec))
        self.command(bytes(tab))

    # mode: sets the MDB debug mode. 0: Distances, 1: Zones, 2: Loading, 3: Disabled
    # yellow: sets the color of the loading animation. True: yellow, False: blue
    # near: sets the distance the robot considers as too close (stops)
    # far: sets the distance the robot considers as dangerous (slows down)
    # brightness: sets the brightness of the leds in the mdb
    @Service.action
    def set_mdb_config(self, mode=None, yellow=None, near=None, far=None, brightness=None):
        if mode is not None:
            self.mdb.set_debug_mode(int(mode))
        if yellow is not None:
            self.mdb.set_color(yellow in [True, 'True', 'true', 1, '1'])
        if near is not None:
            self.mdb.set_near(int(near))
        if far is not None:
            self.mdb.set_far(int(far))
        if brightness is not None:
            self.mdb.set_brightness(int(brightness))

    #######
    # Get #
    #######

    @Service.action
    def get_pid_trsl(self):
        tab = pack('B', 2)
        tab += pack('B', Commands.GET_PID_TRSL.value)
        return self.get_command(bytes(tab))

    @Service.action
    def get_pid_rot(self):
        tab = pack('B', 2)
        tab += pack('B', Commands.GET_PID_ROT.value)
        return self.get_command(bytes(tab))

    @Service.action
    def get_position(self):
        self.log_serial("get_position")
        tab = pack('B', 2)
        tab += pack('B', Commands.GET_POSITION.value)
        return self.get_command(bytes(tab))

    @Service.action
    def get_speeds(self):
        tab = pack('B', 2)
        tab += pack('B', Commands.GET_SPEEDS.value)
        return self.get_command(bytes(tab))

    @Service.action
    def get_wheels(self):
        tab = pack('B', 2)
        tab += pack('B', Commands.GET_WHEELS.value)
        return self.get_command(bytes(tab))

    @Service.action
    def get_delta_max(self):
        tab = pack('B', 2)
        tab += pack('B', Commands.GET_DELTA_MAX.value)
        return self.get_command(bytes(tab))

    @Service.action
    def get_vector_trsl(self):
        tab = pack('B', 2)
        tab += pack('B', Commands.GET_VECTOR_TRSL.value)
        return self.get_command(bytes(tab))

    @Service.action
    def get_vector_rot(self):
        tab = pack('B', 2)
        tab += pack('B', Commands.GET_VECTOR_ROT.value)
        return self.get_command(bytes(tab))

    @Service.action
    def flush_serial(self):
        self.log_serial("Clearing CM buffer")
        self.write(bytes(128))

    @Service.action
    def init_sequence(self):
        self.log_serial("Sending init sequence")
        self.write(bytes([5]))
        self.write(bytes([254]))
        self.write(bytes([0xAA]))
        self.write(bytes([0xAA]))
        self.write(bytes([0xAA]))

    @Service.action
    def flush_queue(self):
        """
        If the serial spits out more messages than expected it will be
        necessary to clean the message buffer.
        """
        self.log_serial("Clearing queue")
        ret = []
        while not self.queue.empty():
            ret.append(self.queue.get())
        return ret

    @Service.action
    def is_moving(self):
        return not self.has_stopped.is_set()

    @Service.action
    def get_zones(self):
        return self.mdb.get_zones()

    @Service.action
    def get_scan(self):
        return self.mdb.get_scan()

    # Calibrate

    @Service.action
    @if_enabled
    def recalibration(self, sens, decal=0, set=1):
        tab = pack('B', 7)
        tab += pack('B', Commands.RECALAGE.value)
        tab += pack('B', int(sens))
        tab += pack('f', float(decal))
        tab += pack('B', int(set))
        return self.command(bytes(tab))

    # Thread 2

    def log_serial(self, *args):
        print(*args)

    def async_read(self):
        """Read events from serial and add them to the queue."""
        while True:
            length = unpack('b', self.serial.read())[0]
            tab = [length]
            # self.log_debug("Message length expected:", length)
            for i in range(length - 1):  # FIXME: use read(lenght)
                tab += self.serial.read()
            # self.log_debug("Received message with length:", len(tab))

            if len(tab) > 1:
                if tab[1] == Commands.ACKNOWLEDGE.value:
                    self.log_serial("Robot acknowledged!")
                    self.ack_recieved.set()

                elif tab[1] == Commands.GET_PID_TRSL.value:
                    self.log_serial("Received the robot's translation pid!")

                    _, _, kp, ki, kd = unpack("=bbfff", bytes(tab))
                    self.log("P =", kp, "I =", ki, "D =", kd)

                    self.queue.put({'kp': kp, 'ki': ki, 'kd': kd})

                elif tab[1] == Commands.GET_PID_ROT.value:
                    self.log_serial("Received the robot's rotation pid!")

                    _, _, kp, ki, kd = unpack("=bbfff", bytes(tab))
                    self.log("P =", kp, "I =", ki, "D =", kd)

                    self.queue.put({'kp': kp, 'ki': ki, 'kd': kd})

                elif tab[1] == Commands.GET_POSITION.value:
                    self.log_serial("Received the robot's position!")

                    _, _, x, y, theta = unpack('=bbfff', bytes(tab))
                    self.log_serial("Position is x:", x, "y:", y, "th:", theta)

                    self.queue.put({
                        'x': x,
                        'y': y,
                        'theta': theta,
                    })

                elif tab[1] == Commands.MOVE_BEGIN.value:
                    self.log_serial("Robot started to move!")
                    self.publish(ROBOT + '_started')
                    self.has_stopped.clear()

                elif tab[1] == Commands.MOVE_END.value:
                    self.log_serial("Robot stopped moving!")
                    self.has_stopped.set()
                    self.publish(ROBOT + '_stopped', has_avoid=self.has_avoid.is_set())
                    self.has_avoid.clear()

                elif tab[1] == Commands.GET_SPEEDS.value:
                    a, b, tracc, trdec, trmax, rtacc, rtdec, rtmax = unpack('=bbffffff', bytes(tab))

                    self.queue.put({
                        'tracc': tracc,
                        'trdec': trdec,
                        'trmax': trmax,
                        'rtacc': rtacc,
                        'rtdec': rtdec,
                        'rtmax': rtmax,
                    })

                    self.log_serial("Translation: Acc:", tracc, "\tDec:", trdec, "\tMax :", trmax, " (mm/(s*s) mm/(s*s) mm/s)")
                    self.log_serial("Rotation:    Acc: {0:.3f}\tDec: {1:.3f}\tMax: {2:.3f} (rad/(s*s) rad/(s*s) rad/s)".format(rtacc, rtdec, rtmax))

                elif tab[1] == Commands.GET_WHEELS.value:
                    a, b, spacing, left_diameter, right_diameter = unpack('=bbfff', bytes(tab))

                    self.queue.put({
                        'spacing': spacing,
                        'left_diameter': left_diameter,
                        'right_diameter': right_diameter,
                    })

                    self.log_serial("Spacing: ", spacing, " Left: ", left_diameter, " Right: ", right_diameter)

                elif tab[1] == Commands.GET_DELTA_MAX.value:
                    a, b, translation, rotation = unpack('=bbff', bytes(tab))

                    self.queue.put({
                        'delta_rot_max': rotation,
                        'delta_trsl_max': translation,
                    })

                    self.log_serial("delta_rot_max : ", rotation, "delta_trsl_max", translation)

                elif tab[1] == Commands.GET_VECTOR_TRSL.value:
                    a, b, speed = unpack('=bbf', bytes(tab))

                    self.queue.put({
                        'trsl_vector': speed,
                    })

                    self.log_serial("Translation vector: ", speed)

                elif tab[1] == Commands.GET_VECTOR_ROT.value:
                    a, b, speed = unpack('=bbf', bytes(tab))

                    self.queue.put({
                        'rot_vector': speed,
                    })

                    self.log_serial("Rotation vector: ", speed)

                elif tab[1] == Commands.RECALAGE.value:
                    a, b, recal_xpos, recal_ypos, recal_theta = unpack('=bbfff', bytes(tab))

                    self.queue.put({
                        'recal_xpos': recal_xpos,
                        'recal_ypos': recal_ypos,
                        'recal_theta': recal_theta,
                    })

                elif tab[1] == Commands.DEBUG_MESSAGE.value:
                    counter, commandid, time, xpos, wpx, ypos, wpy, theta, wpth, trspeed, rotspeed, trp, tri, trd, rtp, rti, rtd = unpack("=bbfffffffffffffff", bytes(tab))
                    try:
                        if self.debug_file and not self.debug_file.closed:
                            self.debug_file.write(str(time) + " ")
                            self.debug_file.write(str(xpos) + " " + str(ypos) + " " + str(theta) + " ")
                            self.debug_file.write(str(wpx) + " " + str(wpy) + " " + str(wpth) + " ")
                            self.debug_file.write(str(trspeed) + " " + str(rotspeed) + " ")
                            self.debug_file.write(str(trp) + " " + str(tri) + " " + str(trd) + " ")
                            self.debug_file.write(str(rtp) + " ")
                            self.debug_file.write(str(rti) + " ")
                            self.debug_file.write(str(rtd) + " ")
                            self.debug_file.write("\n")
                    except:
                        pass

                elif tab[1] == Commands.TELEMETRY_MESSAGE.value:
                    counter, commandid, xpos, ypos, theta, speed =unpack('=bbffff', bytes(tab))
                    self.telemetry = { 'x': xpos, 'y' : ypos, 'theta' : theta, 'speed' : speed}
                    """try:
                        self.publish(ROBOT + '_telemetry', status='successful', telemetry = self.telemetry, robot = ROBOT)
                    except:
                        self.publish(ROBOT + '_telemetry', status='failed', telemetry = None, robot = ROBOT)"""
                elif tab[1] == Commands.ERROR.value:
                    self.log("CM returned an error")
                    if tab[2] == Errors.COULD_NOT_READ.value:
                        self.log("Error was: COULD_NOT_READ")
                    elif tab[2] == Errors.DESTINATION_UNREACHABLE.value:
                        self.log("Error was: DESTINATION_UNREACHABLE")
                    elif tab[2] == Erros.BAD_ORDER.value:
                        self.log("Error was: BAD_ORDER")

                elif tab[1] == Commands.DEBUG.value:
                    message = bytes(tab)[2:]
                    print(message)

                else:
                    self.log("Message not recognised")

def main():
    trajman = TrajMan()
    trajman.run()

if __name__ == '__main__':
    main()
