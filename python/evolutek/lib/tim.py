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

# TIM Class
# config: {pos_x : int, pos_y : int, angle : float, min_size : float, max_distance : float, ip : str, port : int}
# pos is the position of the TIM: Point(x, y)
# angle is the angle of the TIM: float
# min_size is the min size of a shape : float
# max_distance is the max distance between two points for a robot : float

class Tim:

    def __init__(self, config, debug):
        self.window = []
        self.pos = Point(int(config['pos_x']),int(config['pos_y']))
        self.angle = int(config['angle'])
        self.refresh = float(config['refresh'])
        self.window_size = float(config['window'])
        self.min_size = int(config['min_size'])
        self.max_distance = int(config['max_distance'])
        self.window_size = int(config['window'])
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.connected = False
        self.debug = debug
        self.looper = Thread(self.loop_scan)
        self.lock = Lock()
        try:
            print('Connecting to the TIM')
            self.socket.connect((config['ip'], config['port']))
            self.connected = True
        except Exception as e:
            print('Failed to connect to the TIM: ' + str(e))
        print('Connected to the TIM')

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
            if p.y >= 0 and p.x <= 3000 and p.x >= 0 and p.x <= 2000:
                clean_data.append(p)
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
            if self.pos.x != moy.x:
                a = (moy.y - self.pos.y) / (moy.x - self.pos.x)
            b = moy.y - a * moy.x
            radius = -38 if self.pos.x > moy.x else 38
            x = moy.x + (radius / sqrt(1 + a ** 2))
            y = a * x + b
            centers.append(Point(x, y))
        return centers
        

    def scan(self)
        print("Send a scan request to the TIM")
        self.socket.sendall("\x02sRN LMDscandata\x03\0".encode())
        data = ""
        while 1:
            part = self.socket.recv(1024)
            data += part.decode()
            if "\x03" in part.decode():
                break
        length = len(data)
        if (data[0] != '\x02' or data[length - 1] != '\x03'):
            print("Bad response for the TIM")
            return None
        data = data[1:len(data) - 2].split(' ')
        angular_step = parse_num(data[24])/10000
        length = parse_num(data[25])
        raw_points = self.convert_to_card(list(map(parse_num, data[26:26 + length])), angular_step)
        print("End scanning")
        return raw_data

    def loop_scan(self)
        while(1)
          self.sleep(self.refresh_time)
          new_data = self.scan()
          self.lock.acquire()
          if len(self.window) == self.window_size:
              self.window.pop()
          self.window.append(self.scan())
          self.lock.release()


      
    def get_scan(self):
        if self.window == []:
          return None
        self.lock.acquire()
        for a in range(len(self.window[0]))
        raw_data = [point for scan in self.window for point in scan]
        self.lock.release()
        raw_data = self.scan()
        shapes = self.split_raw_data(raw_data)
        robots = self.compute_center(shapes)

        if self.debug:
            return raw_data, shapes, robots
        return robots
