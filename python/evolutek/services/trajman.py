#!/usr/bin/env python3

from functools import wraps
from queue import Queue
from struct import pack, unpack, calcsize
from threading import Thread, Event
import serial
from cellaserv.service import Service, ConfigVariable
from cellaserv.settings import make_setting
import os
from time import sleep

make_setting('TRAJMAN_PORT', '/dev/MotorCard', 'trajman', 'port', 'TRAJMAN_PORT')
make_setting('TRAJMAN_BAUDRATE', 38400, 'trajman', 'baudrate',
             'TRAJMAN_BAUDRATE', int)
from cellaserv.settings import TRAJMAN_PORT, TRAJMAN_BAUDRATE

from evolutek.lib.settings import ROBOT

#######################
# All the commands ID #
#######################

#  FIXME: Use an IntEnum: https://docs.python.org/3/library/enum.html
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

    identification = ROBOT

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

    def __init__(self):
        super().__init__()

        # Messages comming from the motor card
        self.queue = Queue()
        self.ack_recieved = Event()

        self.has_stopped = Event()

        # Used to generate debug
        self.debug_file = None
        self.disabled = False

        self.serial = serial.Serial(TRAJMAN_PORT, TRAJMAN_BAUDRATE)

        self.thread = Thread(target=self.async_read)
        self.thread.daemon = True
        self.thread.start()
        
        #self.thread2 = Thread(target=self.telemetry)
        #self.thread2.daemon = True
        #self.thread2.start()

        self.init_sequence()
        self.set_telemetry(0)

        self.set_wheels_diameter(w1=self.w1(), w2=self.w2())
        self.set_wheels_spacing(spacing=self.spacing())

        self.set_pid_trsl(self.pidtp(), self.pidti(), self.pidtd())
        self.set_pid_rot(self.pidrp(), self.pidri(), self.pidrd())

        self.set_trsl_acc(self.trslacc())
        self.set_trsl_dec(self.trsldec())
        self.set_trsl_max_speed(self.trslmax())

        self.set_rot_acc(self.rotacc())
        self.set_rot_dec(self.rotdec())
        self.set_rot_max_speed(self.rotmax())

        self.set_delta_max_rot(self.deltarot())
        self.set_delta_max_trsl(self.deltatrsl())

        self.set_robot_size_x(self.robot_size_x())
        self.set_robot_size_y(self.robot_size_y())
        
        print(self.telemetry_refresh())

        self.set_telemetry(self.telemetry_refresh())
        self.set_telemetry(500)

    #@Service.thread
    def telemetry(self):
        sleep(5)
        while True:
            position = self.get_position()
            vector_trsl = self.get_vector_trsl()
            telemetry = {
                'x': position['x'],
                'y': position['y'],
                'theta': position['theta'],
                'speed': vector_trsl['trsl_vector']
            }
            self.publish(ROBOT + '_telemetry', status='successful', telemetry=telemetry)
            sleep(1)

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
        tab += pack('B', GOTO_XY)
        tab += pack('ff', float(x), float(y))
        self.command(bytes(tab))

    @Service.action
    @if_enabled
    def goto_theta(self, theta):
        tab = pack('B', 6)
        tab += pack('B', GOTO_THETA)
        tab += pack('f', float(theta))
        self.command(bytes(tab))

    @Service.action
    @if_enabled
    def move_trsl(self, dest, acc, dec, maxspeed, sens):
        tab = pack('B', 19)
        tab += pack('B', MOVE_TRSL)
        tab += pack('ffffb', float(dest), float(acc), float(dec),
                    float(maxspeed), int(sens))
        self.command(bytes(tab))

    @Service.action
    @if_enabled
    def move_rot(self, dest, acc, dec, maxspeed, sens):
        tab = pack('B', 19)
        tab += pack('B', MOVE_ROT)
        tab += pack('ffffb', float(dest), float(acc), float(dec),
                    float(maxspeed), int(sens))
        self.command(bytes(tab))

    @Service.action
    @if_enabled
    def curve(self, dt, at, det, mt, st, dr, ar, der, mr, sr, delayed):
        tab = pack('B', 35)
        tab += pack('B', CURVE)
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
        tab = pack('B', 2)
        tab += pack('B', FREE)
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
        tab += pack('B', SET_TELEMETRY)
        tab += pack('H', int(inter))
        self.command(bytes(tab))

    @Service.action
    def set_pid_trsl(self, P, I, D):
        tab = pack('B', 14)
        tab += pack('B', SET_PID_TRSL)
        tab += pack('fff', float(P), float(I), float(D))
        self.command(bytes(tab))

    @Service.action
    def set_pid_rot(self, P, I, D):
        tab = pack('B', 14)
        tab += pack('B', SET_PID_ROT)
        tab += pack('fff', float(P), float(I), float(D))
        self.command(bytes(tab))

    @Service.action
    def set_debug(self, state: "on or off"):
        tab = pack('B', 3)
        tab += pack('B', SET_DEBUG)
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
        tab += pack('B', SET_TRSL_ACC)
        tab += pack('f', float(acc))
        self.command(bytes(tab))

    @Service.action
    def set_trsl_max_speed(self, maxspeed):
        tab = pack('B', 6)
        tab += pack('B', SET_TRSL_MAXSPEED)
        tab += pack('f', float(maxspeed))
        self.command(bytes(tab))

    @Service.action
    def set_trsl_dec(self, dec):
        tab = pack('B', 6)
        tab += pack('B', SET_TRSL_DEC)
        tab += pack('f', float(dec))
        self.command(bytes(tab))

    @Service.action
    def set_rot_acc(self, acc):
        tab = pack('B', 6)
        tab += pack('B', SET_ROT_ACC)
        tab += pack('f', float(acc))
        self.command(bytes(tab))

    @Service.action
    def set_rot_max_speed(self, maxspeed):
        tab = pack('B', 6)
        tab += pack('B', SET_ROT_MAXSPEED)
        tab += pack('f', float(maxspeed))
        self.command(bytes(tab))

    @Service.action
    def set_rot_dec(self, dec):
        tab = pack('B', 6)
        tab += pack('B', SET_ROT_DEC)
        tab += pack('f', float(dec))
        self.command(bytes(tab))

    @Service.action
    def set_x(self, x):
        tab = pack('B', 6)
        tab += pack('B', SET_X)
        tab += pack('f', float(x))
        self.command(bytes(tab))

    @Service.action
    def set_y(self, y):
        tab = pack('B', 6)
        tab += pack('B', SET_Y)
        tab += pack('f', float(y))
        self.command(bytes(tab))

    @Service.action
    def set_theta(self, theta):
        tab = pack('B', 6)
        tab += pack('B', SET_THETA)
        tab += pack('f', float(theta))
        self.command(bytes(tab))

    @Service.action
    def set_wheels_diameter(self, w1, w2):
        tab = pack('B', 10)
        tab += pack('B', SET_WHEELS_DIAM)
        tab += pack('ff', float(w1), float(w2))
        self.command(bytes(tab))

    @Service.action
    def set_delta_max_rot(self, delta):
        tab = pack('B', 6)
        tab += pack('B', SET_DELTA_MAX_ROT)
        tab += pack('f', float(delta))
        self.command(bytes(tab))

    @Service.action
    def set_delta_max_trsl(self, delta):
        tab = pack('B', 6)
        tab += pack('B', SET_DELTA_MAX_TRSL)
        tab += pack('f', float(delta))
        self.command(bytes(tab))

    @Service.action
    def set_wheels_spacing(self, spacing):
        tab = pack('B', 6)
        tab += pack('B', SET_WHEELS_SPACING)
        tab += pack('f', float(spacing))
        self.command(bytes(tab))

    @Service.action
    def set_pwm(self, left, right):
        tab = pack('B', 10)
        tab += pack('B', SET_PWM)
        tab += pack('ff', float(left), float(right))
        self.command(bytes(tab))

    @Service.action
    def set_robot_size_x(self, size):
        tab = pack('B', 6)
        tab += pack('B', SET_ROBOT_SIZE_X)
        tab += pack('f', float(size))
        self.command(bytes(tab))

    @Service.action
    def set_robot_size_y(self, size):
        tab = pack('B', 6)
        tab += pack('B', SET_ROBOT_SIZE_Y)
        tab += pack('f', float(size))
        self.command(bytes(tab))

    @Service.action
    def stop_asap(self, trsldec, rotdec):
        tab = pack('B', 10)
        tab += pack('B', STOP_ASAP)
        tab += pack('ff', float(trsldec), float(rotdec))
        self.command(bytes(tab))

    #######
    # Get #
    #######

    @Service.action
    def get_pid_trsl(self):
        tab = pack('B', 2)
        tab += pack('B', GET_PID_TRSL)
        return self.get_command(bytes(tab))

    @Service.action
    def get_pid_rot(self):
        tab = pack('B', 2)
        tab += pack('B', GET_PID_ROT)
        return self.get_command(bytes(tab))

    @Service.action
    def get_position(self):
        self.log_serial("get_position")
        tab = pack('B', 2)
        tab += pack('B', GET_POSITION)
        return self.get_command(bytes(tab))

    @Service.action
    def get_speeds(self):
        tab = pack('B', 2)
        tab += pack('B', GET_SPEEDS)
        return self.get_command(bytes(tab))

    @Service.action
    def get_wheels(self):
        tab = pack('B', 2)
        tab += pack('B', GET_WHEELS)
        return self.get_command(bytes(tab))

    @Service.action
    def get_delta_max(self):
        tab = pack('B', 2)
        tab += pack('B', GET_DELTA_MAX)
        return self.get_command(bytes(tab))

    @Service.action
    def get_vector_trsl(self):
        tab = pack('B', 2)
        tab += pack('B', GET_VECTOR_TRSL)
        return self.get_command(bytes(tab))

    @Service.action
    def get_vector_rot(self):
        tab = pack('B', 2)
        tab += pack('B', GET_VECTOR_ROT)
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

    # Calibrate

    @Service.action
    @if_enabled
    def recalibration(self, sens):
        tab = pack('B', 3)
        tab += pack('B', RECALAGE)
        tab += pack('B', int(sens))
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
                if tab[1] == ACKNOWLEDGE:
                    self.log_serial("Robot acknowledged!")
                    self.ack_recieved.set()

                elif tab[1] == GET_PID_TRSL:
                    self.log_serial("Received the robot's translation pid!")

                    _, _, kp, ki, kd = unpack("=bbfff", bytes(tab))
                    self.log("P =", kp, "I =", ki, "D =", kd)

                    self.queue.put({'kp': kp, 'ki': ki, 'kd': kd})

                elif tab[1] == GET_PID_ROT:
                    self.log_serial("Received the robot's rotation pid!")

                    _, _, kp, ki, kd = unpack("=bbfff", bytes(tab))
                    self.log("P =", kp, "I =", ki, "D =", kd)

                    self.queue.put({'kp': kp, 'ki': ki, 'kd': kd})

                elif tab[1] == GET_POSITION:
                    self.log_serial("Received the robot's position!")

                    _, _, x, y, theta = unpack('=bbfff', bytes(tab))
                    self.log_serial("Position is x:", x, "y:", y, "th:", theta)

                    self.queue.put({
                        'x': x,
                        'y': y,
                        'theta': theta,
                    })

                elif tab[1] == MOVE_BEGIN:
                    self.log_serial("Robot started to move!")
                    self.has_stopped.clear()

                elif tab[1] == MOVE_END:
                    self.log_serial("Robot stopped moving!")
                    self.has_stopped.set()
                    self.publish(ROBOT + '_stopped')

                elif tab[1] == GET_SPEEDS:
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

                elif tab[1] == GET_WHEELS:
                    a, b, spacing, left_diameter, right_diameter = unpack('=bbfff', bytes(tab))

                    self.queue.put({
                        'spacing': spacing,
                        'left_diameter': left_diameter,
                        'right_diameter': right_diameter,
                    })

                    self.log_serial("Spacing: ", spacing, " Left: ", left_diameter, " Right: ", right_diameter)

                elif tab[1] == GET_DELTA_MAX:
                    a, b, translation, rotation = unpack('=bbff', bytes(tab))

                    self.queue.put({
                        'delta_rot_max': rotation,
                        'delta_trsl_max': translation,
                    })

                    self.log_serial("delta_rot_max : ", rotation, "delta_trsl_max", translation)

                elif tab[1] == GET_VECTOR_TRSL:
                    a, b, speed = unpack('=bbf', bytes(tab))

                    self.queue.put({
                        'trsl_vector': speed,
                    })

                    self.log_serial("Translation vector: ", speed)

                elif tab[1] == GET_VECTOR_ROT:
                    a, b, speed = unpack('=bbf', bytes(tab))

                    self.queue.put({
                        'rot_vector': speed,
                    })

                    self.log_serial("Rotation vector: ", speed)

                elif tab[1] == RECALAGE:
                    a, b, recal_xpos, recal_ypos, recal_theta = unpack('=bbfff', bytes(tab))

                    self.queue.put({
                        'recal_xpos': recal_xpos,
                        'recal_ypos': recal_ypos,
                        'recal_theta': recal_theta,
                    })

                elif tab[1] == DEBUG_MESSAGE:
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

                elif tab[1] == TELEMETRY_MESSAGE:
                    counter, commandid, xpos, ypos, theta, speed =unpack('=bbffff', bytes(tab))
                    telem = { 'x': xpos, 'y' : ypos, 'theta' : theta, 'speed' : speed}
                    try:
                        self.publish(ROBOT + '_telemetry', status='successful', telemetry = telem)
                    except:
                        self.publish(ROBOT + '_telemetry', status='failed', telemetry = telem)

                elif tab[1] == ERROR:
                    self.log("CM returned an error")
                    if tab[2] == COULD_NOT_READ:
                        self.log("Error was: COULD_NOT_READ")
                    elif tab[2] == DESTINATION_UNREACHABLE:
                        self.log("Error was: DESTINATION_UNREACHABLE")
                    elif tab[2] == BAD_ORDER:
                        self.log("Error was: BAD_ORDER")

                elif tab[1] == DEBUG:
                    message = bytes(tab)[2:]
                    print(message)

                else:
                    self.log("Message not recognised")

def wait_for_beacon():
    hostname = "pi"
    while True:
        r = os.system("ping -c 1 " + hostname)
        if r == 0:
            return
        pass

def main():
    wait_for_beacon()
    trajman = TrajMan()
    trajman.run()

if __name__ == '__main__':
    main()
