#!/usr/bin/env python3

from cellaserv.proxy import CellaservProxy
from cellaserv.service import Event as CellaservEvent, Service

from evolutek.lib.map.map import parse_obstacle_file, ObstacleType, Map
from evolutek.lib.map.point import Point
import evolutek.lib.robot.robot_actions as robot_actions
import evolutek.lib.robot.robot_actuators as robot_actuators
import evolutek.lib.robot.robot_trajman as robot_trajman
from evolutek.lib.settings import ROBOT
from evolutek.lib.status import RobotStatus
from evolutek.lib.utils.action_queue import ActQueue
from evolutek.lib.utils.boolean import get_boolean
from evolutek.lib.utils.wrappers import event_waiter
from evolutek.utils.interfaces.debug_map import Interface

from time import time, sleep
from threading import Event, Lock, Thread

DEBUG = False

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
    goto_avoid = Service.action(robot_trajman.goto_avoid)
    goto_with_path = Service.action(robot_trajman.goto_with_path)
    move_back = Service.action(robot_trajman.move_back)
    recalibration = Service.action(robot_trajman.recalibration)
    recalibration_sensors = robot_trajman.recalibration_sensors
    homemade_recal = Service.action(robot_trajman.homemade_recal)

    # Imported from robot_actuators
    mirror_pump_id = robot_actuators.mirror_pump_id
    pumps_get = Service.action(robot_actuators.pumps_get)
    pumps_drop = Service.action(robot_actuators.pumps_drop)
    flags_raise = Service.action(robot_actuators.flags_raise)
    flags_low = Service.action(robot_actuators.flags_low)
    front_arm_close = Service.action(robot_actuators.front_arm_close)
    front_arm_open = Service.action(robot_actuators.front_arm_open)
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

    # Imported from robot_actions
    get_reef = Service.action(robot_actions.get_reef)
    start_lighthouse = Service.action(robot_actions.start_lighthouse)
    push_windsocks = Service.action(robot_actions.push_windsocks)
    drop_start = Service.action(robot_actions.drop_start)
    drop_center = Service.action(robot_actions.drop_center)
    goto_anchorage = Service.action(robot_actions.goto_anchorage)

    def __init__(self):

        super().__init__(ROBOT)

        self.cs = CellaservProxy()
        self.lock = Lock()

        self.bau_state = None
        self.color1 = self.cs.config.get('match', 'color1')
        self.side = True

        # Size of the robot and min dist from wall
        self.size_x = float(self.cs.config.get(section=ROBOT, option='robot_size_x'))
        self.size_y = float(self.cs.config.get(section=ROBOT, option='robot_size_y'))
        self.size = float(self.cs.config.get(section=ROBOT, option='robot_size'))

        # TODO: rename
        self.dist = ((self.size_x ** 2 + self.size_y ** 2) ** (1 / 2.0))

        self.actuators = self.cs.actuators[ROBOT]
        self.trajman = self.cs.trajman[ROBOT]

        self.goto_xy = event_waiter(self.trajman.goto_xy, self.start_event, self.stop_event, callback=self.check_abort)
        self.goto_theta = event_waiter(self.trajman.goto_theta, self.start_event, self.stop_event, callback=self.check_abort)
        self.move_trsl = event_waiter(self.trajman.move_trsl, self.start_event, self.stop_event, callback=self.check_abort)
        self.move_rot = event_waiter(self.trajman.move_rot, self.start_event, self.stop_event, callback=self.check_abort)
        self.recal = event_waiter(self.trajman.recalibration, self.start_event, self.stop_event, callback=self.check_abort)

        self.robot_size = float(self.cs.config.get(section='match', option='robot_size'))

        self.disabled = Event()
        self.need_to_abort = Event()

        width = int(self.cs.config.get(section='map', option='width'))
        height = int(self.cs.config.get(section='map', option='height'))
        fixed_obstacles, self.color_obstacles = parse_obstacle_file('/etc/conf.d/obstacles.json')
        self.map = Map(width, height, self.size)
        self.map.add_obstacles(fixed_obstacles)
        self.path = []
        self.robots = []
        self.robots_tags = []

        def start_callback(id):
            self.need_to_abort.clear()
            self.publish('%s_robot_started' % ROBOT, id=id)

        def end_callback(id, status):
            self.publish('%s_robot_stopped' % ROBOT, id=id, **status)

        self.queue = ActQueue(
            start_callback,
            end_callback
        )
        self.queue.run_queue()

        try:
            cs = CellaservProxy()
            self.handle_bau(cs.actuators[ROBOT].bau_read())
        except Exception as e:
            print('[TRAJMAN] Failed to get BAU status: %s' % str(e))

        try:
            self.color_callback(self.cs.match.get_color())
        except Exception as e:
            print('[ROBOT] Failed to set color: %s' % str(e))

        if DEBUG:
            Thread(target=Interface, args=[self]).start()

    @Service.event("match_color")
    def color_callback(self, color):
        with self.lock:
            self.side = color == self.color1

            for obstacle in self.color_obstacles:
                if 'tag' in obstacle:
                    self.map.remove_obstacle(obstacle['tag'])
            self.map.add_obstacles(self.color_obstacles, not self.side, type=ObstacleType.color)

    def get_path(self, destination):

        robots = self.trajman.get_robots()
        detected_robots = [ Point(dict=robot) for robot in robots ]
        origin = Point(dict=self.trajman.get_position())

        # TODO : useful ?
        with self.lock:
            # Remove robots
            for tag in self.robots_tags:
                self.map.remove_obstacle(tag)
            self.robots_tags.clear()

            # Add robots on the map
            for i in range(len(detected_robots)):
                self.robots_tags.append('robot-%d' % i)
                self.map.add_octogon_obstacle(detected_robots[i], self.robot_size + 10, tag=self.robots_tags[-1], type=ObstacleType.robot)

            # Compute path
            path = self.map.get_path(origin, destination)

            # Remove robots
            #for tag in robots_tags:
            #    self.map.remove_obstacle(tag)

            self.path = path
            self.robots = robots
            return path

    def clean_map(self):

         with self.lock:
            # Remove robots
            for tag in self.robots_tags:
                self.map.remove_obstacle(tag)
            self.robots_tags.clear()
            self.path.clear()


    @Service.event('raise_flags')
    def raise_flags(self):
        self.enable()
        self.actuators.enable()
        sleep(0.5)
        self.flags_raise(use_queue=False)

    @Service.action
    def enable(self):
        if self.bau_state:
            self.disabled.clear()
            self.queue.run_queue()

    @Service.action
    def disable(self):
        self.disabled.set()
        self.queue.stop_queue()
        self.need_to_abort.set()

    @Service.action
    def reset(self):
        if not self.bau_state:
            return

        self.enable()
        sleep(2)

        self.front_arm_close(use_queue=False)
        self.left_arm_open(use_queue=False)
        self.right_arm_open(use_queue=False)
        self.left_cup_holder_open(use_queue=False)
        self.right_cup_holder_open(use_queue=False)
        self.flags_raise(use_queue=False)
        sleep(1.5)

        self.front_arm_open(use_queue=False)
        self.left_arm_close(use_queue=False)
        self.right_arm_close(use_queue=False)
        self.left_cup_holder_close(use_queue=False)
        self.right_cup_holder_close(use_queue=False)
        self.flags_low(use_queue=False)
        sleep(1.5)

    @Service.event('%s-bau' % ROBOT)
    def handle_bau(self, value, **kwargs):

        new_state = get_boolean(value)
        # If the state didn't change, return
        if new_state == self.bau_state:
            return

        self.bau_state = new_state

        if new_state:
            self.reset()
        else:
            self.disable()

    @Service.action
    def abort_action(self):
        self.need_to_abort.set()
        self.queue.clear_queue()

    def check_abort(self):
        if self.need_to_abort.is_set():
            # TODO : compute dist
            self.trajman.stop_robot()
            self.need_to_abort.clear()
            return RobotStatus.Aborted
        return RobotStatus.Ok

def main():
    robot = Robot()
    robot.run()

if __name__ == '__main__':
    main()
