from math import cos, sin, sqrt, pi, radians
from rplidar import RPLidar, RPLidarException
from time import sleep, time
from threading import Event, Thread, Lock

from evolutek.lib.map.point import Point
import evolutek.lib.map.utils as utils

LIDAR_PATH="/dev/RPLIDAR"

class Rplidar:

    def __init__(self, config):
        self.shape_max_distance = float(config['max_distance'])
        self.shape_min_size = float(config['min_size'])
        self.mean_beacon_radius = float(config['radius'])

        self.lock = Lock()
        self.need_to_stop = Event()
        self.cloud = []
        self.shapes = []
        self.robots = []
        self.callback = None

        self.position = Point(0, 0)
        self.angle = -pi/2

        try:
            self.lidar = RPLidar(LIDAR_PATH)
        except Exception as e:
            print('[RPLIDAR] Fail to init lidar: %s' % str(e))

        try:
            print(self)
        except RPLidarException:
            self.lidar.stop_motor()
            self.lidar.stop()
            self.lidar.disconnect()
            self.lidar = RPLidar(LIDAR_PATH)
            print(self)

    def __str__(self):
        s = '----------\n'
        s += str(self.lidar.get_info()) + '\n'
        s += str(self.lidar.get_health()) + '\n'
        s += '---------'
        return s

    def register_callback(self, callback):
        with self.lock:
            self.callback = callback

    def set_position(self, position, angle):
        with self.lock:
            self.position = position
            self.angle = angle - pi/2

    def convert_scan_to_cloud(self, scan):
        cloud = []
        lidar_angle = None

        #with self.lock:
        #    lidar_angle = self.angle

        for quality, angle, distance in scan:

            # TODO : put 1500 in a config variable
            if distance > 1500: continue

            current_angle = radians(angle) + pi/2# - lidar_angle
            x = distance * sin(current_angle)# + self.position.y
            #if x < 0 or x > 2000: continue
            y = distance * cos(current_angle)# + self.position.y
            #if y < 0 or y > 3000: continue
            cloud.append(Point(x, y))
        return cloud

    def split_shapes(self, cloud):
        shapes = []
        shape = []
        for point in cloud:
            if len(shape) == 0 or point.dist(shape[-1]) < self.shape_max_distance:
                shape.append(point)
            else:
                if len(shape) >= self.shape_min_size:
                    shapes.append(shape)
                shape = [point]
        if len(shape) >= self.shape_min_size:
            shapes.append(shape)
        return shapes

    def compute_center(self, shape):
        mean_point = Point.mean(shape)

        lidar_position = None
        with self.lock:
            lidar_position = self.position

        return lidar_position.compute_offset_point(mean_point, self.mean_beacon_radius)

    def start_scanning(self):
        Thread(target=self.loop_scan).start()

    def stop_scanning(self):
        self.need_to_stop.set()

    def loop_scan(self):
        print('[RPLIDAR] Start scanning')
        #last = time()
        for scan in self.lidar.iter_scans():
            #print(f"[RPLIDAR] New scan: {(time()-last)*1000}ms from last")
            #last = time()
            #t = last
            #process = last
            clean_cloud = self.convert_scan_to_cloud(scan)
            #print(f"[RPLIDAR] Clean cloud: {(time() - t) * 1000}ms")
            #t = time()
            shapes = self.split_shapes(clean_cloud)
            #print(f"[RPLIDAR] Split shapes: {(time() - t) * 1000}ms")
            #t = time()

            robots = []
            for shape in shapes:
                robots.append(self.compute_center(shape))

            #print(f"[RPLIDAR] Compute centers: {(time() - t) * 1000}ms")
            #print(f"[RPLIDAR] Total processing time: {(time() - process)*1000}ms")

            with self.lock:

                self.cloud = clean_cloud
                self.shapes = shapes
                self.robots = robots

                if self.callback is not None:
                    self.callback(self.cloud, self.shapes, self.robots)

            if self.need_to_stop.is_set():
                print('[RPLIDAR] Stop scanning')
                self.need_to_stop.clear()
                return

    def get_cloud(self):
        with self.lock:
            return self.cloud

    def get_shape(self):
        with self.lock:
            return self.shapes

    def get_robots(self):
        with self.lock:
            return self.robots

    def __del__(self):
        if not hasattr(self, "lidar"):
            return # Avoids getting confusing errors when the lidar is not connected to the right USB port
        print("[RPLIDAR] Stopped Lidar")
        self.lidar.stop()
        self.lidar.stop_motor()
        self.lidar.disconnect()
