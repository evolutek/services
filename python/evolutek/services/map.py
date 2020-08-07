from cellaserv.service import Service, Event
from cellaserv.proxy import CellaservProxy

from evolutek.utils.match_interface import MatchInterface as Interface
from evolutek.lib.map.map import Map as Map_lib, ObstacleType, parse_obstacle_file
from evolutek.lib.map.tim import DebugMode, Tim
from evolutek.lib.map.point import Point

from evolutek.lib.map.utils import convert_path_to_dict, merge_polygons
from evolutek.lib.settings import SIMULATION

if SIMULATION:
    from evolutek.simulation.fake_lib.fake_tim import DebugMode, Tim
else:
    from evolutek.lib.map.tim import DebugMode, Tim

import json
from shapely.geometry import Polygon, MultiPolygon
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
        self.pmi_telem = None

    # Initialisation -----------------------------------------------------------

    """ THREAD """
    # TODO: Disable for beacon
    @Service.thread
    def start_debug_interface(self):
        self.interface = Interface()


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
    def get_path(self, origin, dest, robot):

        # To request path from terminal:
        # cellaservctl request map.get_path origin="{'x':300,'y':300}" dest="{'x':500,'y':500}" robot="pal"
        import json
        origin = json.loads(origin.replace("'",'"'))
        dest = json.loads(dest.replace("'",'"'))

        print("[MAP] Path request received")
        with self.lock:
            if robot not in ['pal', 'pmi']:
                print("[MAP] WARNING: Unknown robot " + robot + ". Possible values are pal and pmi");
            else:
                # Adds the other robot as an obstacle
                other_robot = 'pmi' if robot == 'pal' else 'pal'
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
            # Publishes the new path
            if robot in ['pal', 'pmi']:
                res = [p.to_dict() for p in self.path]
                self.publish(robot+'_path', robot=robot, path=res)
            return convert_path_to_dict(self.path)


    """ ACTION """
    @Service.action
    def get_obstacles(self):
        l = []

        # Merge map
        obstacles = MultiPolygon()
        for obstacle in self.map.obstacles:
            obstacles = obstacles.union(obstacle)
        for tag in self.map.color_obstacles:
            obstacles = obstacles.union(self.map.color_obstacles[tag])

        polygons = self.map.borders
        if isinstance(obstacles, Polygon):
            obstacles = [obstacles]
        for poly in obstacles:
            polygons = merge_polygons(polygons, poly)

        if isinstance(polygons, Polygon):
            polygons = [polygons]

        # Add exterior polygons
        for poly in polygons:
            _l = []
            for p in poly.exterior.coords:
                _l.append(Point(tuple=p).to_dict())
            l.append(_l)

            # Add interior polygons
            for _poly in poly.interiors:
                _l = []
                for p in _poly.coords:
                    _l.append(Point(tuple=p).to_dict())
                l.append(_l)

        return l

    """ ACTION """
    @Service.action
    def get_debug_mode(self):
        return self.debug_mode.value


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


    """ THREAD """
    @Service.thread
    def loop_scan(self):
        # TODO
        pass


    # --------------------------------------------------------------------------


def main():
  map = Map()
  map.run()

if __name__ == '__main__':
  main()
