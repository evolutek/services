#!/usr/bin/env python3

from cellaserv.proxy import CellaservProxy
from cellaserv.service import Event as CellaservEvent, Service

from evolutek.lib.map.point import Point
import evolutek.lib.robot.robot_actions as robot_actions
import evolutek.lib.robot.robot_actuators as robot_actuators
import evolutek.lib.robot.robot_trajman as robot_trajman
from evolutek.lib.sensors.rplidar import Rplidar
from evolutek.lib.settings import ROBOT
from evolutek.lib.status import RobotStatus
from evolutek.lib.utils.wrappers import event_waiter

from time import time, sleep
from threading import Event, Lock

# TODO : Queue
# TODO : Permit to use action without queue
# TODO : Manage avoid
# TODO : Pathfinding
# TODO : Reset robot (after aborting ? after BAU ?)

@Service.require('config')
@Service.require('actuators', ROBOT)
@Service.require('trajman', ROBOT)
class Robot(Service):

    start_event = CellaservEvent('%s_started' % ROBOT)
    stop_event = CellaservEvent('%s_stopped' % ROBOT)

    # Imported from robot_trajman
    mirror_pos = robot_trajman.mirror_pos
    set_x = Service.action(robot_trajman.set_x)
    set_y = Service.action(robot_trajman.set_y)
    set_theta = Service.action(robot_trajman.set_theta)
    set_pos = Service.action(robot_trajman.set_pos)
    goto = Service.action(robot_trajman.goto)
    goth = Service.action(robot_trajman.goth)
    move_back = Service.action(robot_trajman.move_back)
    recalibration = Service.action(robot_trajman.recalibration)

    # Imported from robot_actuators
    mirror_pump_id = robot_actuators.mirror_pump_id
    flags_raise = Service.action(robot_actuators.flags_raise)
    flags_low = Service.action(robot_actuators.flags_low)
    left_arm_close = Service.action(robot_actuators.left_arm_close)
    left_arm_open = Service.action(robot_actuators.left_arm_open)
    left_arm_push = Service.action(robot_actuators.left_arm_push)
    right_arm_close = Service.action(robot_actuators.right_arm_close)
    right_arm_open = Service.action(robot_actuators.right_arm_open)
    right_arm_push = Service.action(robot_actuators.right_arm_push)
    left_cup_holder_close = Service.action(robot_actuators.left_cup_holder_close)
    left_cup_holder_open = Service.action(robot_actuators.left_cup_holder_open)
    left_cup_holder_drop = Service.action(robot_actuators.left_cup_holder_drop)
    right_cup_holder_close = Service.action(robot_actuators.right_cup_holder_close)
    right_cup_holder_open = Service.action(robot_actuators.right_cup_holder_open)
    right_cup_holder_drop = Service.action(robot_actuators.right_cup_holder_drop)

    # Imported from robot_actuators
    get_reef = Service.action(robot_actions.get_reef)

    def __init__(self):

        super().__init__(ROBOT)

        self.cs = CellaservProxy()
        self.lock = Lock()

        self.color1 = self.cs.config.get('match', 'color1')
        self.side = True

        try:
            self.color_callback(self.cs.match.get_color())
        except Exception as e:
            print('[ROBOT] Failed to set color: %s' % str(e))

        # Size of the robot and min dist from wall
        self.size_x = float(self.cs.config.get(section=ROBOT, option='robot_size_x'))
        self.size_y = float(self.cs.config.get(section=ROBOT, option='robot_size_y'))
        self.stop_trsl_dec = float(self.cs.config.get(section=ROBOT, option='stop_trsl_dec'))
        self.stop_rot_dec = float(self.cs.config.get(section=ROBOT, option='stop_trsl_rot'))

        # TODO: rename
        self.dist = ((self.size_x ** 2 + self.size_y ** 2) ** (1 / 2.0))

        self.actuators = self.cs.actuators[ROBOT]
        self.trajman = self.cs.trajman[ROBOT]

        self.goto_xy = event_waiter(self.trajman.goto_xy, self.start_event, self.stop_event, callback=lambda:self.check_abort() or self.check_avoid(), has_abort=self.has_abort, has_avoid=self.has_avoid)
        self.goto_theta = event_waiter(self.trajman.goto_theta, self.start_event, self.stop_event, callback=self.check_abort, has_abort=self.has_abort)
        self.move_trsl = event_waiter(self.trajman.move_trsl, self.start_event, self.stop_event, callback=self.check_abort, has_abort=self.has_abort)
        self.move_rot = event_waiter(self.trajman.move_rot, self.start_event, self.stop_event, callback=self.check_abort, has_abort=self.has_abort)
        self.recal = event_waiter(self.recalibration, self.start_event, self.stop_event, callback=self.check_abort, has_abort=self.has_abort)

        lidar_config = self.cs.config.get_section('rplidar')

        self.lidar = Rplidar(lidar_config)
        self.lidar.start_scanning()
        self.lidar.register_callback(self.lidar_callback)

        self.last_telemetry_received = 0

        # TODO : import queue
        self.disabled = Event()
        self.need_to_abort = Event()
        self.has_abort = Event()
        self.has_avoid = Event()

        super().__init__()

    @Service.event("match_color")
    def color_callback(self, color):
        with self.lock:
            self.side = color == self.color1

    @Service.event("%s_telemetry" % ROBOT)
    def callback_telemetry(self, telemetry, **kwargs):
        tmp = time()
        print("[ROBOT] Time since last telemetry: " + str((tmp - self.last_telemetry_received) * 1000) + "s")
        self.last_telemetry_received = tmp
        self.lidar.set_position(Point(dict=telemetry), float(telemetry['theta']))

    # TODO : Usefull ?
    def lidar_callback(self, cloud, shapes, robots):
        print('[ROBOT] Robots seen at: ')
        for robot in robots:
            print('-> ' + str(robot))

    @Service.action
    def enable(self):
        self.disabled.clear()
        # TODO : start queue

    @Service.event('match_end')
    @Service.action
    def disable(self):
        self.disabled.set()
        self.abort_action()

    @Service.action
    def abort_action(self):
        self.need_to_abort.set()
        # TODO

    @Service.action
    def stop_robot(self):
        self.trajman.stop_asap(self.stop_trsl_dec, self.stop_rot_dec)

    def check_abort(self):
        if self.need_to_abort.is_set():
            self.has_abort.set()
            self.stop_robot()
            self.need_to_abort.clear()
            return True
        return False

    def check_avoid(self):
        # TODO :
        # Check if we need to avoid
        # Set event
        # Stop robot
        # Return True
        return False

if __name__ == '__main__':
    robot = Robot()
    robot.run()
