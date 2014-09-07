#!/usr/bin/env python3

from collections import deque
from itertools import zip_longest
import math
import random
import threading
import time

import pantograph

from cellaserv.service import Service
from cellaserv.proxy import CellaservProxy

ADDR = '0.0.0.0'
PORT = 4280

COLORS = ['#f00', '#0f0', '#00f', '#ff0', '#0ff', '#f0f']


def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


def distance(a, b):
    return math.sqrt((b['x'] - a['x']) ** 2 + (b['y'] - a['y']) ** 2)


class WebMonitor(Service):

    def __init__(self):
        super().__init__(identification=str(random.random()))
        self.cs = CellaservProxy()

        self.pal = {'x': 1000, 'y': 1000, 'theta': 0}
        self.pal_traj = []
        self.pmi = {'x': 1000, 'y': 1000, 'theta': 0}
        self.pmi_traj = []

        self.pal_sharps = [0 for _ in range(4)]
        self.pal_sharps_dist = [0 for _ in range(4)]

        self.hokuyo_robots = {}
        self.hokuyo_robots_persist_lock = threading.Lock()
        self.hokuyo_robots_persist = deque()

        self.pal_robot_near = []
        self.pal_all_robot_near = []
        self.pal_robot_near_lock = threading.Lock()
        self.pal_all_robot_near_lock = threading.Lock()

        self.targets = []
        self.targets_lock = threading.Lock()

    @Service.event('log.monitor.robot_position')
    def update_robot_position(self, robot, x, y, theta):
        if robot == 'pal':
            self.pal['x'] = x
            self.pal['y'] = y
            self.pal['theta'] = theta

            if not self.pal_traj:
                self.pal_traj = [self.pal.copy()]
            else:
                dist = distance(self.pal, self.pal_traj[-1])
                if dist > 1:
                    self.pal_traj.append(self.pal.copy())
        else:
            self.pmi['x'] = x
            self.pmi['y'] = y
            self.pmi['theta'] = theta

            if not self.pmi_traj:
                self.pmi_traj = [self.pmi.copy()]
            else:
                dist = distance(self.pmi, self.pmi_traj[-1])
                if dist > 1:
                    self.pmi_traj.append(self.pmi.copy())

    @Service.event('hokuyo.robots')
    def update_hokuyo(self, robots):
        self.hokuyo_robots = robots
        with self.hokuyo_robots_persist_lock:
            if len(self.hokuyo_robots_persist) > 5:
                self.hokuyo_robots_persist.popleft()
            self.hokuyo_robots_persist.append(robots)

    @Service.event
    def sharp_avoid(self, n):
        self.pal_sharps[n] = time.time()

    @Service.event
    def robot_near(self, x, y):
        with self.pal_robot_near_lock:
            self.pal_robot_near.append((float(x), float(y)))

    @Service.thread
    def sharp_poll(self):
        # Clean sharps
        while not time.sleep(.30):
            for i in range(4):
                if self.pal_sharps[i] == 0:
                    continue
                if time.time() - self.pal_sharps[i] > 1:
                    self.pal_sharps[i] = 0  # reset sharp, not activated

    @Service.event
    def ia_new_target(self, pos, name):
        with self.targets_lock:
            self.targets.append((pos, name))
        with self.pal_robot_near_lock:
            with self.pal_all_robot_near_lock:
                self.pal_all_robot_near.extend(self.pal_robot_near)
                self.pal_robot_near.clear()


