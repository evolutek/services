#!/usr/bin/env python3

from cellaserv.proxy import CellaservProxy
from cellaserv.service import Event as CellaservEvent, Service

#from evolutek.lib.map.map import parse_obstacle_file, ObstacleType, Map
from evolutek.lib.map.point import Point
import evolutek.lib.robot.robot_actions as robot_actions
import evolutek.lib.robot.robot_actuators as robot_actuators
import evolutek.lib.robot.robot_trajman as robot_trajman
from evolutek.lib.settings import ROBOT
from evolutek.lib.status import RobotStatus
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
    canon_on = Service.action(robot_actuators.canon_on)
    canon_off = Service.action(robot_actuators.canon_off)
    turbine_on = Service.action(robot_actuators.turbine_on)
    turbine_low_power = Service.action(robot_actuators.turbine_low_power)
    turbine_off = Service.action(robot_actuators.turbine_off)
    extend_left_vacuum = Service.action(robot_actuators.extend_left_vacuum)
    retract_left_vacuum = Service.action(robot_actuators.retract_left_vacuum)
    extend_right_vacuum = Service.action(robot_actuators.extend_right_vacuum)
    retract_right_vacuum = Service.action(robot_actuators.retract_right_vacuum)
    clamp_open = Service.action(robot_actuators.clamp_open)
    clamp_open_half = Service.action(robot_actuators.clamp_open_half)
    clamp_close = Service.action(robot_actuators.clamp_close)
    push_canon = Service.action(robot_actuators.push_canon)
    push_tank = Service.action(robot_actuators.push_tank)
    push_drop = Service.action(robot_actuators.push_drop)
    elevator_up = Service.action(robot_actuators.elevator_up)
    elevator_down = Service.action(robot_actuators.elevator_down)
    '''grab_stack = Service.action(robot_actuators.grab_stack)'''

    # Imported from robot_actions
    goto_random = Service.action(robot_actions.goto_random)
    roam_stacks = Service.action(robot_actions.roam_stacks)
    roam_zones = Service.action(robot_actions.roam_zones)
    go_grab_one_stack = Service.action(robot_actions.go_grab_one_stack)
    go_grab_some_stacks = Service.action(robot_actions.go_grab_some_stacks)
    go_drop_all = Service.action(robot_actions.go_drop_all)
    empty_n_cherries = Service.action(robot_actions.empty_n_cherries)
    empty_all_cherries = Service.action(robot_actions.empty_all_cherries)
    fill_n_cherries = Service.action(robot_actions.fill_n_cherries)
    fill_all_cherries = Service.action(robot_actions.fill_all_cherries)

    def __init__(self):

        super().__init__(ROBOT)

        self.cs = CellaservProxy()
        self.lock = Lock()

        self.cherry_count = 0

        self.bau_state = None
        self.color1 = self.cs.config.get('match', 'color1')
        self.side = True

        # Size of the robot and min dist from wall
        self.size_x = float(self.cs.config.get(section=ROBOT, option='robot_size_x'))
        self.size_y = float(self.cs.config.get(section=ROBOT, option='robot_size_y'))
        self.size = float(self.cs.config.get(section=ROBOT, option='robot_size'))
        self.dist_to_center = float(self.cs.config.get(section=ROBOT, option='dist_to_center'))

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
        self.pattern = None
        self.disabled = Event()
        self.need_to_abort = Event()

        width = int(self.cs.config.get(section='map', option='width'))
        height = int(self.cs.config.get(section='map', option='height'))
        '''fixed_obstacles, self.color_obstacles = parse_obstacle_file('/etc/conf.d/obstacles.json')
        self.map = Map(width, height, self.size)
        self.map.add_obstacles(fixed_obstacles)'''
        self.path = []
        self.robots = []
        self.robots_tags = []

        self.current_task = None
        Thread(target=self.run_tasks).start()

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

    def run_tasks(self):
        while True:
            sleep(0.1)

            if self.disabled.is_set():
                continue

            if self.current_task is None:
                continue

            task = None
            with self.lock:
                task = self.current_task

            print('[ROBOT] Running task:')
            print(task)

            self.need_to_abort.clear()
            self.publish('%s_robot_started' % ROBOT, id=task.id)
            r = None
            try:
                r = task.run()
            except Exception as e:
                print('[ROBOT] Task crashed due to %s' % str(e))
                r = RobotStatus.return_status(RobotStatus.Failed)

            self.publish('%s_robot_stopped' % ROBOT, id=task.id, **r)

            with self.lock:
                self.current_task = None

    @Service.event("match_color")
    def color_callback(self, color):
        with self.lock:
            self.side = color == self.color1

            '''for obstacle in self.color_obstacles:
                if 'tag' in obstacle:
                    self.map.remove_obstacle(obstacle['tag'])
            self.map.add_obstacles(self.color_obstacles, not self.side, type=ObstacleType.color)'''

    def get_path(self, destination):

        robots = self.trajman.get_robots()
        detected_robots = [ Point(dict=robot) for robot in robots ]
        origin = Point(dict=self.trajman.get_position())

        # TODO : useful ?
        with self.lock:
            '''# Remove robots
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

            self.path = path'''
            self.robots = robots
            return destination  # path

    '''def clean_map(self):
         with self.lock:
            # Remove robots
            for tag in self.robots_tags:
                self.map.remove_obstacle(tag)
            self.robots_tags.clear()
            self.path.clear()'''

    @Service.action
    def enable(self):
        if self.bau_state:
            self.disabled.clear()

    @Service.action
    def disable(self):
        #self.clamp_open(async_task=False)
        self.disabled.set()
        self.need_to_abort.set()

    @Service.action
    def reset(self):
        if not self.bau_state:
            return
        self.enable()
        #self.clamp_open(async_task=False)
        sleep(0.5)
        self.elevator_down(async_task=False)
        sleep(1)

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

    @Service.action
    def abort_action(self):
        self.need_to_abort.set()

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
