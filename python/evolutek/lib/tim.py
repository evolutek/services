from PIL import Image, ImageDraw
from math import sqrt, cos, sin, radians
from socket import socket, AF_INET, SOCK_STREAM
from time import sleep
from threading import Thread

def parse_num(s):
    if '+' in s or '-' in s:
        return int(s)
    else:
        return int(s, 16)

def average(a, b):
    """ return the average between two points """
    return Point((a.x + b.x) // 2, (a.y + b.y) // 2)

class Point:

  def __init__(self, x_, y_):
    self.x = x_
    self.y = y_

  def __str__(self):
    return str(x) + ', ' + str(y)

  def distance(self, point):
    return sqrt((point.x - self.x) ** 2 + (point.y - self.y) ** 2)

# TIM Class
# config: {pos_x : int, pos_y : int, angle : float, min_size : float, max_distance : float, ip : str, port : int}
# pos is the position of the TIM: Point(x, y)
# angle is the angle of the TIM: float
# min_size is the min size of a shape : float
# max_distance is the max distance between two points for a robot : float

class Tim:

    def __init__(self, config):
        self.pos = Point(config['pos_x'], config['pos_y'])
        self.angle = config['angle']
        self.min_size = config['min_size']
        self.max_distance = config['max_distance']
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.connected = False
        try:
          print('Connecting to the TIM')
          self.socket.connect((config['ip'], config['port']))
          self.connected = True
        except:
          print('Failed to connect to the TIM')
        print('Connected to the TIM')

    def convert_to_card(self, cyl_data, size_a):
        clean_data = []
        length = len(cyl_data)
        for i in range(0, length):
            angle = radians(length - i * size_a + self.angle)
            y = cyl_data[i] * cos(angle) + self.pos.y
            x = cyl_data[i] * sin(angle) + self.pos.x
            if y >= 0 and y <= 3000 and x >= 0 and x <= 2000:       # check if it is in the table
                clean_data.append(Point(x, y))
        return clean_data

    def detect_robots(self, data):
        result = []
        if len(data) <= 2:
            return result

        cur = None
        prev = data[0]
        shape = []
        building_shape = False

        print(result)

        for i in range(1, len(data)):
            cur = data[i]
            prev_distance =  cur.distance(prev)
            if prev_distance < self.max_distance:
            #if two points are close enougth, we select them
                shape.append(cur)
                building_shape = True
            else:
                if building_shape and len(shape) >= self.min_size:
                    # we do the average between the first point selected and the last
                    result.append(average(shape[0], shape[-1]))
                shape = []
                building_shape = False
            prev = cur

        if building_shape and len(shape) >= self.min_size:
            result.append(average(shape[0], shape[-1]))
        return result

    def get_scan(self):
        print("Send a scan request to the TIM")
        self.socket.sendall("\x02sRN LMDscandata\x03\0".encode())
        data = ""
        while 1:
            part = self.socket.recv(1024)
            data += part.decode()
            if "\x03" in part.decode():
                break
        length = len(data)
        #print("Receive a response of: " + str(length) + " characters")
        if (data[0] != '\x02' or data[length - 1] != '\x03'):
            print("Bad response for the TIM")
            return None
        data = data[1:len(data) - 2].split(' ')
        angular_step = parse_num(data[24])/10000                       # step size
        length = parse_num(data[25])                             # number of values
        print("Converting to cardinal coordiantes")
        data = self.convert_to_card(list(map(parse_num, data[26:26 + length])), angular_step)
        print("Detecting robots")
        data = self.detect_robots(data)
        print("End processing data")
        
        #self.export_png(data)

        return data

    def export_png(self, data):
        arc_ray = 5
        size = 0.1
        size_y = 1500
        size_x = 1000
        im = Image.new("RGB", (size_y, size_x), (255,255,255))
        draw = ImageDraw.Draw(im)
        for i in range(len(data)):
            draw.arc([data[i].y * size - arc_ray + size_y / 2,
                      data[i].x * size - arc_ray + size_x / 2,
                      data[i].y * size + arc_ray + size_y / 2,
                      data[i].x * size + arc_ray + size_x / 2],
                      0, 360, (0, 0, 0))
        draw.arc([self.pos.y * size - arc_ray + size_y / 2,
                  self.pos.x * size - arc_ray + size_x / 2,
                  self.pos.y * size + arc_ray + size_y / 2,
                  self.pos.x * size + arc_ray + size_x / 2],
                  0, 360, (0,255,0))

        draw.arc([-arc_ray + size_y / 2,
                  -arc_ray + size_x / 2,
                  arc_ray + size_y / 2,
                  arc_ray + size_x / 2],
                  0, 360, (255, 0,0))

        draw.arc([0 * size - arc_ray + size_y / 2,
                  2000 * size - arc_ray + size_x / 2,
                  0 * size + arc_ray + size_y / 2,
                  2000 * size + arc_ray + size_x / 2],
                  0, 360, (255,0,0))
        draw.arc([3000 * size - arc_ray + size_y / 2,
                  0 * size - arc_ray + size_x / 2,
                  3000 * size + arc_ray + size_y / 2,
                  0 * size + arc_ray + size_x / 2],
                  0, 360, (255,0,0))
        draw.arc([3000 * size - arc_ray + size_y / 2,
                  2000 * size - arc_ray + size_x / 2,
                  3000 * size + arc_ray + size_y / 2,
                  2000 * size + arc_ray + size_x / 2],
                  0, 360, (255,0,0))
        del draw
        im.save("scan.png", "PNG")
