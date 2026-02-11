#!/usr/bin/env python3

from cellaserv.proxy import CellaservProxy
from cellaserv.service import Event as CellaservEvent, Service

#from evolutek.lib.map.map import parse_obstacle_file, ObstacleType, Map
from evolutek.lib.utils.task import async_task
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
    forward = Service.action(robot_trajman.forward)
    goth = Service.action(robot_trajman.goth)
    goto_avoid = Service.action(robot_trajman.goto_avoid)
    goto_avoid_extend = Service.action(robot_trajman.goto_avoid_extend)
    goto_with_path = Service.action(robot_trajman.goto_with_path)
    move_back = Service.action(robot_trajman.move_back)
    recalibration = Service.action(robot_trajman.recalibration)
    recalibration_sensors = robot_trajman.recalibration_sensors
    homemade_recal = Service.action(robot_trajman.homemade_recal)

    # Imported from robot_actuators
    move_elevator  = Service.action(robot_actuators.move_elevator)
    move_elevator_ex = Service.action(robot_actuators.move_elevator_ex)
    move_plank_arm = Service.action(robot_actuators.move_plank_arm)
    move_pilar_arm = Service.action(robot_actuators.move_pilar_arm)
    toggle_magnets = Service.action(robot_actuators.toggle_magnets)
    toggle_pumps   = Service.action(robot_actuators.toggle_pumps)
    move_pumps_arm = Service.action(robot_actuators.move_pumps_arm)
    move_side_arms = Service.action(robot_actuators.move_side_arms)


    # Imported from robot_actions
    prepare_banner = Service.action(robot_actions.prepare_banner)
    place_banner = Service.action(robot_actions.place_banner)
    grab_materials = Service.action(robot_actions.grab_materials)
    prepare_second_layer = Service.action(robot_actions.prepare_second_layer)
    place_materials = Service.action(robot_actions.place_materials)
    build_3_layers = Service.action(robot_actions.build_3_layers)

    def __init__(self):
        super().__init__(ROBOT)

        self.cs = CellaservProxy()
        self.lock = Lock()

        self.cherry_count = 0
        self.cakes_stack = []
        self.elevator_status = "Low"

        self.bau_state = None
        self.color1 = self.cs.config.get('match', 'color1')
        self.side = True

        # Size of the robot and min dist from wall
        self.size_x = float(self.cs.config.get(section=ROBOT, option='robot_size_x'))
        self.size_y = float(self.cs.config.get(section=ROBOT, option='robot_size_y'))
        self.size = float(self.cs.config.get(section=ROBOT, option='robot_size'))
        self.dist_recal_sensors_to_center = float(self.cs.config.get(section=ROBOT, option='dist_recal_sensors_to_center'))

        # TODO: rename
        self.dist = ((self.size_x ** 2 + self.size_y ** 2) ** (1 / 2.0))

        self.actuators = self.cs.actuators[ROBOT]
        self.trajman = self.cs.trajman[ROBOT]

        self.goto_xy = event_waiter(self.trajman.goto_xy, self.start_event, self.stop_event, callback=self.check_abort)
        self.goto_theta = event_waiter(self.trajman.goto_theta, self.start_event, self.stop_event, callback=self.check_abort)
        self.move_trsl = event_waiter(self.trajman.move_trsl, self.start_event, self.stop_event, callback=self.check_abort)
        self.move_rot = event_waiter(self.trajman.move_rot, self.start_event, self.stop_event, callback=self.check_abort)
        self.goto_global = event_waiter(self.trajman.goto_global, self.start_event, self.stop_event, callback=self.check_abort)
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

        self.toggle_magnets(robot_actuators.MagnetsSetId.FRONT, robot_actuators.MagnetState.DISABLE, async_task = False)
        self.toggle_magnets(robot_actuators.MagnetsSetId.BACK, robot_actuators.MagnetState.DISABLE, async_task = False)

        self.toggle_pumps(robot_actuators.PumpsSetId.FRONT, False, async_task = False)
        self.toggle_pumps(robot_actuators.PumpsSetId.BACK, False, async_task = False)

        # self.move_elevator_ex(robot_actuators.ElevatorId.FRONT, 0, async_task = False)
        # self.move_elevator_ex(robot_actuators.ElevatorId.BACK, 0, async_task = False)

        self.move_plank_arm(robot_actuators.PlankArmId.FRONT, robot_actuators.PlankArmPosition.COLLAPSED, async_task = False)
        self.move_plank_arm(robot_actuators.PlankArmId.BACK, robot_actuators.PlankArmPosition.COLLAPSED, async_task = False)

        sleep(0.5)

        self.actuators.stepper_home(0, 80)
        sleep(0.05)
        self.actuators.stepper_home(2, 80)

        self.move_side_arms(robot_actuators.SideArmsId.FRONT, robot_actuators.SideArmPosition.NORMAL, async_task = False)
        self.move_side_arms(robot_actuators.SideArmsId.BACK, robot_actuators.SideArmPosition.NORMAL, async_task = False)

        self.move_pumps_arm(robot_actuators.PumpsArmId.FRONT, robot_actuators.PumpsArmPosition.COLLAPSED, async_task = False)
        self.move_pumps_arm(robot_actuators.PumpsArmId.BACK, robot_actuators.PumpsArmPosition.COLLAPSED, async_task = False)

        sleep(4)

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
