from enum import Enum
from math import cos, sin, radians, sqrt
from socket import socket, AF_INET, SOCK_STREAM
from time import sleep
from evolutek.lib.map.point import Point
from threading import Thread, Lock
import evolutek.lib.map.utils as utils
# Debug Modes of a TIM :
# - normal : display only the viewed robots
# - debug_merge : display all the viewed robots befor merging
# - debug_tims : display all data from tims
class DebugMode(Enum):
  normal=0
  debug_merge=1
  debug_tims=2

# Parse a number if it is in HEX
def parse_num(s):
  if '+' in s or '-' in s:
    return int(s)
  else:
    return int(s, 16)

# Cloud class
#
# points: Point[]
# center: Point
# ip: str
# tag: str
class RobotCloud:
  def __init__(self, points=[], center=None, ip="", tag="", dict=None):
    self.points = {}
    self.pos = {}
    if dict is not None:
      from_dict(dict)
    else:
      self.points[ip] = points[:]
      self.pos[ip] = center
      self.merged_pos = self.pos[ip]
      self.tag = tag

  def __str__(self):
    return self.tag + self.merged_pos
  
  # Import from dict
  def from_dict(self, dict):
      for ip in dict["points"]:
        self.points[ip] = utils.convert_path_to_points(dict["points"])
        self.pos[ip]= Point(dict=dict["pos"])
      self.merged_pos = Point(dict=dict["merged_pos"])
      self.tag = dict["tag"]

  # Export to dict
  def to_dict(self):
    temp_points = {}
    temp_pos = {}
    for ip in self.pos:
      temp_points[ip] = utils.convert_path_to_dict(self.points[ip])
      temp_pos[ip] = self.pos[ip].to_dict()
    return { 
        "points": temp_points,
        "pos": temp_pos,
        "merged_pos": self.merged_pos.to_dict(),
        "tag": self.tag,
        }

  # Merge with another cloud
  def merge(self, other, delta_dist):
    ip = list(other.pos.keys())[0]
    if ip in self.points:
      return False
    if self.merged_pos.dist(other.merged_pos) < delta_dist:
      self.points[ip] = other.points[ip][:]
      self.pos[ip] = other.pos[ip]
      # get position from closest lidar
      max_size = 0
      max_pos = []
      for ip in self.points:
        if len(self.points[ip]) > max_size:
          max_pos = [self.pos[ip]]
          max_size = len(self.points[ip])
        elif len(self.points[ip]) == max_size:
          max_pos.append(self.pos[ip])
      self.merged_pos = Point.mean(max_pos)
      return True
    else:
      return False

  # Add a telemtry
  def add_telemetry(self, pos):
    self.pos["telemetry"] = Point(dict=pos)
    self.points["telemetry"] = []
    self.merged_pos = Point(dict = pos)


# TIM Class

# config: {ip : str, port : int, pos_x : int, pos_y : int, angle : int}
# computation_config: {refresh : float, min_size: int, max_distance: int, radius_beacon: int}
# mirror: indicate if we need to mirror the tim

# config:
# - ip: ip of the tim : str
# - port : port of the tim : int
# - pos_x : x position : int
# - pos_y : y position : int
# - angle : angle in degree : int

