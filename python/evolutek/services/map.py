from cellaserv.service import Service, Event
from cellaserv.proxy import CellaservProxy

from evolutek.lib.map.debug_map import Interface
from evolutek.lib.map.map import Map as Map_lib, ObstacleType, parse_obstacle_file
from evolutek.lib.map.tim import DebugMode, Tim
from evolutek.lib.map.point import Point
from evolutek.lib.map.utils import convert_path_to_dict

from threading import Lock
import json
from time import sleep


@Service.require('config')
@Service.require('match')
class Map(Service):
    def __init__(self):
        super().__init__()

        self.cs = CellaservProxy()
        self.lock = Lock()
        self.debug_mode = DebugMode.normal

        # Map (lib) init
        width = int(self.cs.config.get(section='map', option='width'))
        height = int(self.cs.config.get(section='map', option='height'))
        self.pal_size = float(self.cs.config.get(section='pal', option='robot_size'))
        self.pmi_size = float(self.cs.config.get(section='pmi', option='robot_size_y'))
        fixed_obstacles, self.color_obstacles = parse_obstacle_file('/etc/conf.d/obstacles.json')
        self.map = Map_lib(width, height, self.pal_size)
        self.map.add_obstacles(fixed_obstacles)
        self.path = []

        # TIM (lidars) init
        self.refresh = int(self.cs.config.get(section='tim', option='refresh'))
        self.tim_computation_config = self.cs.config.get_section('tim')
        self.tim = {}
        self.tim_config = None
        with open('/etc/conf.d/tim.json', 'r') as tim_file:
            self.tim_config = tim_file.read()
            self.tim_config = json.loads(self.tim_config)
        self.robots = []

        # Gets the color (side) of the robot
        self.color = None
        self.color1 = self.cs.config.get(section='match', option='color1')
        self.color2 = self.cs.config.get(section='match', option='color2')
        try:
            color = self.cs.match.get_color()
            self.match_color(color)
        except Exception as e:
            print('[MAP] Failed to get color: %s\nUsing default Yellow' % str(e))
            self.match_color(self.color1) # Default color

        self.robot_size = int(self.cs.config.get(section='match', option='robot_size'))
        self.delta_dist = float(self.cs.config.get(section='tim', option='delta_dist')) * 2
        self.pal_telem = None
        self.pmi_telem = {'x':900, 'y':900}

    # Initialisation -----------------------------------------------------------

    """ THREAD """
    # TODO: Disable for beacon
    @Service.thread
    def start_debug_interface(self):
        self.interface = Interface(self.map, self)


    """ EVENT """
    @Service.event
    def match_color(self, color):
        if color != self.color:
            self.color = color

        if self.color is not None:
            # Change color obstacles position
            with self.lock:
                for obstacle in self.color_obstacles:
                    if 'tag' in obstacle:
                        self.map.remove_obstacle(obstacle['tag'])
                self.map.add_obstacles(self.color_obstacles, self.color != self.color1, type=ObstacleType.color)

        # Connected to the tim or change the pos if it is already connected
        for tim in self.tim_config:
            if tim['ip'] in self.tim and not self.tim[tim['ip']] is None:
                self.tim[tim['ip']].change_pos(self.color != self.color1)
            else:
                self.tim[tim['ip']] = Tim(tim, self.tim_computation_config, self.color != self.color1)

    # Getters ------------------------------------------------------------------

    """ ACTION """
    @Service.action
    def get_opponnents(self):
        return self.robots


    """ ACTION """
    @Service.action
    def get_path(self, origin, dest, for_robot):

        # To request path from terminal:
        # cellaservctl request map.get_path origin="{'x':300,'y':300}" dest="{'x':900,'y':900}" for_robot="pal"
        # import json
        # origin = json.loads(origin.replace("'",'"'))
        # dest = json.loads(dest.replace("'",'"'))

        print("[MAP] Path request received")
        with self.lock:
            if for_robot not in ['pal', 'pmi']:
                print("[MAP] WARNING: Unknown robot " + for_robot + ". Possible values are pal and pmi");
            else:
                # Adds the other robot as an obstacle
                other_robot = 'pmi' if for_robot == 'pal' else 'pal'
                if getattr(self, '%s_telem' % other_robot) is None:
                    print("[MAP] WARNING: %s telemetry not known, calculating a path ignoring it" % other_robot)
                else:
                    self.map.add_octogon_obstacle(
                            Point(dict=getattr(self, '%s_telem' % other_robot)),
                            getattr(self, '%s_size' % other_robot),
                            tag='otherrobot',
                            type=ObstacleType.robot)
            # Finds the path
            self.path = self.map.get_path(Point(dict=origin), Point(dict=dest))
            # Removes the temporary obstacle that corresponds to the other robot
            self.map.remove_obstacle('otherrobot')

        return convert_path_to_dict(self.path)

    # Config ----------------------------------------------------------

    """ ACTION """
    @Service.action
    def add_tmp_obstacle(self, pos):
        pass # TODO

    """ ACTION """
    @Service.action
    def clean_tmp_obstacle(self):
        pass # TODO

    """ ACTION """
    @Service.action
    def set_debug_mode(self, mode):
        new_mode = None
        try:
            new_mode = DebugMode(int(mode))
        except:
            print('[MAP] Debug mode not existing')
            return
        print('[MAP] Setting debug mode to %s' % new_mode.value)
        self.debug_mode = new_mode

    # Updaters -----------------------------------------------------------------

    """ EVENT """
    @Service.event
    def pal_telemetry(self, status, telemetry):
        if status != 'failed':
            self.pal_telem = telemetry

    """ EVENT """
    @Service.event
    def pmi_telemetry(self, status, telemetry):
        if status != 'failed':
            self.pmi_telem = telemetry


    # TODO: debug mode not getting oppenents
    """ THREAD """
    @Service.thread
    def loop_scan(self):
        while True:

            # Iterate over tim
            scans = {}
            for ip in self.tim:

                tim = self.tim[ip]

                # Not connected
                if not tim.connected:
                    continue

                scan = tim.get_scan()
                scans[tim.ip] = scan

            # Merge robots
            robots = []
            for ip in scans:

                new = []
                for point in scans[ip]:

                    # It's one of our robots
                    if (self.pal_telem and point.dist(self.pal_telem) < self.delta_dist)\
                        or (self.pmi_telem and point.dist(self.pmi_telem) < self.delta_dist):
                        continue

                    merged = False
                    for robot in robots:
                        # Already know this robot: merge it with the current point
                        if robot.dist(point) < self.delta_dist:
                            new.append(robot.average(point))
                            robots.remove(robot)
                            merged = True
                            break

                    # Robot not found, add it
                    if not merged:
                        new.append(point)

                # Add not merged robots
                new += robots
                robots = new

            with self.lock:

                # Remove old robots
                #for robot in self.robots:
                #    self.map.remove_obstacle(robot['tag'])
                #self.robots.clear()

                # Add robots on the map
                i = 0
                for robot in robots:
                    tag = "robot%d" % i
                    if self.map.add_octogon_obstacle(robot, self.robot_size, tag=tag, type=ObstacleType.robot):
                        d = point.to_dict()
                        d['tag'] = tag
                        i += 1
                        self.robots.append(d)

                #print('[MAP] Detected %d robots' % len(self.robots))
                #self.publish('opponents', robots=self.robots)
            sleep(self.refresh / 1000)

    # --------------------------------------------------------------------------


def main():
  map = Map()
  map.run()

if __name__ == '__main__':
  main()
