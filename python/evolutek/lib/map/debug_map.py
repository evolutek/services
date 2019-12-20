#!/usr/bin/env python3
from evolutek.lib.map.map import ObstacleType
from evolutek.lib.map.point import Point

from tkinter import *
from PIL import Image
from PIL import ImageTk
from math import cos, sin, pi, atan
from os import _exit
from shapely.geometry import Polygon, LineString

colors = ["yellow", "orange", "red", "purple", "blue", "cyan", "green"]
unit = 1/2
refresh = 50

class Interface:

    def __init__(self, map, service):

        print('[DEBUG_MAP] Init interface')

        self.window = Tk()
        self.map = map
        self.service = service
        self.width = map.width * unit
        self.height = map.height * unit
        self.close_button = Button(self.window, text='Close', command=self.close)
        self.close_button.pack()
        self.canvas = Canvas(self.window, width=self.width, height=self.height)

        img = Image.open('/etc/conf.d/map.png')
        img = img.resize((int(map.width * unit), int(map.height * unit)), Image.ANTIALIAS)
        self.image =  ImageTk.PhotoImage(img)

        self.canvas.create_image(int(map.width * unit / 2), int(map.height * unit / 2), image=self.image)

        self.canvas.pack()
        print('[DEBUG_MAP] Window created')
        self.window.after(refresh, self.update)
        self.window.mainloop()

    def close(self):
        self.window.destroy()
        _exit(0)

    def print_polygon(self, points, color):

        for i in range(1, len(points)):
            p1 = Point(tuple=points[i - 1])
            p2 = Point(tuple=points[i])

            self.canvas.create_line(p1.y * unit, p1.x * unit,
                p2.y * unit, p2.x * unit, width=5, fill=color)

        for p in points:
            point = Point(tuple=p)
            x1 = (point.y - 10) * unit
            x2 = (point.y + 10) * unit
            y1 = (point.x - 10) * unit
            y2 = (point.x + 10) * unit
            self.canvas.create_rectangle(x1, y1, x2, y2, fill='violet')

    def print_map(self):
        self.print_polygon(self.map.borders.exterior.coords)
        for interior in self.map.borders.interiors:
            self.print_polygon(interior.coords)
        for poly in self.map.color_obstacles:
            print(self.map.color_obstacles[poly])
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

        for i in range(1, len(path)):
            p1 = path[i - 1]
            p2 = path[i]

            self.canvas.create_line(p1.y * unit, p1.x * unit,
                p2.y * unit, p2.x * unit, width=5, fill='yellow')

        for p in path:
            x1 = (p.y - 10) * unit
            x2 = (p.y + 10) * unit
            y1 = (p.x - 10) * unit
            y2 = (p.x + 10) * unit
            self.canvas.create_rectangle(x1, y1, x2, y2, fill='violet')

    def print_graph(self, graph):

        for point in graph:

            for p in graph[point]:

                self.canvas.create_line(point.y * unit, point.x * unit,
                    p.y * unit, p.x * unit, width=5, fill='yellow')

        for p in graph:
            x1 = (p.y - 10) * unit
            x2 = (p.y + 10) * unit
            y1 = (p.x - 10) * unit
            y2 = (p.x + 10) * unit
            self.canvas.create_rectangle(x1, y1, x2, y2, fill='violet')

    def update(self):
        #print('[DEBUG_MAP] Update interface')
        self.canvas.delete('all')
        self.canvas.create_image(self.width * unit, self.height * unit, image=self.image)
        #self.print_map()
        self.print_merged_map()
        """if hasattr(self.service, 'pal_telem') and hasattr(self.service, 'pal_size_y'):
            self.print_robot(self.service.pal_telem, self.service.pal_size_y)
        if hasattr(self.service, 'pmi_telem') and hasattr(self.service, 'pmi_size_y'):
            self.print_robot(self.service.pmi_telem, self.service.pmi_size)"""
        if hasattr(self.service, 'path'):
            self.print_path(self.service.path)
        self.window.after(refresh, self.update)
