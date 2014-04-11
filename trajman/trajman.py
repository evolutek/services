#!/usr/bin/python3

import serial
import time
from threading import Thread, Event
from queue import Queue
from struct import *

from cellaserv.service import Service
from cellaserv.proxy import CellaservProxy

PRINT_DEBUG = False

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
    """The trajman service is the interface between cellaserv and the motors of
    the robot.

    It uses two threads: one for the service and one to read the serial
    asynchronously.

    It can be switched to a "soft free" mode in order to stop processing
    commands. This mode is used to completely stop the robot until the soft
    free state is reset.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cs = CellaservProxy()

        self.queue = Queue()
        self.ack_recieved = Event()
        self.has_stopped = Event()

        # Used to generate debug
        self.debug_file = None

        self.serial = serial.Serial('/dev/ttySAC0', 115200)

        self.thread = Thread(target=self.async_read)
        self.thread.start()

        self.soft_free_state = False

        #self.flush_serial()
        self.init_sequence()
        #self.set_wheels_diameter(w1=53.234, w2=54.248)
        self.set_wheels_diameter(w1=53, w2=53)
        self.set_wheels_spacing(spacing=302.447)

    def log_debug(self, *args, **kwargs):
        if PRINT_DEBUG:
            print(*args, **kwargs)

    def write(self, data):
        """Write data to serial and flush."""
        self.serial.write(data)
        self.serial.flush()

    def command(self, data):
        """Handle commands sent to the card and wait for ack.

        If trajman is in soft_tree (ie. does not process commands anymore) then
        this function does not send the command."""
        if self.soft_free_state:
            return

        self.ack_recieved.clear()
        self.write(data)
        self.ack_recieved.wait()

    def get_command(self, data):
        """Handle commands that waits for an answer from the motors.

        If trajman is in soft_tree (ie. does not process commands anymore) then
        this function does not send the command and returns None."""

        if self.soft_free_state:
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
    def soft_free(self):
        self.soft_free_state = True

    @Service.action
    def soft_asserv(self):
        self.soft_free_state = False

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
        self.debug_file = open("debug.data", "w")

        tab = pack('B', 3)
        tab += pack('B', SET_DEBUG)
        if state:
            tab += pack('B', 1)
            self.fdebug = open("debug.data", "w")

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
        """Read events from serial and add them to queue."""
        while True:
            length = unpack('b', self.serial.read())[0]
            tab = [length]
            self.log_debug("Message length expected:", length)
            for i in range(length - 1): # Fixme: use read(lenght)?
                tab += self.serial.read()
            self.log_debug("Received message with length:", len(tab))

            # Fixme: Use function lookup table?
            if len(tab) > 1:
                if tab[1] == ACKNOWLEDGE:
                    self.log_debug("Robot acknowledged!")
                    self.ack_recieved.set()

                elif tab[1] == GET_PID_TRSL:
                    self.log_debug("Received the robot's translation pid!")

                    # TODO: use [2:]
                    a, b, kp, ki, kd = unpack("=bbfff", bytes(tab))
                    self.log_debug("P =", kp, "I =", ki, "D =", kd)

                    self.queue.put({'kp': kp, 'ki': ki, 'kd': kd})

                elif tab[1] == GET_PID_ROT:
                    self.log_debug("Received the robot's rotation pid!")

                    # TODO: use [2:]
                    a, b, kp, ki, kd = unpack("=bbfff", bytes(tab))
                    self.log_debug("P =", kp, "I =", ki, "D =", kd)

                    self.queue.put({'kp': kp, 'ki': ki, 'kd': kd})

                elif tab[1] == GET_POSITION:
                    self.log_debug("Received the robot's position!")

                    # TODO: use [2:]
                    a, b, x, y, theta = unpack('=bbfff', bytes(tab))
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
                    self.cs('robot-stopped')

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
                    if not fdebug.closed:
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

    # OLD self tests

    def test_trsl(self):
        self.GotoXY(10100, 10000)
        self.WaitForStop()
        time.sleep(0.1)
        self.GotoXY(10000, 10000)
        self.WaitForStop()
        time.sleep(0.1)

    def test_rot(self):
        self.GotoTheta(1.6)
        self.WaitForStop()
        time.sleep(0.1)
        self.GotoTheta(3)
        self.WaitForStop()
        time.sleep(0.1)
        self.GotoTheta(0)
        self.WaitForStop()
        time.sleep(0.1)

    def test_queued(self):
        tab = pack('B', 19)
        tab += pack('B', MOVE_TRSL)
        tab += pack('ffffb', float(100), float(100), float(100), float(100),
                int(3))
        self.command(bytes(tab))
        tab = pack('B', 19)
        tab += pack('B', MOVE_TRSL)
        tab += pack('ffffb', float(100), float(100), float(100), float(100),
                int(2))
        self.command(bytes(tab))

    def compute_wheels_size(arg):
        """ TODO: Move this to robot.py """
        return False

        self.free()
        self.log_debug("###############################################################")
        self.log_debug("## Hi ! and welcome to the wheels size computing assistant ! ##")
        self.log_debug("###############################################################")
        self.log_debug("Please place the robot on a special mark, facing the right direction. Press enter when ready")
        input()
        self.set_x(1000)
        self.set_y(1000)
        self.set_theta(0)
        time.sleep(.1)
        old = self.get_wheels()
        time.sleep(.1)
        speeds = self.get_speeds()
        time.sleep(.1)
        if arg == "all" or arg == "diam":
            self.log_debug("########################################################")
            self.log_debug("Please enter the length of the distance to mesure (mm) :")
            self.log_debug("########################################################")
            length = float(sys.stdin.readline())
            self.log_debug("Length = ", length)
            self.log_debug("Getting the old settings...")
            self.set_trsl_max_speed(100)
            time.sleep(.1)
            self.log_debug("################################################################")
            self.log_debug("Do you want the robot to go to the second mark by itself (y/n) ?")
            self.log_debug("################################################################")
            if input()[0] == 'y':
                self.log_debug("Going...")
                self.goto_xy_block(1000 + length, 1000)
            time.sleep(.1)
            self.free()
            self.log_debug("#################################################################")
            self.log_debug("Please place the robot on the second mark, press Enter when ready")
            self.log_debug("#################################################################")
            sys.stdin.readline()
            newpos = self.get_position()
            #mesured = ((newpos[0] - 1000) ** 2 + (newpos[1] - 1000) ** 2))
            mesured = (newpos[0] - 1000)
            coef = float(length) / float(mesured)
            coef1 = float(length) / float(mesured - math.sin(newpos[2]) * old[0])
            coef2 = float(length) / float(mesured + math.sin(newpos[2]) * old[0])
            self.log_debug("The error was of :", length - (newpos[0] - 1000))
            self.log_debug("The new diameters are :", old[1] * coef, old[2] * coef)
            self.log_debug("Setting the new diameters")
            self.set_wheels_diameter(old['left'] * coef, old['right'] * coef)
            time.sleep(.1)
            self.log_debug("########################")
            self.log_debug("Going back to the origin")
            self.log_debug("########################")
            self.set_x(1000 + length)
            self.goto_xy_block(1000, 1000)
            self.free()
        if arg == "all" or arg == "spacing":
            self.log_debug("##########################################")
            self.log_debug("Please enter the number of turns to mesure")
            self.log_debug("##########################################")
            nbturns = float(sys.stdin.readline())
            self.log_debug("nbturns = ", nbturns)
            nbturns = nbturns * 2
            self.log_debug("#######################################################")
            self.log_debug("Do you want the robot to do the turns by itself (y/n) ?")
            self.log_debug("#######################################################")
            if sys.stdin.readline()[0] == 'y':
                self.log_debug("Going...")
                self.rotate(nbturns * math.pi, 3, 3, 3, 1)
                self.has_stopped.wait()
                time.sleep(.1)
                self.free()
                self.log_debug("############################################################")
                self.log_debug("Please replace the robot on the mark, press Enter when ready")
                self.log_debug("############################################################")
            else:
                self.log_debug("################################################################")
                self.log_debug("Please make the robot do turns on itself, press Enter when ready")
                self.log_debug("################################################################")
            sys.stdin.readline()
            newpos = self.get_position()
            mesured = newpos['theta'] + nbturns * math.pi
            coef = float(mesured) / float(nbturns * math.pi)
            self.log_debug("The error was of :", newpos['theta'])
            self.log_debug("The new spacing is :", old['spacing'] * coef)
            self.log_debug("Setting the new spacing")
            self.set_wheels_spacing(old['spacing'] * coef)
            self.set_theta(0)
            self.rotate(nbturns * math.pi, 3, 3, 3, 0)
            self.has_stopped.wait()
        self.set_trsl_max_speed(speeds['trmax'])
        self.log_debug("#############################################")
        self.log_debug("## GO TO THE MOTOR CARD AND SET THE VALUES ##")
        self.log_debug("#############################################")
        self.log_debug(self.get_wheels())

def main():
    trajman = TrajMan()
    trajman.run()

if __name__ == '__main__':
    main()
