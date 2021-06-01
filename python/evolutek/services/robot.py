#!/usr/bin/env python3

from cellaserv.proxy import CellaservProxy
from cellaserv.service import Event as CellaservEvent, Service

from evolutek.lib.map.point import Point
import evolutek.lib.robot.robot_actuators as ra
import evolutek.lib.robot.robot_trajman as rt
from evolutek.lib.sensors.rplidar import Rplidar
from evolutek.lib.settings import ROBOT
from evolutek.lib.status import RobotStatus
from evolutek.lib.utils.wrappers import event_waiter

from queue import Queue
from time import time, sleep
from threading import Event, Lock

@Service.require('config')
@Service.require('actuators', ROBOT)
@Service.require('trajman', ROBOT)
class Robot(Service):

    start_event = CellaservEvent('%s_started' % ROBOT)
    stop_event = CellaservEvent('%s_stopped' % ROBOT)

    goto_xy = Service.action(event_waiter(self.trajman.goto_xy))
    goto_theta = Service.action(event_waiter(self.trajman.goto_theta))
    move_trsl = Service.action(event_waiter(self.trajman.move_trsl))
    move_rot = Service.action(event_waiter(self.trajman.move_rot)))
    recal = Service.action(event_waiter(self.recalibration))

    # Imported from robot_trajman
    set_x = Service.action(rt.set_x)
    set_y = Service.action(rt.set_y)
    set_theta = Service.action(rt.set_theta)
    set_pos = Service.action(rt.set_pos)
    mirror_pos = rt.mirror_pos

    # Imported from robot_actuators
    mirror_pump_id = ra.mirror_pump_id
    flags_raise = Service.action(ra.flags_raise)
    flags_low = Service.action(ra.flags_low)
    left_arm_close = Service.action(ra.left_arm_close)
    left_arm_open = Service.action(ra.left_arm_open)
    left_arm_push = Service.action(ra.left_arm_push)
    right_arm_close = Service.action(ra.right_arm_close)
    right_arm_open = Service.action(ra.right_arm_open)
    right_arm_push = Service.action(ra.right_arm_push)
    left_cup_holder_close = Service.action(ra.left_cup_holder_close)
    left_cup_holder_open = Service.action(ra.left_cup_holder_open)
    left_cup_holder_drop = Service.action(ra.left_cup_holder_drop)
    right_cup_holder_close = Service.action(ra.right_cup_holder_close)
    right_cup_holder_open = Service.action(ra.right_cup_holder_open)
    right_cup_holder_drop = Service.action(ra.right_cup_holder_drop)

    def __init__(self):
        self.cs = CellaservProxy()
        self.lock = Lock()

        self.color1 = self.cs.config.get('match', 'color1')
        self.side = True

        try:
            self.color_callback(self.cs.match.get_color())
        except Exception as e:
            print('[ROBOT] Failed to set color: %s' % str(e))

        self.actuators = self.cs.actuators[ROBOT]
        self.trajman = self.cs.trajman[ROBOT]

        lidar_config = self.cs.config.get_section('rplidar')

        self.lidar = Rplidar(lidar_config)
        self.lidar.start_scanning()
        self.lidar.register_callback(self.lidar_callback)

        self.last_telemetry_received = 0

        self.queue = Queue()
        self.disabled = Event()

        super().__init__()

    @Service.event("match_color")
    def color_callback(color):
        with self.lock:
            self.side = color == self.color1

    @Service.event("%s_telemetry" % ROBOT)
    def callback_telemetry(self, telemetry, **kwargs):
        tmp = time()
        print("[ROBOT] Time since last telemetry: " + str((tmp - self.last_telemetry_received) * 1000) + "s")
        self.last_telemetry_received = tmp
        self.lidar.set_position(Point(dict=telemetry), float(telemetry['theta']))

    # Usefull
    def lidar_callback(self, cloud, shapes, robots):
        print('[ROBOT] Robots seen at: ')
        for robot in robots:
            print('-> ' + str(robot))

    @Service.action
    def enable(self):
        self.disabled.clear()
        Thread(target=self.run_queue).start()

    @Service.action
    def disable(self):
        # Empty queue
        while not self.queue.empty():
            self.queue.get()


        self.disabled.set()

    def run_queue(self):
        while not self.disabled.is_set():
            task, args = self.queue.get()
            self.publish('%s_robot_started' % ROBOT)
            try:
                status = task(*args)
            except Exception as e:
                print('[ROBOT Failed to execute task: %s' % str(e))

            try:
                status = RobotStatus(status)
            except:
                status RobotStatus.Unknow
            self.publish('%s_robot_stopped' % ROBOT, status=status.value)

if __name__ == '__main__':
    robot = Robot()
    robot.run()
