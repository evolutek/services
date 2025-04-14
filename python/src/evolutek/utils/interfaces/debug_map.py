#!/usr/bin/env python3
from evolutek.lib.map.map import ObstacleType
from evolutek.lib.map.point import Point

from tkinter import *
from PIL import Image
from PIL import ImageTk
from math import ceil
from os import _exit
from shapely.geometry import Polygon, LineString

colors = ["yellow", "orange", "red", "purple", "blue", "cyan", "green"]

#TODO: add robot angle
class Interface:

    def __init__(self, robot):

        print('[DEBUG_MAP] Init interface')

        self.window = Tk()
        self.unit = self.window
        self.window.attributes('-fullscreen', True)
        self.window.bind('<Escape>', lambda e: self.close())
        self.window.title('Map interface')

        self.robot = robot
        self.map = self.robot.map

        unit_width = self.window.winfo_screenwidth() / self.map.width
        unit_height = (self.window.winfo_screenheight() - 50) / self.map.height
        self.unit = min(unit_width, unit_height)

        self.width = self.map.width * self.unit
        self.height = self.map.height * self.unit

        self.close_button = Button(self.window, text='Close', command=self.close)
        self.close_button.grid(row=1, column=1)

        self.canvas = Canvas(self.window, width=self.width, height=self.height)

        img = Image.open('/etc/conf.d/map.png')
        img = img.resize((int(self.width), int(self.height)), Image.ANTIALIAS)
        self.image = ImageTk.PhotoImage(img)

        self.canvas.create_image(int(self.width / 2), int(self.height / 2), image=self.image)
        self.canvas.grid(row=3, column=0)

        print('[DEBUG_MAP] Window created')
        self.window.after(100, self.update)
        self.window.mainloop()

    def close(self):
        self.window.destroy()
        _exit(0)

    def print_robots(self, robots, color):
        for i in range(len(robots)):
            if not isinstance(robots[i], Point):
                p = Point(dict=robots[i])
            else:
                p = robots[i]
            self.canvas.create_rectangle(p.y * self.unit, p.x * self.unit, p.y * self.unit + 10, p.x * self.unit + 10, fill=color)

    def print_polygon(self, points, color):

        for i in range(1, len(points)):
            p1 = Point(tuple=points[i - 1])
            p2 = Point(tuple=points[i])

            self.canvas.create_line(p1.y * self.unit, p1.x * self.unit,
                p2.y * self.unit, p2.x * self.unit, width=5, fill=color)

        for p in points:
            point = Point(tuple=p)
            x1 = (point.y - 10) * self.unit
            x2 = (point.y + 10) * self.unit
            y1 = (point.x - 10) * self.unit
            y2 = (point.x + 10) * self.unit
            self.canvas.create_rectangle(x1, y1, x2, y2, fill='violet')

    def print_map(self):
        self.print_polygon(self.map.borders.exterior.coords)
        for interior in self.map.borders.interiors:
            self.print_polygon(interior.coords)
        for poly in self.map.color_obstacles:
            self.print_polygon(self.map.color_obstacles[poly].exterior.coords, ObstacleType.color)
        for poly in self.map.robots:
            self.print_polygon(self.map.robots[poly].exterior.coords, ObstacleType.robot)

    def print_merged_map(self):

        #merged_map = self.map.merge_map()
        merged_map = self.map.merged_map
        if isinstance(merged_map, Polygon):
            merged_map = [merged_map]

        #self.print_polygon(self.map.borders.exterior.coords, 'black')

        for poly in merged_map:
            self.print_polygon(poly.exterior.coords, 'grey')
            for interior in poly.interiors:
                self.print_polygon(interior.coords, 'red')

    def print_path(self, path):

        if len(path) < 2:
            return

        for i in range(1, len(path)):
            p1 = path[i - 1]
            p2 = path[i]

            self.canvas.create_line(p1.y * self.unit, p1.x * self.unit,
                p2.y * self.unit, p2.x * self.unit, width=5, fill='yellow')

        for p in path:
            x1 = (p.y - 10) * self.unit
            x2 = (p.y + 10) * self.unit
            y1 = (p.x - 10) * self.unit
            y2 = (p.x + 10) * self.unit
            self.canvas.create_rectangle(x1, y1, x2, y2, fill='violet')

    def print_robots(self, robots):

        unit = self.unit
        for i in range(len(robots)):
            color = colors[i % len(colors)]
            p = robots[i]
            self.canvas.create_rectangle((p['y'] - self.robot.robot_size) * unit,
            (p['x'] - self.robot.robot_size) * unit, (p['y'] + self.robot.robot_size) * unit,
            (p['x'] + self.robot.robot_size) * unit, fill='red')

    def update(self):

        self.canvas.delete('all')
        self.canvas.create_image(int(self.width / 2), int(self.height / 2), image=self.image)

        self.print_merged_map()
        if self.robot.robots:
            with self.robot.lock:
                r = self.robot.robots[:]
            self.print_robots(r)
        if self.robot.path:
            with self.robot.lock:
                p = self.robot.path[:]
            self.print_path(p)

        self.window.after(100, self.update)
