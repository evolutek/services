#!/usr/bin/env python3

from collections import deque
from itertools import zip_longest
import math
import random
import threading

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

        self.pal = {'x': 1000, 'y': 1000, 'theta': 0}
        self.pmi = {'x': 0, 'y': 0, 'theta': 0}
        self.pal_traj = []

        self.hokuyo_robots = {}
        self.hokuyo_robots_persist_lock = threading.Lock()
        self.hokuyo_robots_persist = deque()

    @Service.event('log.monitor.robot_position')
    def update_robot_position(self, robot, x, y, theta):
        print(x, y)
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

    @Service.event('hokuyo.robots')
    def update_hokuyo(self, robots):
        self.hokuyo_robots = robots
        with self.hokuyo_robots_persist_lock:
            if len(self.hokuyo_robots_persist) > 25:
                self.hokuyo_robots_persist.popleft()
            self.hokuyo_robots_persist.append(robots)


class EvolutekSimulator(pantograph.PantographHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.monitor = WebMonitor()
        self.monitor_thread = threading.Thread(target=self.monitor.run)
        self.monitor_thread.start()

        self.mouse_pos = {'x': 0, 'y': 0}

        self.cs = CellaservProxy()

    def get_xscale(self):
        return self.width / 3000

    def get_yscale(self):
        return self.height / 2000

    xscale = property(get_xscale)
    yscale = property(get_yscale)

    def setup(self):
        self.cs = CellaservProxy()
        self.robots = {}

    def update(self):
        """Update canvas."""
        self.clear_rect(0, 0, self.width, self.height)

        # Draw table
        self.draw_image('table.png', 0, 0, self.width, self.height)

        self.update_self_tracking()
        #self.update_hokuyo_robots()

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

        # Draw pal circle
        x, y = self.from_evo_to_canvas(
            (self.monitor.pal['x']-75,
             self.monitor.pal['y']-75))
        shape = pantograph.Rect(
            x=x,
            y=y,
            width=150*self.xscale,
            height=150*self.yscale,
            fill_color='rgba(0, 0, 255, 0.5)',
        )
        shape.rotate(float(self.monitor.pal['theta']))
        shape.draw(self)

        # Draw pal orientation
        dir_poly = [(self.monitor.pal['x'] + 75, self.monitor.pal['y']),
            (self.monitor.pal['x'] - 75,self.monitor.pal['y']),
            (self.monitor.pal['x'], self.monitor.pal['y'] + 75)]
        dir_shape = pantograph.Polygon(
                [self.from_evo_to_canvas(p) for p in dir_poly], None, '#000')
        dir_shape.rotate(float(self.monitor.pal['theta']))
        dir_shape.draw(self)

        # Draw pal text
        text = pantograph.Text(
            'pal ({r[x]:.0f},{r[y]:.0f},{r[theta]:.1f})'.format(r=self.monitor.pal),
            self.monitor.pal['y']*self.xscale,
            self.monitor.pal['x']*self.yscale,
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
                    shape = pantograph.Circle(
                        x=int(robot['y']*self.xscale),
                        y=int(robot['x']*self.yscale),
                        radius=int(robot['g']) * 5,
                        fill_color='hsla({}, 60%, 70%, 0.5)'.format(i * 10),
                        line_color='black')
                    shape.draw(self)

                    self.draw_text('({r[x]}, {r[y]})'.format(r=robot),
                                   x=robot['y']*self.yscale,
                                   y=robot['x']*self.xscale)

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
            if robot['name'] not in self.robots:
                # New robot
                shape = pantograph.Circle(
                    x=int(robot['y']*self.xscale),
                    y=int(robot['x']*self.yscale),
                    radius=10,
                    fill_color=random.choice(COLORS))
                self.robots[robot['name']] = shape
            else:
                shape = self.robots[robot['name']]
                # Update position
                shape.x = int(robot['y']*self.xscale)
                shape.y = int(robot['x']*self.yscale)

            shape.draw(self)

    def on_mouse_move(self, event):
        #self.cs('log.monitor.robot_position',
        #        robot='pal',
        #        y=event.x/self.xscale,
        #        x=event.y/self.yscale,
        #        theta=0)
        #self.cs.trajman.gotoxy(
        #    x=int(event.x/self.xscale),
        #    y=int(event.y/self.yscale))
        self.mouse_pos['x'] = event.x
        self.mouse_pos['y'] = event.y

    def on_mouse_down(self, event):
        data = {
            'x': int(self.mouse_pos['y']/self.yscale),
            'y': int(self.mouse_pos['x']/self.xscale),
            }
        print(data)
        self.cs.trajman['pal'].goto_xy(**data)

def main():
    app = pantograph.SimplePantographApplication(EvolutekSimulator)
    app.run(ADDR, PORT)

if __name__ == '__main__':
    main()
