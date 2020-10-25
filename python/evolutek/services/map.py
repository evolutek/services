#! /usr/bin/python3
from cellaserv.service import Service, Event
from cellaserv.proxy import CellaservProxy

from evolutek.lib.map.debug_map import Interface
from evolutek.lib.map.map import parse_obstacle_file, ObstacleType, Map as Map_lib
from evolutek.lib.map.point import Point

from evolutek.lib.map.utils import convert_path_to_dict, convert_path_to_point, merge_polygons
#from evolutek.lib.settings import SIMULATION

#if SIMULATION:
#  from evolutek.simulation.fake_lib.fake_tim import DebugMode, Tim
#else:
from evolutek.lib.map.tim import DebugMode, Tim

import json
from shapely.geometry import Polygon, MultiPolygon
from threading import Lock
import json
from time import sleep

@Service.require('config')
#@Service.require('match')
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
        self.tims = {}
        self.tim_config = None
        with open('/etc/conf.d/tim.json', 'r') as tim_file:
            self.tim_config = tim_file.read()
            self.tim_config = json.loads(self.tim_config)
        self.robots = []
        self.nbrobots = 0

        # Gets the color (side) of the robot
        self.color = None
        self.color1 = self.cs.config.get(section='match', option='color1')
        self.color2 = self.cs.config.get(section='match', option='color2')
        try:
            color = self.cs.match.get_color()
            self.match_color(color)
        except Exception as e:
            print('[MAP] Failed to get color: %s\nUsing default %s' % (str(e), self.color1))
            self.match_color(self.color1) # Default color

        self.robot_size = int(self.cs.config.get(section='match', option='robot_size'))
        self.delta_dist = float(self.cs.config.get(section='tim', option='delta_dist')) * 2
        self.pal_telem = None
        self.pmi_telem = None
        self.clouds = []
        self.tim_scans = {}

    # Initialisation -----------------------------------------------------------

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
          if tim['ip'] in self.tims and not self.tims[tim['ip']] is None:
            self.tims[tim['ip']].change_pos(self.color != self.color1)
          else:
            self.tims[tim['ip']] = Tim(tim, self.tim_computation_config, self.color != self.color1)

  # Getters ------------------------------------------------------------------

    """ ACTION """
    @Service.action
    def get_opponents(self):
        return self.robots

    """ ACTION """
    @Service.action
    def get_path(self, origin, dest, robot):

        # To request path from terminal:
        # cellaservctl request map.get_path origin="{'x':300,'y':300}" dest="{'x':500,'y':500}" robot="pal"
        #import json
        #origin = json.loads(origin.replace("'",'"'))
        #dest = json.loads(dest.replace("'",'"'))

        with self.lock:
            print("[MAP] Path request received")
            if robot not in ['pal', 'pmi']:
                print("[MAP] WARNING: Unknown robot " + robot + ". Possible values are pal and pmi")
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
            res = convert_path_to_dict(self.path)
            if robot in ['pal', 'pmi']:
                self.publish(robot+'_path', robot=robot, path=res)
            print("[MAP] Path: " + str(res))
            return res

    """ ACTION """
    @Service.action
    def get_obstacles(self):
        with self.lock:

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

    """ ACTION """
    @Service.action
    def is_path_valid(self, path, robot):
        with self.lock:
            print("[MAP] Path validity check request received")
            if robot not in ['pal', 'pmi']:
                print("[MAP] WARNING: Unknown robot " + robot + ". Possible values are pal and pmi")
            else:
                # Adds the other robot as an obstacle
                other_robot = 'pmi' if robot == 'pal' else 'pal'
                if getattr(self, '%s_telem' % other_robot) is None:
                    print("[MAP] WARNING: %s telemetry not known, checking valididy ignoring it" % other_robot)
                else:
                    self.map.add_octogon_obstacle(
                            Point(dict=getattr(self, '%s_telem' % other_robot)),
                            getattr(self, '%s_size' % other_robot),
                            tag='otherrobot',
                            type=ObstacleType.robot)
            # Checks the validity
            res = self.map.is_path_valid(convert_path_to_point(path))
            # Removes the temporary obstacle that corresponds to the other robot
            self.map.remove_obstacle('otherrobot')
            return res

  # Config ----------------------------------------------------------

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
        self.publish("tim_debug_mode", mode=mode)

    # Updaters -----------------------------------------------------------------

    """ EVENT """
    @Service.event
    def pal_telemetry(self, status, telemetry, robot):
      # To place a fake pal from terminal:
      # cellaservctl p pal_telemetry status='success' telemetry="{'x':1000,'y':1000,'theta':0}" robot="pal"
      #import json
      #telemetry = json.loads(telemetry.replace("'",'"'))
      if status != 'failed':
        self.pal_telem = telemetry


    """ EVENT """
    @Service.event
    def pmi_telemetry(self, status, telemetry, robot):
      # To place a fake pmi from terminal:
      # cellaservctl p pmi_telemetry status='success' telemetry="{'x':1000,'y':1000,'theta':0}" robot="pmi"
      #import json
      #telemetry = json.loads(telemetry.replace("'",'"'))
      print("Telemetry received")
      if status != 'failed':
        self.pmi_telem = telemetry
      else:
        print("failed")


    """ THREAD """
    @Service.thread
    def loop_scan(self):
      while True:

        # Iterate over tim
        tims = {}
        merges = {}
        scans = {}
        clouds = []
        id = 0
        for ip in self.tims:

          tim = self.tims[ip]

          # Not connected
          if not tim.connected:
            continue
          if self.debug_mode == DebugMode.debug_tims:
            self.tim_scans[ip] = convert_path_to_dict(tim.get_raw_data())
          scan = tim.get_scan()
          scans[tim.ip] = scan
          # merge all robots together
          for new in scan:
            merged = False
            for cloud in clouds:
              merged = cloud.merge(new, self.delta_dist)
              if merged:
                break
            if not merged:
              clouds.append(new)

              if self.pal_telem and new.merged_pos.dist(self.pal_telem) < self.delta_dist:
                new.tag = "PAL"
                new.add_telemetry(self.pal_telem)
              elif self.pmi_telem and new.merged_pos.dist(self.pmi_telem) < self.delta_dist:
                new.tag = "PMI"
                new.add_telemetry(self.pmi_telem)
          # Add not merged robots
        robots = []
        for cloud in clouds:
          if cloud.tag == "PAL" or cloud.tag == "PMI":
            continue
          else:
            robots.append(cloud.merged_pos)

        with self.lock:
          # Remove old robots
          #for robot in self.robots:
          #  self.map.remove_obstacle(robot['tag'])
          #self.robots.clear()
          self.clouds.clear()
          self.clouds = clouds[:]
          translated_clouds = [cloud.to_dict() for cloud in self.clouds]
          # Remove robots from the map #TODO: I think it could be greatly optimized
          for i in range(self.nbrobots):
            tag = "robot%d" % i
            self.map.remove_obstacle(tag)
          # Add robots on the map
          i = 0
          self.robots.clear()
          for robot in robots:
            tag = "robot%d" % i
            if self.map.add_octogon_obstacle(robot, self.robot_size, tag=tag, type=ObstacleType.robot):
              d = robot.to_dict()
              d['tag'] = tag
              i += 1
              self.robots.append(d)
          self.nbrobots = len(robots)

          #print('[MAP] Detected %d robots' % len(self.robots))
          #self.publish('tim_detected_robots', robots=self.robots)
          #if self.debug_mode == DebugMode.debug_tims:
          #  self.publish('tim_scans', scans=self.tim_scans)
          #if self.debug_mode == DebugMode.debug_merge:
          #  self.publish('tim_merge', merge= translated_clouds)
        sleep(self.refresh / 1000)


def main():
    map = Map()
    map.run()

if __name__ == '__main__':
    main()
