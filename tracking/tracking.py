#!/usr/bin/python3

from math import sqrt
import copy
import time
import threading

from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service

# TODO: Periodic scan
# TODO: Perimeter checking & configurating
# TODO: Zone marking & detecting


class Tracked:
    """Classe d'un objet tracké par l'algorithme."""

    def __init__(self, x, y):
        self.name = "Unknown Robot"
        self.idle_time = 0
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.ax = 0
        self.ay = 0
        self.ours = False

    def __str__(self):
        ret = ("X: {self.x:<6} Vx: {self.vx}\n"
               "Y: {self.y:<6} Vy: {self.vy}\n"
               "Ax: {self.ax:<5} Ay: {self.ay}").format(self=self)

        return ret

    def update(self, x, y, dt):
        self.idle_time = 0
        self.ax = (x - self.x) - self.vx / dt
        self.ay = (y - self.y) - self.vy / dt
        self.vx = (x - self.x) / dt
        self.vy = (y - self.y) / dt
        self.x = x
        self.y = y

    def predict_position(self, dt):
        futurx = self.x + self.vx * dt + (self.ax * dt * dt) / 2
        futury = self.y + self.vy * dt + (self.ay * dt * dt) / 2
        return [futurx, futury]

    def predict_state(self, dt):
        futurx = self.x + self.vx * dt + (self.ax * dt * dt) / 2
        futury = self.y + self.vy * dt + (self.ay * dt * dt) / 2
        futurvx = self.vx + self.ax * dt
        futurvy = self.vy + self.ay * dt
        return [futurx, futury, futurvx, futurvy]

    def idle(self):
        self.idle_time = self.idle_time + 1

    def is_down(self):
        return self.idle_time > 10

    def get_coords(self):
        return self.x, self.y

    def get_infos(self):
        return (self.name, [self.predict_state(0), self.predict_state(0.1),
                self.predict_state(0.2)])

    def rename(self, name):
        self.name = name


class Tracker(Service):
    """Tracker service."""

    def __init__(self):
        super().__init__()
        self.robots = []
        self.dt = 0.1
        self.cs = CellaservProxy()

    def scan(self):
        # merge les scans des 2 hokuyos
        #scan1 = celletracking.hokuyo["beacon1"].robots()
        #scan2 = celletracking.hokuyo["beacon2"].robots()
        #print("SCAN 1")
        #print(scan1)
        #print("SCAN 2")
        #print(scan2)
        #scan = []
        #for r1 in scan1:
        #    tmp = 0
        #    for r2 in scan2:
        #        if r1 - 5 < r2 and r1 + 5 > r2:
        #            print("merge " + str(r1) + " and " + str(r2))
        #            scan.append((r1 + r2) / 2)
        #            scan2.remove(r2)
        #            tmp = 1
        #            break
        #    if tmp == 0:
        #        scan.append(r1)
        #scan.extend(scan2)
        #print("SCAN")
        #print(scan)
        scan = self.cs.hokuyo.robots()
        self.track(scan['robots'])

    def loop(self):
        while True:
            timer = .1
            while timer > 0:
                time.sleep(.01)
                timer = timer - .01
            self.scan()

    # Returns the robots on the map
    @Service.action
    def update(self):
        ret = []
        self.scan()
        for r in self.robots:
            print("Getting infos")
            print(r.get_infos())
            ret.append(r.get_infos())
        return ret

    @Service.action
    def get_robot_pos(self, name):
        for r in self.robots:
            if r.name == name:
                return r.get_coords()
        return None

    # Tries to rename our robots on the map.
    # According to the rule : 1 stands for red, -1 stands for blue
    @Service.action
    def init_color(self, color):
        ret = ""
        if not self.rename_robot_bool("androo", 1500 + 1400 * color, 1000):
            ret = ret + "Robot androo not found"
        if not self.rename_robot("pmi", 1500 + 1400 * color, 600):
            ret = ret + " Robot pmi not found"
        return ret

    def rename_robot_bool(self, name, x, y):
        return self.rename_robot(name, x, y) != "Robot not found"

    @Service.action
    def rename_robot(self, name, x, y):
        mindist = 100
        currobot = None
        for r in self.robots:
            dist = (sqrt((r.get_coords()[0] - x) ** 2
                    + (r.get_coords()[1] - y) ** 2))
            if dist <= mindist:
                mindist = dist
                currobot = r

        if currobot is not None:
            currobot.rename(name)
            return "Robot successfuly renamed to " + name
        else:
            return "Robot not found"

    def track(self, measurements):
        tmp_robots = copy.copy(self.robots)
        for measure in measurements:
            currobot = -1
            mindist = 100
            for m in range(len(tmp_robots)):
                fx, fy = tmp_robots[m].predict_position(self.dt)
                dist = (sqrt((measure['x'] - fx) ** 2
                        + (measure['y'] - fy) ** 2))
                if dist <= mindist:
                    mindist = dist
                    currobot = m
            if currobot == -1:  # Pas de robot trouvé pour cette position
                # on cree donc un nouveau robot
                self.robots.append(Tracked(measure['x'], measure['y']))
            else:  # on actualise le robot correspondant
                tmp_robots[m].update(measure['x'], measure['y'], self.dt)
                tmp_robots.remove(tmp_robots[m])
        for r in tmp_robots:
            r.idle()
            if r.is_down():
                self.robots.remove(r)


def main():
    tracker = Tracker()
    #loop = threading.Thread(target=tracker.loop)
    #loop.start()
    tracker.run()

if __name__ == '__main__':
    main()
