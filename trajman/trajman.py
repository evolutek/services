#!/usr/bin/python3

import serial
import time
from threading import Thread, Event
from queue import Queue
from struct import *

from cellaserv.service import Service
from cellaserv.proxy import CellaservProxy

#######################
# All the commands ID #
#######################

DEBUG_MESSAGE           = 127
ACKNOWLEDGE             = 200
MOVE_BEGIN              = 128
MOVE_END                = 129

GET_PID_TRSL            = 10
GET_PID_ROT             = 11
GET_POSITION            = 12
GET_SPEEDS              = 13
GET_WHEELS              = 14
GOTO_XY                 = 100
GOTO_THETA              = 101
MOVE_TRSL               = 102
MOVE_ROT                = 103
CURVE                   = 104
FREE                    = 109
RECALAGE                = 110
SET_PID_TRSL            = 150
SET_PID_ROT             = 151
SET_TRSL_ACC            = 152
SET_TRSL_DEC            = 153
SET_TRSL_MAXSPEED       = 154
SET_ROT_ACC             = 155
SET_ROT_DEC             = 156
SET_ROT_MAXSPEED        = 157
SET_X                   = 158
SET_Y                   = 159
SET_THETA               = 160
SET_DIAM_WHEELS         = 161
SET_WHEELS_SPACING      = 162
SET_DEBUG               = 200
ERROR                   = 255

#################
# The errors ID #
#################

COULD_NOT_READ          = 1
DESTINATION_UNREACHABLE = 2
BAD_ORDER               = 3