# computation_config:
# - min_size: min size of a shape : int
# - max_distance: max distance between two points for a robot : int
# - radius_beacon: radius of a beacon placed on a robot : int
# - refresh: refresh of a TIM : float
class Tim:

    def __init__(self, config, computation_config, debug, mirror=False):
        self.scan_list = []

        # Network config
        self.ip = config['ip']
        self.port = int(config['port'])

        # Pos config
        self.default_pos = Point(int(config['pos_x']),int(config['pos_y']))
        self.default_angle = int(config['angle'])

        # Computation config
        self.refresh = float(computation_config['refresh'])
        self.min_size = int(computation_config['min_size'])
        self.max_distance = int(computation_config['max_distance'])
        self.radius_beacon = int(computation_config['radius_beacon'])

        self.raw_data = []
        self.shapes = []
        self.robots = []
        self.clouds = []

        self.socket = socket(AF_INET, SOCK_STREAM)
        self.connected = False
        self.lock = Lock()

        self.pos = None
        self.angle = None
        self.change_pos(mirror)
        self.try_connection()
        print(self)

        print('[TIM] TIM created')

    def __str__(self):
        s = "ip: %s\n" % self.ip
        s += "port: %d\n" % self.port
        s += "pos: " + str(self.pos) + "\n"
        s += "angle: %d\n" % self.angle
        s += "connected: %s" % str(self.connected)
        return s

    # Launch a thread to communicate with tim
    def try_connection(self):
        Thread(target = self._try_connection).start()

    # Try to connect to TIM via a TCP/IP Socket
    # Loop to try connection
    # Launch loop_scan()
    # Infinite loop
    def _try_connection(self):
        while True:
            while not self.connected:
                try:
                    print('[TIM] Connecting to the TIM: %s, %d' % (self.ip, self.port))
                    self.socket.connect((self.ip, self.port))
                    self.connected = True

                except Exception as e:
                    print('[TIM] Failed to connect to the TIM %s: %s' % (self.ip, str(e)))
                    self.connected = False
                    sleep(1)

            self.loop_scan()

    # Change the pos of the TIM according of the side of the table
    def change_pos(self, mirror=False):
        self.pos = Point(self.default_pos.x, 3000 - self.default_pos.y if mirror else self.default_pos.y)
        self.angle = self.default_angle * -1 if mirror else self.default_angle
        print('[TIM] Changing tim %s pos: %s, angle: %d' % (self.ip, self.pos, self.angle))

    # Send a scan request to the tim
    def send_request(self):
        try:
            self.socket.sendall("\x02sRN LMDscandata\x03\0".encode())
        except Exception as e:
            print('[TIM] Failed to send scan request to %s: %s' % (self.ip, str(e)))
            self.connected = False
            return None
        data = ""

        while True:
            try:
                part = self.socket.recv(1024)
            except Exception as e:
                print('[TIM] Failed to recieve scan data of %s: %s' % (self.ip, str(e)))
                self.connected =  False
                return None
            data += part.decode()
            if "\x03" in part.decode():
                break
        length = len(data)
        if (data[0] != '\x02' or data[length - 1] != '\x03'):
            print("[TIM] Bad response for the TIM %s" % self.ip)
            return None

        return data[1:len(data) - 2].split(' ')

    # Change all the cylindrical coords to cardinal coords
    def convert_to_card(self, cyl_data, size_a):
        clean_data = []
        length = len(cyl_data)
        for i in range(0, length):
            angle = radians((length - i) * size_a - self.angle)
            y = cyl_data[i] * cos(angle) + self.pos.y
            x = cyl_data[i] * sin(angle) + self.pos.x
            clean_data.append(Point(round(x), round(y)))
        return clean_data

    # Remove out  of table points
    # TODO: use obstacle config config
    def cleanup(self, raw_points):
        clean_points = []
        for p in raw_points:
            if p.y >= 0 and p.y <= 3000 and p.x >= 0 and p.x <= 2000:
                clean_points.append(p)
        return clean_points

    # Split raw date in shapes
    def split_raw_data(self, raw_data):
        shapes = []
        shape = []
        for p in raw_data:
            if len(shape) == 0 or p.dist(shape[-1]) < self.max_distance:
                shape.append(p)
            else:
                if len(shape) >= self.min_size:
                    shapes.append(shape)
                shape = [p]
        if len(shape) >= self.min_size:
            shapes.append(shape)
        return shapes

    # Compute center of shape using the ray between the mean of the shape and the pos of TIM
    def compute_center(self, shape):
        moy = Point.mean(shape)
        a = 0
        b = 0
        dy = False
        if self.pos.x != moy.x:
            a = (moy.y - self.pos.y) / (moy.x - self.pos.x)
            b = moy.y - a * moy.x
        else:
            dy = True
            a = (moy.x - self.pos.x) / (moy.y - self.pos.y)
            b = moy.x - a * moy.y
        radius = self.radius_beacon * (-1 if self.pos.x > moy.x else 1)
        x = 0
        y = 0
        if dy:
            y = moy.y + (radius / sqrt(1 + a ** 2))
            x = a * y + b
        else:
            x  = moy.x + (radius / sqrt(1 + a ** 2))
            y = a * x + b
        return Point(x, y)

    # Make a scan
    def scan(self):

        if self.pos is None or self.angle is None:
            print('[TIM] %s Pos or angle not configured' % self.ip)
            return None

        data = self.send_request()

        if data is None:
            return None

        angular_step = parse_num(data[24])/10000.0
        length = parse_num(data[25])

        if length == 0:
            return [], [], [], []

        # Convert data to cardinal coordinates
        raw_points = self.convert_to_card(list(map(parse_num, data[26:26 + length])), angular_step)

        # Remove point out of the table
        clean_points = self.cleanup(raw_points)

        # Split points in different cloud
        shapes = self.split_raw_data(clean_points)
        # Compute robots center
        clouds = []
        # Generate unified output
        for shape in shapes:
          clouds.append(RobotCloud(shape, ip=self.ip, center=self.compute_center(shape)))
        #print("[TIM] End scanning")
        return clean_points, clouds

    # Loop to make scans
    def loop_scan(self):
        while self.connected:
          sleep(.1)
          new_data = self.scan()
          if new_data is None:
              return
          with self.lock:
              if new_data is None:
                  print('[TIM] Failed to get scan on %s' % self.ip)
                  self.raw_data.clear()
                  self.clouds.clear()
                  continue
              self.raw_data, self.clouds = new_data

    # Return raw data
    def get_raw_data(self):
        with self.lock:
            return self.raw_data

    # Return viewed robots
    def get_robots(self):
        robots = []
        with self.lock:
          robots = [c.merged_pos for cloud in self.clouds]

        return robots
    
    # Return all scan info
    def get_scan(self):
        scan = []
        with self.lock:
            scan = self.clouds
        return scan
