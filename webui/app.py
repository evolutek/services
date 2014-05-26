#!/usr/bin/env python3

from itertools import zip_longest
import random

import pantograph

from cellaserv.proxy import CellaservProxy

ADDR = '0.0.0.0'
PORT = 4280

COLORS = ['#f00', '#0f0', '#00f', '#ff0', '#0ff', '#f0f']


def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


class EvolutekSimulator(pantograph.PantographHandler):

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
        self.draw_image('table.png', 0, 0, self.width, self.height)

        text = pantograph.Text('hello', 42, 42)
        text.fill_color = 'red'
        text.draw(self)

        return

        for robot in self.cs.hokuyo['1'].robots()['robots']:
            shape = pantograph.Circle(
                x=int(robot['x']*self.xscale),
                y=int(robot['y']*self.yscale),
                radius=int(robot['g']) * 10,
                fill_color=random.choice(COLORS))

            shape.draw(self)

        for x, y in grouper(self.cs.hokuyo['1'].scan()['points'], 2):
            shape = pantograph.Circle(
                x=int(x)*self.xscale,
                y=int(y)*self.yscale,
                radius=2,
                fill_color=random.choice(COLORS))

            shape.draw(self)

        return

        for robot in self.cs.tracking.get_robots():
            if robot['name'] not in self.robots:
                # New robot
                shape = pantograph.Circle(
                    x=int(robot['x']*self.xscale),
                    y=int(robot['y']*self.yscale),
                    radius=10,
                    fill_color=random.choice(COLORS))
                self.robots[robot['name']] = shape
            else:
                shape = self.robots[robot['name']]
                # Update position
                shape.x = int(robot['x']*self.xscale)
                shape.y = int(robot['y']*self.yscale)

            shape.draw(self)

    def on_mouse_move(self, event):
        try:
            self.cs.trajman.gotoxy(
                x=int(event.x/self.xscale),
                y=int(event.y/self.yscale))
        except:
            pass


def main():
    app = pantograph.SimplePantographApplication(EvolutekSimulator)
    app.run(ADDR, PORT)

if __name__ == '__main__':
    main()
