#!/usr/bin/env python3

from tkinter import *
from evolutek.lib.map import wall
from math import cos, sin, pi, atan


radius_pal = 75
radius_mi = 52.5
radius_robot = 75

refresh_interface= 500
unit = 1/2

class Interface:

    def __init__(self, map, service):

        print('Init interface')

        self.window = Tk()
        self.map = map
        self.service = service
        self.width = map.real_width * unit
        self.height = map.real_height * unit
        self.close_button = Button(self.window, text='Close', command=self.window.quit)
        self.close_button.pack()
        self.canvas = Canvas(self.window, width=self.width, height=self.height)
        self.image = PhotoImage(file='/home/kmikaz/Evolutek/services/python/evolutek/lib/map.png')
        self.canvas.create_image(750, 500, image=self.image)

        self.canvas.pack()
        print('Window created')
        self.window.after(refresh_interface, self.update)
        self.window.mainloop()

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
                if self.map.map[x][y] == wall:
                    x1 = (y * self.map.unit - self.map.unit/2) * unit
                    x2 = (y * self.map.unit + self.map.unit/2) * unit
                    y1 = (x * self.map.unit - self.map.unit/2) * unit
                    y2 = (x * self.map.unit + self.map.unit/2) * unit
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill='black')

    def print_pal(self, pal):
        if not pal:
            return

        x = pal['y'] * unit
        y = pal['x'] * unit

        points = []
        points.append((x - radius_pal, y - radius_pal))
        points.append((x + radius_pal, y - radius_pal))
        points.append((x + radius_pal, y + radius_pal))
        points.append((x - radius_pal, y + radius_pal))

        cos_val = cos(pal['theta'])
        sin_val = sin(pal['theta'])

        new_points = []
        for point in points:
            new_points.append((
                (point[0] - x) * cos_val - (point[1] - y) * sin_val + x,
                (point[0] - x) * sin_val + (point[1] - y) * cos_val + y
            ))

        self.canvas.create_polygon(new_points, fill='orange')


    def print_path(self, path):
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
        self.window.after(refresh_interface, self.update)