class EvolutekSimulator(pantograph.PantographHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cs = CellaservProxy()

        self.monitor = WebMonitor()
        self.monitor_thread = threading.Thread(target=self.monitor.run)
        self.monitor_thread.start()

        self.mouse_pos = {'x': 0, 'y': 0}

        # robots tracked by tracking
        self.robots = {}

    def get_xscale(self):
        return self.width / 3000

    def get_yscale(self):
        return self.height / 2000

    xscale = property(get_xscale)
    yscale = property(get_yscale)

    def update(self):
        """Update canvas."""
        self.clear_rect(0, 0, self.width, self.height)

        # Draw table
        self.draw_image('table.png', 0, 0, self.width, self.height)

        self.update_self_tracking()
        #self.update_hokuyo_robots()
        #self.update_tracking()
        self.update_robot_near()
        self.update_ia()

        self.update_mouse()

    def from_evo_to_canvas(self, point):
        return (point[1]*self.xscale, point[0]*self.yscale)

    def update_self_tracking(self):

        # Draw pal traj
        if len(self.monitor.pal_traj) > 2:
            X = self.monitor.pal_traj
            for i in range(len(self.monitor.pal_traj)-1):
                self.draw_line(X[i]['y']*self.xscale, X[i]['x']*self.yscale,
                               X[i+1]['y']*self.xscale, X[i+1]['x']*self.yscale,
                               color='blue')

        # Draw pmi traj
        if len(self.monitor.pmi_traj) > 2:
            X = self.monitor.pmi_traj
            for i in range(len(self.monitor.pmi_traj)-1):
                self.draw_line(X[i]['y']*self.xscale, X[i]['x']*self.yscale,
                               X[i+1]['y']*self.xscale, X[i+1]['x']*self.yscale,
                               color='orange')

        pal = self.monitor.pal

        # Draw pal rect
        x, y = self.from_evo_to_canvas(
            (pal['x']-150,
             pal['y']-150))
        shape = pantograph.Rect(
            x=x,
            y=y,
            width=300*self.xscale,
            height=300*self.yscale,
            fill_color='rgba(0, 0, 255, 0.5)',
        )

        # Draw pal sharps
        x, y = self.from_evo_to_canvas(
            (pal['x']+130,
             pal['y']+130))
        sharp0 = pantograph.Circle(
            x=x,
            y=y,
            radius=5,
            fill_color='red' if self.monitor.pal_sharps[0] != 0 else 'black')

        x, y = self.from_evo_to_canvas(
            (pal['x']-130,
             pal['y']+130))
        sharp1 = pantograph.Circle(
            x=x,
            y=y,
            radius=5,
            fill_color='red' if self.monitor.pal_sharps[1] != 0 else 'black')

        x, y = self.from_evo_to_canvas(
            (pal['x']+130,
             pal['y']-130))
        sharp2 = pantograph.Circle(
            x=x,
            y=y,
            radius=5,
            fill_color='red' if self.monitor.pal_sharps[2] != 0 else 'black')

        x, y = self.from_evo_to_canvas(
            (pal['x']-130,
             pal['y']-130))
        sharp3 = pantograph.Circle(
            x=x,
            y=y,
            radius=5,
            fill_color='red' if self.monitor.pal_sharps[3] != 0 else 'black')

        # Draw pal orientation
        dir_poly = [
            (pal['x'] + 150, pal['y']),
            (pal['x'] - 150, pal['y']),
            (pal['x'], pal['y'] + 150)]
        dir_shape = pantograph.Polygon(
            [self.from_evo_to_canvas(p) for p in dir_poly], None, '#000')

        compound = pantograph.CompoundShape(
            [shape, dir_shape, sharp0, sharp1, sharp2, sharp3])
        compound.rotate(math.pi/2 - float(self.monitor.pal['theta']))
        compound.draw(self)

        pmi = self.monitor.pmi
        # Draw pmi rect
        x, y = self.from_evo_to_canvas(
            (pmi['x']-100,
             pmi['y']-75))
        shape = pantograph.Rect(
            x=x,
            y=y,
            width=200*self.xscale,
            height=150*self.yscale,
            fill_color='rgba(0, 0, 255, 0.5)',
        )
        shape.rotate(math.pi/2 - float(self.monitor.pmi['theta']))
        shape.draw(self)

        # Draw pal text
        text = pantograph.Text(
            'pal ({r[x]:.0f},{r[y]:.0f},{r[theta]:.1f})'.format(r=self.monitor.pal),
            self.monitor.pal['y']*self.xscale,
            self.monitor.pal['x']*self.yscale,
            text_align='center')
        text.fill_color = 'black'
        text.draw(self)

        # Draw pmi text
        text = pantograph.Text(
            'pmi ({r[x]:.0f},{r[y]:.0f},{r[theta]:.1f})'.format(r=self.monitor.pmi),
            self.monitor.pmi['y']*self.xscale,
            self.monitor.pmi['x']*self.yscale,
            text_align='center')
        text.fill_color = 'black'
        text.draw(self)

    def update_mouse(self):
        # Draw mouse
        text = pantograph.Text(
            '({},{})'.format(int(self.mouse_pos['y']/self.yscale),
                             int(self.mouse_pos['x']/self.xscale)),
            self.mouse_pos['x'],
            self.mouse_pos['y'])
        text.fill_color = 'blue'
        text.draw(self)

    def update_hokuyo_robots(self):
        with self.monitor.hokuyo_robots_persist_lock:
            for i, robot_trace in enumerate(self.monitor.hokuyo_robots_persist):
                for robot in robot_trace:
                    x, y = self.from_evo_to_canvas((int(robot['x']),
                                                    int(robot['y'])))
                    shape = pantograph.Circle(
                        x=x,
                        y=y,
                        radius=int(robot['g']) * 5,
                        fill_color='hsla({}, 60%, 70%, 0.5)'.format(i * 10),
                        line_color='black')
                    shape.draw(self)

                    self.draw_text('({r[x]}, {r[y]})'.format(r=robot),
                                   x=x,
                                   y=y+20)

    def update_hokuyo_scan(self):
        for x, y in grouper(self.cs.hokuyo['1'].scan()['points'], 2):
            shape = pantograph.Circle(
                x=int(x)*self.xscale,
                y=int(y)*self.yscale,
                radius=2,
                fill_color=random.choice(COLORS))

            shape.draw(self)

    def update_tracking(self):
        for robot in self.cs.tracking.get_robots():
            x, y = self.from_evo_to_canvas(
                (int(robot['x']),
                 int(robot['y'])))

            if robot['name'] not in self.robots:
                # New robot
                shape = pantograph.Circle(
                    x=x,
                    y=y,
                    radius=10,
                    fill_color=random.choice(COLORS))
                self.robots[robot['name']] = shape
            else:
                shape = self.robots[robot['name']]
                # Update position
                shape.x = x
                shape.y = y

            shape.draw(self)
            self.draw_text(robot['name'], x, y)

    def update_robot_near(self):
        with self.monitor.pal_robot_near_lock:
            for i, blob in enumerate(self.monitor.pal_robot_near):
                x, y = self.from_evo_to_canvas(blob)
                shape = pantograph.Circle(
                    x, y, radius=5,
                    fill_color='rgba(123, 0, 0, 0.7)',
                    line_color='red')
                shape.draw(self)

        with self.monitor.pal_all_robot_near_lock:
            for i, blob in enumerate(self.monitor.pal_all_robot_near):
                x, y = self.from_evo_to_canvas(blob)
                shape = pantograph.Circle(
                    x, y, radius=5,
                    fill_color='rgba(123, 0, 0, 0.7)',
                    line_color='blue')
                shape.draw(self)

    def update_ia(self):
        with self.monitor.targets_lock:
            for (x, y), name in self.monitor.targets:
                x, y = self.from_evo_to_canvas((x, y))
                shape = pantograph.Circle(
                    x, y, radius=5,
                    fill_color='green',
                    line_color='black')
                shape.draw(self)
                self.draw_text(name, x=x+7, y=y+7)

    def on_mouse_move(self, event):
        self.mouse_pos['x'] = event.x
        self.mouse_pos['y'] = event.y

    def on_mouse_down(self, event):
        data = {
            'x': int(self.mouse_pos['y']/self.yscale),
            'y': int(self.mouse_pos['x']/self.xscale),
            }
        self.cs.trajman['pal'].goto_xy(**data)

    def on_key_down(self, event):
        print(event)
        if event.key_code == 82:  # reset
            self.monitor.pal_traj.clear()
        elif event.key_code == 49:  # 1
            self.cs('beep_ok')
        elif event.key_code == 50:  # 2
            self.cs('beep_ready')
        elif event.key_code == 51:  # 3
            self.cs('beep_ko')
        elif event.key_code == 52:  # 4
            self.cs('beep_down')
        elif 97 <= event.key_code <= 105:  # keypad
            self.cs.trajman['pal'].free()

def main():
    app = pantograph.SimplePantographApplication(EvolutekSimulator)
    app.run(ADDR, PORT)

if __name__ == '__main__':
    main()
