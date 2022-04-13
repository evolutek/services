#!/usr/bin/env python3

from enum import Enum
import os
from queue import Queue
import serial
from struct import pack, unpack, calcsize
from threading import Thread, Event, Lock
from time import sleep
import atexit

from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service, ConfigVariable
from cellaserv.settings import make_setting

make_setting('TRAJMAN_PORT', '/dev/serial0', 'trajman', 'port', 'TRAJMAN_PORT')
make_setting('TRAJMAN_BAUDRATE', 38400, 'trajman', 'baudrate',
             'TRAJMAN_BAUDRATE', int)
from cellaserv.settings import TRAJMAN_PORT, TRAJMAN_BAUDRATE

from evolutek.lib.map.point import Point
from evolutek.lib.sensors.rplidar import Rplidar
from evolutek.lib.settings import ROBOT
from evolutek.lib.status import RobotStatus
from evolutek.lib.utils.boolean import get_boolean
from evolutek.lib.utils.wrappers import if_enabled

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

    def __init__(self):
        super().__init__(ROBOT)

        atexit.register(self.lidar_stop)

        # Messages comming from the motor card
        self.queue = Queue()
        self.ack_recieved = Event()

        self.has_stopped = Event()
        self.has_detected_collision = Event()

        # Used to generate debug
        self.debug_file = None
        self.disabled = Event()
        self.bau_state = None

        self.lock = Lock()
        cs = CellaservProxy()

        lidar_config = cs.config.get_section('rplidar')
        self.lidar = Rplidar(lidar_config)
        self.lidar.start_scanning()
        self.lidar.register_callback(self.lidar_callback)

        self.detected_robots = []
        self.has_avoid = Event()
        self.avoid_side = None
        self.is_avoid_enabled = Event()
        self.destination = None
        self.robot_size = float(cs.config.get(section='match', option='robot_size'))

        self.robot_position = Point(0, 0)
        self.robot_orientation = 0.0
        self.robot_speed = 0.0

        self.serial = serial.Serial(TRAJMAN_PORT, TRAJMAN_BAUDRATE)

        self.thread = Thread(target=self.async_read)
        self.thread.start()

        # Set config of the robot
        self.init_sequence()
        self.set_telemetry(0)

        self.set_wheels_diameter(w1=self.w1(), w2=self.w2())
        self.set_wheels_spacing(spacing=self.spacing())

        self.set_pid_trsl(self.pidtp(), self.pidti(), self.pidtd())
        self.set_pid_rot(self.pidrp(), self.pidri(), self.pidrd())

        self.trsl_acc = self.trslacc()
        self.set_trsl_acc(self.trsl_acc)
        self.trsl_dec = self.trsldec()
        self.set_trsl_dec(self.trsl_dec)
        self.trsl_max_speed = self.trslmax()
        self.set_trsl_max_speed(self.trsl_max_speed)

        self.set_rot_acc(self.rotacc())
        self.set_rot_dec(self.rotdec())
        self.set_rot_max_speed(self.rotmax())

        self.set_delta_max_rot(self.deltarot())
        self.set_delta_max_trsl(self.deltatrsl())

        self.size_x = self.robot_size_x()
        self.set_robot_size_x(self.size_x)
        self.size_y = self.robot_size_y()
        self.set_robot_size_y(self.size_y)


        Thread(target=self.avoid_loop).start()

        try:
            self.handle_bau(cs.actuators[ROBOT].bau_read())
        except Exception as e:
            print('[TRAJMAN] Failed to get BAU status: %s' % str(e))

        self.set_telemetry(self.telemetry_refresh())

    """ AVOID """
    def lidar_callback(self, cloud, shapes, robots):
        with self.lock:
            self.detected_robots = robots

    def lidar_stop(self):
        self.lidar.__del__()

    @Service.action
    def get_robots(self):
        robots = []
        for robot in self.detected_robots:
            robots.append(robot.change_referencial(self.robot_position, self.robot_orientation).to_dict())
        return robots

    @Service.action
    def need_to_avoid(self, detection_dist, side):
        with self.lock:

            d1 = self.size_y + self.robot_size + 10
            d2 = detection_dist + self.robot_size

            # Compute the vertexes of the detection zone
            p1 = Point(self.size_x * (1 if side else -1), d1)
            p2 = Point(p1.x + d2 * (1 if side else -1), -p1.y)

            for robot in self.detected_robots:
                if min(p1.x, p2.x) < robot.x and robot.x < max(p1.x, p2.x) and\
                    min(p1.y, p2.y) < robot.y and robot.y < max(p1.y, p2.y):

                    global_pos = robot.change_referencial(self.robot_position, self.robot_orientation)

                    # Check if it is located on the map
                    if 0 < global_pos.x and global_pos.x < 2000 and 0 < global_pos.y and global_pos.y < 3000:
                        print('[ROBOT] Need to avoid robot at dist: %f' % Point(x=0, y=0).dist(robot))
                        return True

                    else:
                        print('[ROBOT] Ignoring obstacle: %s' % str(global_pos))

        return False

    @Service.action
    def stop_robot(self, dist=100):
        if self.is_moving():
            self.move_trsl(min(float(dist), 100), 0, 1000, self.robot_speed, int(self.robot_speed > 0))

    def avoid_loop(self):
        while True:

            sleep(0.01)

            if not self.is_avoid_enabled.is_set():
                continue

            stop_distance = 0.0
            detection_dist = 0.0
            side = False

            with self.lock:

                if self.robot_speed == 0.0:
                    continue

                stop_distance = (self.robot_speed**2 / (2 * 1000))
                detection_dist = min(stop_distance, self.robot_position.dist(self.destination)) + 50
                side = self.robot_speed > 0.0

            if self.need_to_avoid(detection_dist, side):

                with self.lock:
                    self.avoid_side = self.robot_speed > 0.0

                self.has_avoid.set()
                self.is_avoid_enabled.clear()
                self.stop_robot(stop_distance)


    """ BAU """
    # BAU handler
    @Service.event('%s-bau' % ROBOT)
    def handle_bau(self, value, **kwargs):

        new_state = get_boolean(value)
        # If the state didn't change, return
        if new_state == self.bau_state:
            return

        self.bau_state = new_state

        if new_state:
            self.enable()
        else:
            self.disable()

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
        return {'disabled': self.disabled.is_set(),
                'moving': self.is_moving()}

    ###########
    # Actions #
    ###########

    @Service.action
    @if_enabled
    def goto_xy(self, x, y, avoid=True):
        tab = pack('B', 2 + calcsize('ff'))
        tab += pack('B', Commands.GOTO_XY.value)
        tab += pack('ff', float(x), float(y))

        avoid = get_boolean(avoid)

        self.destination = Point(x=float(x), y=float(y))

        if avoid:
            self.is_avoid_enabled.set()

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
        print('[TRAJMAN] Free robot')
        tab = pack('B', 2)
        tab += pack('B', Commands.FREE.value)
        self.command(bytes(tab))

    @Service.action
    @if_enabled
    def unfree(self):
        self.move_trsl(0, 1, 1, 1, 1)

    @Service.action
    def disable(self):
        self.disabled.set()
        self.free()

    @Service.action
    def enable(self):
        if self.bau_state:
            self.disabled.clear()
            self.unfree()

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
        return {'x': self.robot_position.x, 'y': self.robot_position.y, 'theta': round(self.robot_orientation, 3)}
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
                    self.has_detected_collision.clear()
                    self.has_avoid.clear()

                elif tab[1] == Commands.MOVE_END.value:
                    self.log_serial("Robot stopped moving!")
                    self.has_stopped.set()
                    status = RobotStatus.Reached
                    if self.has_avoid.is_set():
                        status = RobotStatus.HasAvoid
                    elif self.has_detected_collision.is_set():
                        status = RobotStatus.NotReached

                    self.is_avoid_enabled.clear()

                    avoid_side = None
                    with self.lock:
                        self.destination = None
                        avoid_side = self.avoid_side
                        self.avoid_side = None

                    self.publish(ROBOT + '_stopped', **RobotStatus.return_status(status, avoid_side=avoid_side))

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

                    with self.lock:
                        self.robot_position = Point(x=xpos, y=ypos)
                        self.robot_orientation = theta
                        self.robot_speed = speed * 1000

                    #telemetry = { 'x': round(xpos), 'y' : round(ypos), 'theta' : round(theta, 4), 'speed' : round(speed, 2)}
                    #self.publish(ROBOT + '_telemetry', status='successful', telemetry=telemetry, robot=ROBOT)

                elif tab[1] == Commands.ERROR.value:
                    self.log("CM returned an error")
                    if tab[2] == Errors.COULD_NOT_READ.value:
                        self.log("Error was: COULD_NOT_READ")
                    elif tab[2] == Errors.DESTINATION_UNREACHABLE.value:
                        self.log("Error was: DESTINATION_UNREACHABLE")
                        self.has_detected_collision.set()
                    elif tab[2] == Errors.BAD_ORDER.value:
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
