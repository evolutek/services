from math import cos, sin, radians, sqrt
from socket import socket, AF_INET, SOCK_STREAM
from time import sleep
from evolutek.lib.point import Point
from threading import Thread, Lock

def parse_num(s):
    if '+' in s or '-' in s:
        return int(s)
    else:
        return int(s, 16)

# TODO: Update Documentation
# TIM Class
# config: {pos_x : int, pos_y : int, angle : float, min_size : float, max_distance : float, ip : str, port : int}
# pos is the position of the TIM: Point(x, y)
# angle is the angle of the TIM: float
# min_size is the min size of a shape : float
# max_distance is the max distance between two points for a robot : float

class Tim:

    def __init__(self, config, debug, mirror=False):
        self.window = []

        # Network config
        self.ip = config['ip']
        self.port = int(config['port'])

        # Pos config
        self.default_pos = Point(int(config['pos_x']),int(config['pos_y']))
        self.default_angle = int(config['angle'])

        # Computation config
        self.refresh = float(config['refresh'])
        self.window_size = float(config['window'])
        self.min_size = int(config['min_size'])
        self.max_distance = int(config['max_distance'])
        self.window_size = int(config['window'])

        self.socket = socket(AF_INET, SOCK_STREAM)
        self.connected = False
        self.debug = debug
        self.lock = Lock()

        self.pos = None
        self.angle = None
        self.change_pos(mirror)

        print('TIM created')

    def try_connection(self):
        try:
            print('[TIM] Connecting to the TIM')
            self.socket.connect((self.ip, self.port))
            self.connected = True
            looper = Thread(target = self.loop_scan)
            looper.setDaemon(True)
            looper.start()
            print('[TIM] Connected to the TIM')
        except Exception as e:
            print('[TIM] Failed to connect to the TIM: ' + str(e))
            self.connected = False

    def change_pos(self, mirror=False):
        self.pos = Point(self.default_pos.x, 3000 - self.default_pos.y if mirror else self.default_pos.y)
        self.angle = self.default_angle * -1 if mirror else self.default_angle
        if not self.connected:
            self.try_connection()

    def convert_to_card(self, cyl_data, size_a):
        clean_data = []
        length = len(cyl_data)
        for i in range(0, length):
            angle = radians(length - i * size_a + self.angle)
            y = cyl_data[i] * cos(angle) + self.pos.y
            x = cyl_data[i] * sin(angle) + self.pos.x
            clean_data.append(Point(x, y))
        return clean_data

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
            if len(shape) == 0:
                shape.append(p)
                continue
            if p.dist(shape[-1]) < self.max_distance:
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
            radius = -40 if self.pos.x > moy.x else 40
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
            print('[TIM] Pos or angle not configured')
            return None

        #print('[TIM] Scanning')

        #("Send a scan request to the TIM")
        try:
            self.socket.sendall("\x02sRN LMDscandata\x03\0".encode())
        except Exception as e:
            print('[TIM] Failed to send scan request: %s' % str(e))
            self.connected = False
            return None
        data = ""

        while True:
            try:
                part = self.socket.recv(1024)
            except Exception as e:
                print('[TIM] Failed to recieve scan data: %s' % str(e))
                self.connected =  False
                return None
            data += part.decode()
            if "\x03" in part.decode():
                break
        length = len(data)
        if (data[0] != '\x02' or data[length - 1] != '\x03'):
            print("[TIM] Bad response for the TIM")
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
          if new_data is None:
              print('[TIM] Failed to get scan')
              continue
          self.lock.acquire()
          if len(self.window) == self.window_size:
              self.window.pop(0)
          self.window.append(self.scan())
          self.lock.release()

    # TODO: Make an algorithm to merge all scan in the window
    def merge_window(self):
        clean = []
        robots = [scan[2] for scan in self.window]
        return robots

    def get_scan(self):
        if self.window == []:
          return []
        self.lock.acquire()
        scan = self.window[-1]
        raw_data, shapes, robots = scan[0], scan[1], scan[2]
        self.lock.release()

        if self.debug:
            return raw_data, shapes, robots
        return robots
