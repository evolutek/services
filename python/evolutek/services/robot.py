#!/usr/bin/env python3

from cellaserv.proxy import CellaservProxy
from cellaserv.service import Event as CellaservEvent, Service

from evolutek.lib.map.map import parse_obstacle_file, ObstacleType, Map
from evolutek.lib.map.point import Point
import evolutek.lib.robot.robot_actions as robot_actions
import evolutek.lib.robot.robot_actuators as robot_actuators
import evolutek.lib.robot.robot_trajman as robot_trajman
from evolutek.lib.sensors.rplidar import Rplidar
from evolutek.lib.settings import ROBOT
from evolutek.lib.status import RobotStatus
from evolutek.lib.utils.action_queue import ActQueue
from evolutek.lib.utils.wrappers import event_waiter

from time import time, sleep
from threading import Event, Lock

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
    goto_avoid = Service.action(robot_trajman.goto_avoid)
    goto_with_path = Service.action(robot_trajman.goto_with_path)
    move_back = Service.action(robot_trajman.move_back)
    recalibration = Service.action(robot_trajman.recalibration)

    # Imported from robot_actuators
    mirror_pump_id = robot_actuators.mirror_pump_id
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
        self.size = float(self.cs.config.get(section=ROBOT, option='robot_size'))
        self.trsl_dec = float(self.cs.config.get(section=ROBOT, option='trsl_dec'))
        self.trsl_max = float(self.cs.config.get(section=ROBOT, option='trsl_max'))

        # TODO: rename
        self.dist = ((self.size_x ** 2 + self.size_y ** 2) ** (1 / 2.0))

        self.actuators = self.cs.actuators[ROBOT]
        self.trajman = self.cs.trajman[ROBOT]

        self.goto_xy = event_waiter(self.trajman.goto_xy, self.start_event, self.stop_event, callback=self.check_abort_and_avoid)
        self.goto_theta = event_waiter(self.trajman.goto_theta, self.start_event, self.stop_event, callback=self.check_abort)
        self.move_trsl = event_waiter(self.trajman.move_trsl, self.start_event, self.stop_event, callback=self.check_abort)
        self.move_rot = event_waiter(self.trajman.move_rot, self.start_event, self.stop_event, callback=self.check_abort)
        self.recal = event_waiter(self.recalibration, self.start_event, self.stop_event, callback=self.check_abort)

        self.robot_position = Point(x=0, y=0)
        self.robot_orientation = 0.0
        self.current_speed = 0.0
        self.detected_robots = []
        self.avoid_side = False
        self.avoid_robot = None
        self.robot_size = float(self.cs.config.get(section='match', option='robot_size'))

        lidar_config = self.cs.config.get_section('rplidar')
        self.lidar = Rplidar(lidar_config)
        self.lidar.start_scanning()
        self.lidar.register_callback(self.lidar_callback)

        self.disabled = Event()
        self.need_to_abort = Event()
        self.has_abort = Event()
        self.has_avoid = Event()
        self.moving_side = None

        width = int(self.cs.config.get(section='map', option='width'))
        height = int(self.cs.config.get(section='map', option='height'))
        fixed_obstacles, self.color_obstacles = parse_obstacle_file('/etc/conf.d/obstacles.json')
        self.map = Map(width, height, self.size)
        self.map.add_obstacles(fixed_obstacles)

        def start_callback(id):
            self.need_to_abort.clear()
            self.publish('%s_robot_started' % ROBOT, id=id)

        def end_callback(id, r):
            if isinstance(r['status'], RobotStatus):
                r['status'] = r['status'].value
            self.publish('%s_robot_stopped' % ROBOT, id=id, **r)

        self.queue = ActQueue(
            start_callback,
            end_callback
        )
        self.queue.run_queue()

    @Service.event("match_color")
    def color_callback(self, color):
        with self.lock:
            self.side = color == self.color1

            for obstacle in self.color_obstacles:
                if 'tag' in obstacle:
                    self.map.remove_obstacle(obstacle['tag'])
            self.map.add_obstacles(self.color_obstacles, not self.side, type=ObstacleType.color)

    @Service.event("%s_telemetry" % ROBOT)
    def callback_telemetry(self, telemetry, **kwargs):
        with self.lock:
            self.robot_orientation = float(telemetry['theta'])
            self.robot_position = Point(dict=telemetry)
            self.current_speed = float(telemetry['speed']) * 1000

    def lidar_callback(self, cloud, shapes, robots):
        with self.lock :
            self.detected_robots = robots

    def get_path(self, origin, destination):

        robots_tags = []

        with self.lock:
            # Add robots on the map
            for i in range(len(self.detected_robots)):
                robots_tags.append('robot-%d' % i)
                global_pos = self.detected_robots[i].change_referencial(self.robot_position, self.robot_orientation)
                self.map.add_octogon_obstacle(global_pos, self.robot_size + 10, tag=robots_tags[-1], type=ObstacleType.robot)

            # Coompute path
            path = self.map.get_path(origin, destination)

            # Remove robots
            for tag in robots_tags:
                self.map.remove_obstacle(tag)

            return path


    @Service.action
    def enable(self):
        self.disabled.clear()
        self.queue.run_queue()

    @Service.event('match_end')
    @Service.action
    def disable(self):
        self.disabled.set()
        self.queue.stop_queue()
        self.need_to_abort.set()

    @Service.action
    def abort_action(self):
        self.need_to_abort.set()
        self.queue.clear_queue()

    @Service.action
    def stop_robot(self, dist=100):
        with self.lock:
            self.trajman.move_trsl(dest=dist, acc=0.0, dec=self.trsl_dec, sens=int(self.moving_side))

    def check_abort(self):
        if self.need_to_abort.is_set():
            self.has_abort.set()
            # TODO : compute dist
            self.stop_robot()
            self.need_to_abort.clear()
            return RobotStatus.Aborted
        return RobotStatus.Ok

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
                        self.avoid_robot = robot
                        return True

                    else:
                        print('[ROBOT] Ignoring obstacle: %s' % str(global_pos))

        return False

    def check_avoid(self):

        side = True
        detection_dist = 0.0
        with self.lock:
            if self.moving_side is None:
                self.moving_side = float(self.trajman.get_vector_trsl()['trsl_vector']) > 0

            side = self.moving_side

            # Compute needed stop_distance depending on deceleration and current speed
            stop_distance = (self.current_speed**2 / (2 * self.trsl_dec))
            detection_dist = stop_distance + 50

        if self.need_to_avoid(detection_dist, side):
            self.has_avoid.set()
            self.stop_robot(stop_distance)
            with self.lock:
                self.avoid_side = self.moving_side
            return RobotStatus.HasAvoid

        return RobotStatus.Ok

    def check_abort_and_avoid(self):
        status = self.check_abort()
        if status != RobotStatus.Ok:
            return status
        return self.check_avoid()

if __name__ == '__main__':
    robot = Robot()
    robot.run()
