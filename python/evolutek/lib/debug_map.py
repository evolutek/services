#!/usr/bin/env python3

from tkinter import *
from PIL import Image
from PIL import ImageTk
from math import cos, sin, pi, atan
from os import _exit

colors = ["yellow", "orange", "red", "purple", "blue", "cyan", "green"]
unit = 1/2
refresh = 500

class Interface:

    def __init__(self, map, service):

        print('Init interface')

        self.window = Tk()
        self.map = map
        self.service = service
        self.width = map.real_width * unit
        self.height = map.real_height * unit
        self.close_button = Button(self.window, text='Close', command=self.close)
        self.close_button.pack()
        self.canvas = Canvas(self.window, width=self.width, height=self.height)

        img = Image.open('/etc/conf.d/map.png')
        img = img.resize((int(3000 * unit), int(2000 * unit)), Image.ANTIALIAS)
        self.image =  ImageTk.PhotoImage(img)

        self.canvas.create_image(int(3000 * unit / 2), int(2000 * unit / 2), image=self.image)

        self.canvas.pack()
        print('Window created')
        self.window.after(refresh, self.update)
        self.window.mainloop()

    def close(self):
        self.window.destroy()
        _exit(0)

    def print_grid(self):
        for x in range(self.map.width):
            x_inf = (x * self.map.unit - self.map.unit/2) * unit
            x_sup = (x * self.map.unit + self.map.unit/2) * unit
            self.canvas.create_line(x_inf, 0, x_inf, self.height, fill='black')
            self.canvas.create_line(x_sup, 0, x_sup, self.height, fill='black')
        for y in range(self.map.height):
            y_inf = (y * self.map.unit - self.map.unit/2) * unit
            y_sup = (y * self.map.unit + self.map.unit/2) * unit
            self.canvas.create_line(0, y_inf, self.width, y_inf, fill='black')
            self.canvas.create_line(0, y_sup, self.width, y_sup, fill='black')

    def print_obstacles(self):
        for y in range(self.map.width + 1):
            for x in range(self.map.height + 1):
                if self.map.map[x][y] > 0:
                    x1 = (y * self.map.unit - self.map.unit/2) * unit
                    x2 = (y * self.map.unit + self.map.unit/2) * unit
                    y1 = (x * self.map.unit - self.map.unit/2) * unit
                    y2 = (x * self.map.unit + self.map.unit/2) * unit
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill='black')

    def print_raw_data(self, raw_data):
      print("data points: %d" % len(raw_data))
      for p in raw_data:
        print("%d, %d" % (p.x * unit, p.y * unit))
        self.canvas.create_rectangle(p.y * unit, p.x * unit, p.y * unit + 5, p.x * unit + 5, fill='white')

    def print_shapes(self, shapes):
      print("nb shapes: %d" % len(shapes))
      for i in range(len(shapes)):
          color = colors[i % len(colors)]
          for p in shapes[i]:
            self.canvas.create_rectangle(p.y * unit, p.x * unit, p.y * unit + 5, p.x * unit + 5, fill=color)

    def print_robots(self, robots):
      print("nb robots: %d" % len(robots))
      for i in range(len(robots)):
        color = colors[i % len(colors)]
        p = robots[i]
        if self.service.debug:
            self.canvas.create_rectangle(p.y * unit, p.x * unit, p.y * unit + 10, p.x * unit + 10, fill=color)
        else:
            self.canvas.create_rectangle((p['y'] - self.service.robot_size) * unit,
            (p['x'] - self.service.robot_size) * unit, (p['y'] + self.service.robot_size) * unit,
            (p['x'] + self.service.robot_size) * unit, fill='red')

    def print_pal(self, pal):
        if not pal:
            return

        x = pal['y'] * unit
        y = pal['x'] * unit

        points = []
        points.append((x - self.service.pal_size, y - self.service.pal_size))
        points.append((x + self.service.pal_size, y - self.service.pal_size))
        points.append((x + self.service.pal_size, y + self.service.pal_size))
        points.append((x - self.service.pal_size, y + self.service.pal_size))

        cos_val = cos(pi/2 - pal['theta'])
        sin_val = sin(pi/2 - pal['theta'])

        new_points = []
        for point in points:
            new_points.append((
                (point[0] - x) * cos_val - (point[1] - y) * sin_val + x,
                (point[0] - x) * sin_val + (point[1] - y) * cos_val + y
            ))

        self.canvas.create_polygon(new_points, fill='orange')

    def print_path(self, path):
        if path is None:
            return
        for i in range(1, len(path)):
            p1 = path[i - 1]
            p2 = path[i]

            self.canvas.create_line(p1['y'] * unit, p1['x'] * unit,
                p2['y'] * unit, p2['x'] * unit, width=5, fill='yellow')

    def update(self):
        self.canvas.delete('all')
        self.canvas.create_image(self.width * unit, self.height * unit, image=self.image)
        self.print_grid()
        self.print_obstacles()
        self.print_pal(self.service.pal_telem)
        if self.service.debug:
            self.print_raw_data(self.service.raw_data)
            self.print_shapes(self.service.shapes)
        self.print_robots(self.service.robots)
        #self.print_path(self.service.path)
        self.window.after(refresh, self.update)
