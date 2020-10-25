from cellaserv.service import AsynClient
from cellaserv.settings import get_socket

from evolutek.lib.map.point import Point
from evolutek.lib.map.tim import DebugMode, Tim as _Tim
from evolutek.simulation.simulator import read_config
from evolutek.lib.watchdog import Watchdog

import asyncore
from math import cos, sin, radians
from shapely.geometry import LineString
from threading import Thread

class Tim(_Tim):

    def __init__(self, config, computation_config, mirror=False):


        print('[INIT] Initializing Fake Tim')
        super().__init__(config, computation_config, mirror)

        # In config ?
        self.radius_beacon = 40
        self.angular_step = 0.33
        self.len_ray = 5000
        self.timeout_robot = 1.0
        self.view_angle = 180
        self._robots = {}

        self.client = AsynClient(get_socket())

        self._robots['pal'] = None
        self.client.add_subscribe_cb('pal_telemetry', self.telemetry_handler)
        setattr(self, 'pal_watchdog', Watchdog(self.timeout_robot, self.reset_robot, ['pal']))
        self._robots['pmi'] = None
        self.client.add_subscribe_cb('pmi_telemetry', self.telemetry_handler)
        setattr(self, 'pmi_watchdog', Watchdog(self.timeout_robot, self.reset_robot, ['pmi']))


        enemies = read_config('enemies')
        for enemy in enemies['robots']:
            self._robots[enemy] = None
            self.client.add_subscribe_cb(enemy + '_telemetry', self.telemetry_handler)

         # Start the event listening thread
        self.client_thread = Thread(target=asyncore.loop)
        self.client_thread.start()

    def reset_robot(self, robot):
        self._robots[robot] = None

    def telemetry_handler(self, status, robot, telemetry):
        if status != 'failed':
            self._robots[robot] = telemetry
        else:
            self._robots[robot] = None

        if robot in ['pal', 'pmi']:
            getattr(self, '%s_watchdog' % robot).reset()

    # Replace Tim function
    def _try_connection(self):

        self.connected = True

        while True:
            self.loop_scan()

    def send_request(self):
        data = [hex(0)] * 24
        data.append(hex(int(self.angular_step * 10000)))
        data.append(None)

        # Generate circles for beacon on robots
        shapes = []
        for robot in self._robots.values():
            if robot is None:
                continue
            shapes.append(Point(robot['x'], robot['y']).buffer(self.radius_beacon))

        # Generate the scan
        for i in range(int(self.view_angle / self.angular_step)):
            p1 = Point(self.pos.x, self.pos.y)
            p2 = Point(
                self.len_ray * cos(radians(i * self.angular_step + self.angle)) + self.pos.x,
                self.len_ray * sin(radians(i * self.angular_step + self.angle)) + self.pos.y
            )

            line = LineString([p1, p2])

            # Search for the closest intersection with shapes
            intersect = None
            dist = 0
            for shape in shapes:
                new = Point(shape.intersection(line))
                new_dist = new.dist(p1)
                if intersect is None or dist > new_dist:
                    intersect = new
                    dist = new_dist

            data.insert(26, hex(self.len_ray if intersect is None else dist))

        data[25] = hex(len(data) - 26)

        return data
