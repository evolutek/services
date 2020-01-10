from enum import Enum
from math import cos, sin, radians, sqrt
from socket import socket, AF_INET, SOCK_STREAM
from time import sleep
from evolutek.lib.map.point import Point
from threading import Thread, Lock

class DebugMode(Enum):
    normal=0
    debug_merge=1
    debug_tims=2

def parse_num(s):
    if '+' in s or '-' in s:
        return int(s)
    else:
        return int(s, 16)

# TIM Class

# config: {ip : str, port : int, pos_x : int, pos_y : int, angle : int}
# pos: position of the TIM: Point(x, y)
# angle: angle of the TIM: int


# computation_config: (min_size : int, max_distance : int, radius_beacon : int, refresh : float}
# min_size: min size of a shape : int
# max_distance: max distance between two points for a robot : int
# radius_beacon: radius of a beacon placed on a robot : int
# refresh: refresh of a TIM : float

# try_connection():
# Try to connect to TIM via a TCP/IP Socket
# Launch a thread which will make scans

# change_pos(mirror):
# Change the pos of the TIM according of the side of the table

# convert_to_card(cyl_data, size_a):
# Change all the cylindrical coords to cardinal coords

# cleanup(raw_points):
# Remove out table points

# split_raw_data(sraw_data):
# Split raw date in shapes

# ompute_center(shapes):
# Compute center of shape using the ray between the mean of the shape and the pos of TIM

# scan():
# Make a scan

# loop_scan():
# Loop to make scans

# get_scan():
# Return detected robots

class Tim:

    def __init__(self, config, computation_config, mirror=False):

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

        self.socket = socket(AF_INET, SOCK_STREAM)
        self.connected = False
        self.lock = Lock()

        self.pos = None
        self.angle = None
        self.change_pos(mirror)
        self.try_connection()

        print('TIM created')

    def __str__(self):
        s = "ip: %s\n" % self.ip
        s += "port: %d\n" % self.port
        s += "pos: " + str(self.pos) + "\n"
        s += "angle: %d\n" % self.angle
        s += "connected: %s" % str(self.connected)
        return s

    def try_connection(self):
        Thread(target = self._try_connection).start()


    def _try_connection(self):
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

    def change_pos(self, mirror=False):
        self.pos = Point(self.default_pos.x, 3000 - self.default_pos.y if mirror else self.default_pos.y)
        self.angle = self.default_angle * -1 if mirror else self.default_angle
        print('[TIM] Changing tim %s pos: %s, angle: %d' % (self.ip, self.pos, self.angle))

    def convert_to_card(self, cyl_data, size_a):
        clean_data = []
        length = len(cyl_data)
        for i in range(0, length):
            angle = radians(length - i * size_a + self.angle)
            y = cyl_data[i] * cos(angle) + self.pos.y
            x = cyl_data[i] * sin(angle) + self.pos.x
            clean_data.append(Point(x, y))
        return clean_data

    # TODO: use table config
    def cleanup(self, raw_points):
        clean_points = []
        for p in raw_points:
            if p.y >= 0 and p.y <= 3000 and p.x >= 0 and p.x <= 2000:
                clean_points.append(p)
        return clean_points

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

    def compute_center(self, shapes):
        centers = []
        for shape in shapes:
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
            centers.append(Point(x, y))
        return centers

    def scan(self):

        if self.pos is None or self.angle is None:
            print('[TIM] %s Pos or angle not configured' % self.ip)
            return None

        try:
            self.socket.sendall("\x02sRN LMDscandata\x03\0".encode())
        except Exception as e:
            print('[TIM] Failed to send scan request to %s: %s' % (self.ip, str(e)))
            self.connected = False
            self._try_connection()
        data = ""

        while True:
            try:
                part = self.socket.recv(1024)
            except Exception as e:
                print('[TIM] Failed to recieve scan data of %s: %s' % (self.ip, str(e)))
                self.connected =  False
                self._try_connection()
            data += part.decode()
            if "\x03" in part.decode():
                break
        length = len(data)
        if (data[0] != '\x02' or data[length - 1] != '\x03'):
            print("[TIM] Bad response for the TIM %s" % self.ip)
            return None
        data = data[1:len(data) - 2].split(' ')
        angular_step = parse_num(data[24])/10000
        length = parse_num(data[25])

        # Convert data to cardinal coordinates
        raw_points = self.convert_to_card(list(map(parse_num, data[26:26 + length])), angular_step)

        # Remove point out of the table
        clean_points = self.cleanup(raw_points)

        # Split points in different cloud
        shapes = self.split_raw_data(clean_points)

        # Compute robots center
        robots = self.compute_center(shapes)

        #print("[TIM] End scanning")
        return clean_points, shapes, robots

    def loop_scan(self):
        while self.connected:
          sleep(.1)
          new_data = self.scan()
          with self.lock:
              if new_data is None:
                  print('[TIM] Failed to get scan on %s' % self.ip)
                  self.raw_data.clear()
                  self.shapes.clear()
                  self.robots.clear()
                  continue
              self.raw_data, self.shapes, self.robots = new_data

    def get_scan(self):

        with self.lock:
            robots = self.robots

        return robots