class TrajMan(Service):
    """
    The trajman service is the interface between cellaserv and the motors of
    the robot.

    It uses two threads: one for the service and one to read on the serial
    asynchronously.

    It can be disabled in order to stop processing commands and make sure that
    the robot will not move.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cs = CellaservProxy()

        self.queue = Queue()
        self.ack_recieved = Event()
        self.has_stopped = Event()

        # Used to generate debug
        self.debug_file = None
        self.disabled = False

        self.serial = serial.Serial('/dev/ttySAC0', 115200)

    def setup(self):
        """Setup the service."""
        super().setup()

        self.thread = Thread(target=self.async_read)
        self.thread.start()

        self.log_debug("Init starting")
        self.init_sequence()
        self.log_debug("Init ended correctly")

        self.set_wheels_diameter(w1=53.8364, w2=53.8364)
        self.set_wheels_spacing(spacing=302.67)

    def log_debug(self, *args, **kwargs):
        """Send log to cellaserv"""
        self.log(msg=args, **kwargs)

    def write(self, data):
        """Write data to serial and flush."""
        self.serial.write(data)
        self.serial.flush()

    def command(self, data):
        """
        Handle commands sent to the card and wait for ack.

        If trajman is disabled (ie. does not process commands anymore) then
        this function does not send the command.
        """
        if self.disabled:
            return

        self.ack_recieved.clear()
        self.write(data)
        self.ack_recieved.wait()

    def get_command(self, data):
        """
        Handle commands that waits for an answer from the motors.

        If trajman is disabled (ie. does not process commands anymore) then
        this function does not send the command and returns None.
        """

        if self.disabled:
            return None

        self.write(data)
        return self.queue.get(timeout=1)

    ###########
    # Actions #
    ###########

    @Service.action
    def goto_xy(self, x, y):
        self.log_debug("GOING TO", x, y)

        tab = (pack('B', 2 + calcsize('ff')))
        tab += (pack('B', GOTO_XY))
        tab += (pack('ff', float(x), float(y)))
        self.command(bytes(tab))

    @Service.action
    def goto_theta(self, theta):
        self.log_debug("GOING TO THETA", theta)

        tab = pack('B', 6)
        tab += pack('B', GOTO_THETA)
        tab += pack('f', float(theta))
        self.command(bytes(tab))

    @Service.action
    def move_trsl(self, dest, acc, dec, maxspeed, sens):
        tab = pack('B', 19)
        tab += pack('B', MOVE_TRSL)
        tab += pack('ffffb', float(dest), float(acc), float(dec),
                float(maxspeed), int(sens))
        self.command(bytes(tab))

    @Service.action
    def move_rot(self, dest, acc, dec, maxspeed, sens):
        tab = pack('B', 19)
        tab += pack('B', MOVE_ROT)
        tab += pack('ffffb', float(dest), float(acc), float(dec),
                float(maxspeed), int(sens))
        self.command(bytes(tab))

    @Service.action
    def curve(self, dt, at, det, mt, st, dr, ar, der, mr, sr, delayed):
        tab = pack('B', 35)
        tab += pack('B', CURVE)
        tab += pack('ffffffff', float(dt), float(at), float(det), float(mt),
                float(dr), float(ar), float(der), float(mt))

        s = 0
        s += 1 if int(st) == 1 else 0
        s += 2 if int(sr) == 1 else 0
        s += 4 if int(delayed) == 1 else 0

        self.log_debug(s)
        tab += pack('B', s)
        self.write(bytes(tab))

    @Service.action
    def free(self):
        tab = pack('B', 2)
        tab += pack('B', FREE)
        self.command(bytes(tab))

    @Service.action
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
    def set_debug(self, state):

        tab = pack('B', 3)
        tab += pack('B', SET_DEBUG)
        if state:
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
        tab += pack('B', SET_DIAM_WHEELS)
        tab += pack('ff', float(w1), float(w2))
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
        self.log_debug("get_position")
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
    def flush_serial(self):
        self.log_debug("Clearing CM buffer")
        self.write(bytes(1024))

    @Service.action
    def init_sequence(self):
        self.log_debug("Sending init sequence")
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
        self.log_debug("Clearing queue")
        ret = []
        while not self.queue.empty():
            ret.append(self.queue.get())
        return ret

    @Service.action
    def is_moving(self):
        return not self.has_stopped.is_set()

    # Calibrate

    @Service.action
    def recalibration(self, sens):
        tab = pack('B', 3);
        tab += pack('B', RECALAGE)
        tab += pack('B', int(sens))
        return self.get_command(bytes(tab))

    # Thread 2

    def async_read(self):
        """Read events from serial and add them to the queue."""
        while True:
            length = unpack('b', self.serial.read())[0]
            tab = [length]
            self.log_debug("Message length expected:", length)
            for i in range(length - 1): # Fixme: use read(lenght)?
                tab += self.serial.read()
            self.log_debug("Received message with length:", len(tab))

            if len(tab) > 1:
                if tab[1] == ACKNOWLEDGE:
                    self.log_debug("Robot acknowledged!")
                    self.ack_recieved.set()

                elif tab[1] == GET_PID_TRSL:
                    self.log_debug("Received the robot's translation pid!")

                    _, _, kp, ki, kd = unpack("=bbfff", bytes(tab))
                    self.log_debug("P =", kp, "I =", ki, "D =", kd)

                    self.queue.put({'kp': kp, 'ki': ki, 'kd': kd})

                elif tab[1] == GET_PID_ROT:
                    self.log_debug("Received the robot's rotation pid!")

                    _, _, kp, ki, kd = unpack("=bbfff", bytes(tab))
                    self.log_debug("P =", kp, "I =", ki, "D =", kd)

                    self.queue.put({'kp': kp, 'ki': ki, 'kd': kd})

                elif tab[1] == GET_POSITION:
                    self.log_debug("Received the robot's position!")

                    _, _, x, y, theta = unpack('=bbfff', bytes(tab))
                    self.log_debug("Position is x:", x, "y:", y, "th:", theta)

                    self.queue.put({
                        'x': x,
                        'y': y,
                        'theta': theta,
                    })

                elif tab[1] == MOVE_BEGIN:
                    self.log_debug("Robot started to move!")
                    self.has_stopped.clear()

                elif tab[1] == MOVE_END:
                    self.log_debug("Robot stopped moving!")
                    self.has_stopped.set()
                    self.cs('robot_stopped')

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

                    self.log_debug("Translation:    Acc:", tracc, "\tDec:", trdec, "\tMax :", trmax,
                    " (mm/(s*s) mm/(s*s) mm/s)")
                    self.log_debug("Rotation:       Acc: {0:.3f}\tDec: {1:.3f}\tMax:"
                            " {2:.3f} (rad/(s*s) rad/(s*s) rad/s)".format(rtacc, rtdec, rtmax))

                elif tab[1] == GET_WHEELS:
                    a, b, spacing, left_diameter, right_diameter = unpack('=bbfff', bytes(tab))

                    self.queue.put({
                        'spacing': spacing,
                        'left_diameter': left_diameter,
                        'right_diameter': right_diameter,
                        })

                    if PRINT_DEBUG:
                        self.log_debug("Spacing: ", spacing, " Left: ", left_diameter, " Right: ", right_diameter)

                elif tab[1] == RECALAGE:
                    a, b, recal_xpos, recal_ypos, recal_theta = unpack('=bbfff', bytes(tab))

                    self.queue.put({
                        'recal_xpos': recal_xpos,
                        'recal_ypos': recal_ypos,
                        'recal_theta': recal_theta,
                        })

                elif tab[1] == DEBUG_MESSAGE:
                    counter, commandid, time, xpos, wpx, ypos, wpy, theta, wpth, trspeed, rotspeed, trp, tri, trd, rtp, rti, rtd = unpack("=bbfffffffffffffff", bytes(tab))
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
                else:
                    self.log_debug("Message not recognised")

def main():
    trajman = TrajMan()
    trajman.run()

if __name__ == '__main__':
    main()
