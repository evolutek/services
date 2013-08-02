#!/usr/bin/python3
from math import sqrt
import copy
import time
import threading
import random

from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service

class Tracked:
    """Classe d'un objet tracké par l'algorithme."""

    def __init__(self, x, y):
        self.name = "PILPPE Robot "
        self.name += str(random.randint(0, 999))
        self.idle_time = 0
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.ax = 0
        self.ay = 0
        self.alive = 0
        self.ours = False

    def __str__(self):
        ret = ("X: {self.x:<6} Vx: {self.vx}\n"
               "Y: {self.y:<6} Vy: {self.vy}\n"
               "Ax: {self.ax:<5} Ay: {self.ay}").format(self=self)

        return ret

    def update(self, x, y, dt):
        self.alive = self.alive + 1
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
        futurx, futury = self.predict_position(dt)
        futurvx = self.vx + self.ax * dt
        futurvy = self.vy + self.ay * dt
        return [futurx, futury, futurvx, futurvy]

    def idle(self):
        self.idle_time = self.idle_time + 1

    def is_down(self):
        return self.idle_time > 10

    def is_alive(self):
        return self.alive > 10

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
        self.collide_androo = False
        done = False
        while not done:
            try:
                self.cs.hokuyo['beacon2'].set_position(pos=2)
                self.cs.hokuyo['beacon2'].add_deadzone(type='circle', x=1500,  y=2000,
                        radius=500)
                done = True
            except:
                print("Hokuyo timed out")
                time.sleep(1)
                pass
        self.pmi_wall = False


    @Service.action
    def is_safe(self, x, y):
        safe = 500
        safe = safe ** 2
        for r in self.robots:
            rx, ry = r.get_coords()
            if r.name != "androo" and r.name != "pmi":
                if (rx - x) ** 2 + (ry - y) ** 2 < safe:
                    return False
        return True

    def scan(self):
        # TODO: Merge 2 hokuyos
        scan = None
        while not scan:
            try:
                scan = self.cs.hokuyo["beacon2"].robots()
            except Exception as e:
                time.sleep(.01)
                print(e)
        self.track(scan['robots'])

    def loop(self):
        while True:
            # Fixme: use sleep(remaining_time) ?
            timer = .2
            while timer > 0:
                time.sleep(.01)
                timer = timer - .01
            self.scan()
            self.check_collision()

    def collision_androo(self):
        limit = 500 ** 2
        pos = None
        for r in self.robots:
            if r.name == "androo":
                pos = r.get_coords()
        if not pos:
            print("Androo not found")
            return False
        for r in self.robots:
            if r.name != "androo" and r.name != "pmi" and r.is_alive():
                print("Testing androo " + str(pos) + " with " +
                        str(r.get_coords()))
                p = r.get_coords()
                dist = (p[0] - pos[0]) ** 2 + (p[1] - pos[1]) ** 2
                if dist < limit:
                    self.collide_androo = True
                    print("Event set ! ANDROO")
                    return True
            if not r.is_alive():
                print("Robot not alive", r.alive)
        if self.collide_androo:
            self.cs('robot-far')
        self.collide_androo = False
        return False

    def collision_pmi_others(self):
        limit = 500 ** 2
        pos = None
        for r in self.robots:
            if r.name == "pmi":
                pos = r.get_coords()
        if not pos:
            print("PMI not found")
            return False
        for r in self.robots:
            if r.name != "androo" and r.name != "pmi":
                print("Testing pmi" + str(pos) + " with " +
                        str(r.get_coords()))
                p = r.get_coords()
                dist = (p[0] - pos[0]) ** 2 + (p[1] - pos[1]) ** 2
                if dist < limit:
                    print("Event set ! PMI")
                    return True
        return False

    def collision_pmi(self):
        def reset_wall():
            nonlocal self
            time.sleep(6)
            self.pmi_wall = False
        border = 550
        for r in self.robots:
            if r.name == "pmi":
                if r.get_coords()[1] < border:
                    self.cs.buzzer.freq_seconds(freq=1500, seconds=0.2)
                    threading.Thread(target=reset_wall).start()
                    return True
                return False
        return False

    def check_collision(self):
        if self.collision_androo():
            self.cs('robot-near')
        if self.collision_pmi() and not self.pmi_wall:
            self.pmi_wall = True
            self.cs('border')
        #if self.collision_pmi_others():
        #    self.cs('pmi-near')

    @Service.action
    def update(self):
        """Returns the robots on the map."""
        ret = []
        for r in self.robots:
            ret.append(r.get_infos())
        return ret

    @Service.action
    def get_robot_pos(self, name):
        for r in self.robots:
            if r.name == name:
                return r.get_coords()
        return None

    @Service.action
    def init_color(self, color):
        """Tries to rename our robots on the map.
        According to the rule: 1 stands for red, -1 stands for blue"""
        ret = ""
        done = False
        while not done:
            try:
                self.cs.hokuyo['beacon2'].set_position(pos=2 if color == -1 else 5)
                self.cs.hokuyo['beacon2'].add_deadzone(type='circle', x=1500,  y=2000,
                        radius=500)
                done = True
            except:
                print("Hokuyo timed out")
                pass
        if not self.rename_robot_bool("androo", 1500 + 1400 * color, 1000):
            ret = ret + "Robot androo not found"
        if not self.rename_robot_bool("pmi", 1500 + 1400 * color, 800):
            ret = ret + " Robot pmi not found"
        return ret

    def rename_robot_bool(self, name, x, y):
        return self.rename_robot(name, x, y) != "Robot not found"

    @Service.action
    def rename_robot(self, name, x, y):
        mindist = 200
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
        # Tous les robots non en cours de creation
        while len(tmp_robots) > 0 and len (measurements) > 0:
            mindist = 200
            best_mesure = None
            best_robot = None
            for r in tmp_robots:
                if r.name != "androo" and r.name != "pmi":
                    continue
                for m in measurements:
                    fx, fy = r.get_coords()
                    dist = (sqrt((m['x'] - fx) ** 2
                            + (m['y'] - fy) ** 2))
                    if dist <= mindist:
                        mindist = dist
                        best_mesure = m
                        best_robot = r
            if best_mesure and best_robot:
                best_robot.update(best_mesure['x'], best_mesure['y'], self.dt)
                measurements.remove(best_mesure)
                tmp_robots.remove(best_robot)
            else:
                break

        # Boucle des robots deja crees
        while len(tmp_robots) > 0 and len (measurements) > 0:
            mindist = 1000
            best_mesure = None
            best_robot = None
            for r in tmp_robots:
                if not r.is_alive():
                    continue
                for m in measurements:
                    fx, fy = r.get_coords()
                    dist = (sqrt((m['x'] - fx) ** 2
                            + (m['y'] - fy) ** 2))
                    if dist <= mindist:
                        mindist = dist
                        best_mesure = m
                        best_robot = r
            if best_mesure and best_robot:
                best_robot.update(best_mesure['x'], best_mesure['y'], self.dt)
                measurements.remove(best_mesure)
                tmp_robots.remove(best_robot)
            else:
                break

        while len(tmp_robots) > 0 and len (measurements) > 0:
            mindist = 1000
            best_mesure = None
            best_robot = None
            for r in tmp_robots:
                for m in measurements:
                    fx, fy = r.get_coords()
                    dist = (sqrt((m['x'] - fx) ** 2
                            + (m['y'] - fy) ** 2))
                    if dist <= mindist:
                        mindist = dist
                        best_mesure = m
                        best_robot = r
            if best_mesure and best_robot:
                best_robot.update(best_mesure['x'], best_mesure['y'], self.dt)
                measurements.remove(best_mesure)
                tmp_robots.remove(best_robot)
            else:
                break

        # Pour tous les robots qui n'ont pas ete update
        print("Robots left " + str(len(tmp_robots)))
        for r in tmp_robots:
            r.idle()
            print(r.idle_time)
            if r.is_down() and r.name != "androo" and r.name != "pmi":
                self.robots.remove(r)

        # Pour toutes les mesures qui n'ont pas de robot
        for measure in measurements:
            print("Measurements left")
            mindist_ = 101
            for r in self.robots:
                rx, ry = r.get_coords()
                dist_ = (sqrt((measure['x'] - rx) ** 2
                        + (measure['y'] - ry) ** 2))
                if dist_ < mindist_:
                    mindist_ = dist_
            # on cree donc un nouveau robot si la distance minimale a tous
            # les robots est superieur a XXcm
            if mindist_ > 100:
                self.robots.append(Tracked(measure['x'], measure['y']))

def main():
    tracker = Tracker()
    loop = threading.Thread(target=tracker.loop)
    loop.start()
    tracker.run()

if __name__ == '__main__':
    main()
