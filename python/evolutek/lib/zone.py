from evolutek.lib.point import Point

import json
from math import pi

class Zone:

    def __init__(self, points, thetas):
        self.p1 = Point(points[0]['x'], points[0]['y'])
        self.p2 = Point(points[1]['x'], points[1]['y'])

        self.theta1 = thetas[0]
        if isinstance(self.theta1, str):
            self.theta1 = eval(self.theta1)
        self.theta2 = thetas[1]
        if isinstance(self.theta2, str):
            self.theta2 = eval(self.theta2)

    def __str__(self):
        s = "Zone:\n->Points:\n"
        s += str(self.p1) + "\n"
        s += str(self.p2) + "\n"
        s += "->Thetas:\n"
        s += str(self.theta1) + "\n"
        s += str(self.theta2) + "\n"
        return s

    def is_inside(self, p):
        if isinstance(p, dict):
            p = Point(p['x'], p['y'])
        return p.x >= self.p1.x and p.x <= self.p2.x and p.y >= self.p1.y and p.y <= self.p2.y

    def is_looking_at(self, theta):
        if theta < 0:
            theta += 2*pi
        return theta >= self.theta1 and theta <= self.theta2

    @staticmethod
    def parse(file):
        with open(file, 'r') as zone_file:
            data = zone_file.read()

        data = json.loads(data)

        parsed = []
        zones = data['zones']
        for zone in zones:
            z = Zone(zone['points'], zone['thetas'])
            parsed.append(z)

        return parsed

if __name__ == "__main__":
    zones = Zone.parse('/etc/conf.d/zones.json')
    for zone in zones:
        print(zone)
